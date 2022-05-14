import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import requests
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView

session = requests.Session()
session.auth = ('tal-kh', '123')
URL = "http://127.0.0.1:5690/"


class ActionsLayout(GridLayout):

    def __init__(self, **kwargs):
        super(ActionsLayout, self).__init__(**kwargs)

        # columns

        self.cols = 1

        # widgets

        self.size_hint = (0.3, 0.2)
        self.pos_hint = {"center_x": 1, "center_y": 0.5}

        self.add_widget(Label(text="enter your message: "))

        self.message = TextInput(multiline=True)
        self.add_widget(self.message)

        self.send = Button(text="send", font_size=25)
        self.send.bind(on_press=self.press)
        self.add_widget(self.send)

    def press(self, instance):
        print(self.message.text)


class ChannelsLayout(GridLayout):
    def __init__(self, main_layout, **kwargs):
        GridLayout.__init__(self, **kwargs)

        self.cols = 1

        user_channels_response = session.get(url=URL + "get_user_channel_ids").json()
        user_channel_ids, user_channel_names = user_channels_response["channel_ids"], \
                                               user_channels_response["channel_names"]

        self.channel_id = user_channel_ids[0]
        self.last_widget = None

        for name, id in zip(user_channel_names, user_channel_ids):
            button = Button(text=name)

            def func(instance, channel_name=name, channel_id=id):

                if self.last_widget != None:
                    main_layout.remove_widget(self.last_widget)

                self.channel_id = channel_id

                channel_messages = session.get(url=URL + "download_channel",
                                               params={"channel_id": channel_id}).json()['channel']

                root2 = ScrollView(size_hint=(0.2, None), size=(Window.width, Window.height))

                root2.add_widget(MessagesLayout(channel_messages))

                main_layout.add_widget(root2)
                self.last_widget = root2

            button.bind(on_press=func)
            self.add_widget(button)

    @property
    def last_channel_id(self):
        return self.channel_id


class MessagesLayout(GridLayout):
    def __init__(self, channel_messages: list, **kwargs):
        GridLayout.__init__(self, **kwargs)

        self.cols = 1
        self.pos_hint = {"center_x": 0, "center_y": 0.5}

        self.size_hint = (0.5, len(channel_messages) * 0.1)

        for message in channel_messages:
            label = Label(text=message['text'] + "\n" + f"{message['time']['hour']}:{message['time']['minute']}:{message['time']['second']}")
            label.text_size = label.width, None

            self.add_widget(label)


class MyApp(App):
    def build(self):
        main_layout = BoxLayout()
        root = ScrollView(size_hint=(0.3, None), size=(Window.width, Window.height))
        channel_layout = ChannelsLayout(main_layout)
        root.add_widget(channel_layout)
        main_layout.add_widget(root)

        main_layout.add_widget(ActionsLayout())

        return main_layout


if __name__ == "__main__":
    a = MyApp()
    a.run()
