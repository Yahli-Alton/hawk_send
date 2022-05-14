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
URL = "http://NickJohnson.pythonanywhere.com/"


class ActionsLayout(GridLayout):

    def __init__(self, main_layout, channels_layout, root, **kwargs):
        super(ActionsLayout, self).__init__(**kwargs)
        self.channels_layout = channels_layout
        self.main_layout = main_layout
        self.root = root

        self.func()

    def func(self):
        # columns

        self.cols = 1

        # widgets

        self.size_hint = (0.3, 0.5)
        self.pos_hint = {"center_x": 1, "center_y": 0.5}

        self.label1 = Label(text="enter your message: ")
        self.add_widget(self.label1)

        self.message = TextInput(multiline=True)
        self.add_widget(self.message)

        self.send = Button(text="send", font_size=25)
        self.send.bind(on_press=self.send_onpress)
        self.add_widget(self.send)

        self.label2 = Label(text="Name the channel: ")
        self.add_widget(self.label2)

        self.channel_name_textinput = TextInput(multiline=True)
        self.add_widget(self.channel_name_textinput)

        self.label3 = Label(text="Name usernames:")
        self.add_widget(self.label3)

        self.channel_name_usernames = TextInput(multiline=True)
        self.add_widget(self.channel_name_usernames)

        self.create_channel = Button(text="create_channel", font_size=25)
        self.create_channel.bind(on_press=self.create_channel_onpress)
        self.add_widget(self.create_channel)

    def delete_widgets(self):
        self.remove_widget(self.label1)
        self.remove_widget(self.label2)
        self.remove_widget(self.label3)

        self.remove_widget(self.message)
        self.remove_widget(self.send)
        self.remove_widget(self.channel_name_usernames)
        self.remove_widget(self.channel_name_textinput)

        self.remove_widget(self.create_channel)

    def send_onpress(self, instance):
        session.post(url=URL + "upload_message",
                     json={
                         "channel_id": self.channels_layout.last_channel_id,
                         "message": self.message.text
                     })

    def create_channel_onpress(self, instance):
        session.post(url=URL + "create_channel",
                     json={"channel_name": self.channel_name_textinput.text,
                           "users": self.channel_name_usernames.text.split(",")})

        self.main_layout.remove_widget(self.root)
        self.main_layout.remove_widget(self)
        self.main_layout.remove_widget(self.channels_layout.root2)

        root = ScrollView(size_hint=(0.3, None), size=(Window.width, Window.height))
        channel_layout = ChannelsLayout(self.main_layout)
        root.add_widget(channel_layout)
        self.main_layout.add_widget(root)

        self.delete_widgets()
        self.func()
        self.main_layout.add_widget(self)
        self.root = root
        self.channels_layout = channel_layout


class ChannelsLayout(GridLayout):
    def __init__(self, main_layout, **kwargs):
        GridLayout.__init__(self, **kwargs)

        self.cols = 1

        print("sending")
        user_channels_response = session.get(url=URL + "get_user_channel_ids").json()
        user_channel_ids, user_channel_names = user_channels_response["channel_ids"], \
                                               user_channels_response["channel_names"]

        if len(user_channel_ids) > 0:
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

                    self.root2 = ScrollView(size_hint=(0.2, None), size=(Window.width, Window.height))

                    self.root2.add_widget(MessagesLayout(channel_messages))

                    main_layout.add_widget(self.root2)
                    self.last_widget = self.root2

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

        self.size_hint = (0.5, len(channel_messages) * 0.15)

        for message in channel_messages:
            label = Label(text=message['text'] + "\n" + f"{message['time']['hour']}:{message['time']['minute']}:{message['time']['second']}" + "\n" + message["username"])
            label.text_size = label.width, None

            self.add_widget(label)


class LoginLayout(GridLayout):
    def __init__(self, main_layout, **kwargs):
        super(LoginLayout, self).__init__(**kwargs)
        self.main_layout = main_layout

        self.cols = 1

        self.username_label = Label(text="Enter your username:")
        self.add_widget(self.username_label)

        self.username_textinput = TextInput(multiline=True)
        self.add_widget(self.username_textinput)

        self.password_label = Label(text="Enter your password:")
        self.add_widget(self.password_label)
        self.password_textinput = TextInput(multiline=True)
        self.add_widget(self.password_textinput)

        self.login = Button(text="Login",
                            font_size=25)
        self.login.bind(on_press=self.login_func)
        self.add_widget(self.login)

        self.signup = Button(text="Signup",
                            font_size=25)
        self.signup.bind(on_press=self.signup_func)
        self.add_widget(self.signup)

    def login_func(self, instance):
        session.auth = (self.username_textinput.text, self.password_textinput.text)
        self.continue_app()

    def signup_func(self, instance):
        requests.post(url=URL + "create_user",
                      json={"username": self.username_textinput.text, "password": self.password_textinput.text})

    def continue_app(self):
        self.main_layout.remove_widget(self) # noqa
        root = ScrollView(size_hint=(0.3, None), size=(Window.width, Window.height))
        channel_layout = ChannelsLayout(self.main_layout)
        root.add_widget(channel_layout)
        self.main_layout.add_widget(root)

        self.main_layout.add_widget(ActionsLayout(self.main_layout, channel_layout, root))


class MyApp(App):
    def build(self):
        main_layout = BoxLayout()
        main_layout.add_widget(LoginLayout(main_layout))

        return main_layout


if __name__ == "__main__":
    kivy_app = MyApp()
    kivy_app.run()
