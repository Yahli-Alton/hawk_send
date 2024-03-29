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
import threading
from time import sleep
from kivy.clock import Clock
import time

session = requests.Session()
URL = "http://NickJohnson.pythonanywhere.com/"


class ActionsLayout(GridLayout):
    """
    Contains:
        - Send messages:
            - message textinput
            - send button
        - Create channel:
            - channel_name textinput
            - create_channel button
    """
    def __init__(self, application_object, channel_layout, **kwargs):
        """
        :param application_object: Kivy application object
        :param channel_layout: Kivy layout, in order to refresh
        """
        super(ActionsLayout, self).__init__(**kwargs)
        self.application_object = application_object
        self.channel_layout = channel_layout
        self.objects_list = []

        self.render()

    def add_widget(self, widget):  # noqa
        """
        This function adds widget self.objects_list and then regular kivy.add_widget
        :param widget: Kivy widget
        """
        self.objects_list.append(widget)
        GridLayout.add_widget(self, widget)

    def render(self):
        """
        Renders widgets into self
        """
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
        """
        Deletes all widgets added
        """
        for _object in self.objects_list:
            self.remomve_widget(_object)

    def refresh(self):
        """
        Refreshes the current object to be up-to-date
        """
        self.delete_widgets()
        self.render()

    def send_onpress(self, instance):
        """
        Upload_message into server and refreshes message_layout
        """
        session.post(url=URL + "upload_message",
                     json={
                         "channel_id": self.channel_layout.last_channel_id,
                         "message": self.message.text
                     })
        self.channel_layout.refresh_message()
        self.message.text = ""

    def create_channel_onpress(self, instance):
        """
        Creates channel in server and refreshes channel_layout
        """
        session.post(url=URL + "create_channel",
                     json={"channel_name": self.channel_name_textinput.text,
                           "users": self.channel_name_usernames.text.split(",")})
        self.channel_layout.refresh()


class ChannelsLayout(GridLayout):
    """
    Contains:
        [channel_1, channel_2, ......., channel_n]
    """
    def __init__(self, main_layout, **kwargs):
        """
        Initializes the object and calls render
        :param main_layout: Kivy layout in Kivy App
        """
        GridLayout.__init__(self, **kwargs)
        self.main_layout = main_layout
        self.objects_list = []
        self.buttons = []
        self.last_widget = None
        self.render()

    def render(self):
        """
        Renders channels from server.user_channels into self
        """
        self.cols = 1

        print("sending")
        user_channels_response = session.get(url=URL + "get_user_channel_ids").json()
        user_channel_ids, user_channel_names = user_channels_response["channel_ids"], \
                                               user_channels_response["channel_names"]
        self.size_hint = (0.4, 0.1 * len(user_channel_ids))
        if len(user_channel_ids) > 0:
            self.channel_id = user_channel_ids[0]
            self.last_widget = None

            for name, id in zip(user_channel_names, user_channel_ids):
                button = Button(text=name)

                def func(instance, channel_name=name, channel_id=id):

                    if self.last_widget != None:
                        self.main_layout.remove_widget(self.last_widget)

                    print(channel_id)
                    self.channel_id = channel_id
                    print(self.channel_id)

                    channel_messages = session.get(url=URL + "download_channel",
                                                   params={"channel_id": channel_id}).json()['channel']

                    self.root2 = ScrollView(size_hint=(0.2, None), size=(Window.width, Window.height))

                    self.last_channel_widget = MessagesLayout(channel_messages)
                    self.root2.add_widget(self.last_channel_widget)

                    self.main_layout.add_widget(self.root2)
                    self.last_widget = self.root2

                button.bind(on_press=func)
                self.add_widget(button)

                self.buttons.append(button)

    def add_widget(self, widget):  # noqa
        """
        This function adds widget self.objects_list and then regular kivy.add_widget
        :param widget: Kivy widget
        """
        self.objects_list.append(widget)
        GridLayout.add_widget(self, widget)

    def remove_widgets(self):
        """
        This function removes all buttons from self in order for next refresh
        """
        for button in self.buttons:
            self.remove_widget(button)

    def remove_chat(self):
        """
        This functions removes_chat in order for next refresh
        """
        self.main_layout.remove_widget(self.root2)

    def refresh(self, remove_chat=True):
        """
        This function refreshes Channels: delete and then render
        :param remove_chat: bool
        """
        if remove_chat:
            self.remove_chat()

        self.remove_widgets()
        self.render()

    def refresh_message(self):
        """
        This function refreshes only the message_object by new_information from the server
        """
        if self.last_widget != None:
            self.main_layout.remove_widget(self.last_widget)

        self.root2 = ScrollView(size_hint=(0.2, None), size=(Window.width, Window.height))

        print(f"last channeld id: {self.channel_id}")

        channel_messages = session.get(url=URL + "download_channel",
                                       params={"channel_id": self.last_channel_id}).json()['channel']

        self.root2.add_widget(MessagesLayout(channel_messages))

        self.main_layout.add_widget(self.root2)
        self.last_widget = self.root2

    @property
    def last_channel_id(self):
        return self.channel_id


class MessagesLayout(GridLayout):
    """
    Layout of all of the channel_messages
    """
    def __init__(self, channel_messages: list, **kwargs):
        """
        This function initalizes and renders MessagesLayout
        :param channel_messages: a list of all current channel_messages
        """
        GridLayout.__init__(self, **kwargs)

        self.cols = 1
        self.pos_hint = {"center_x": 0.1, "center_y": 0.5}

        self.size_hint = (1, len(channel_messages) * 0.15)

        for message in channel_messages:
            minute = message['time']['minute']
            hour = message['time']['hour'] + 3
            _time = time.localtime(time.time())

            if message['time']['date'] == f"{_time.tm_mon}.{_time.tm_mday}.{_time.tm_year}":
                label = Label(text=
                              message['username'] + ":" + "\n" +
                              message['text'] + "\n" + f"{hour}:{'0' * (2 - len(str(minute)))}{minute}")
                label.text_size = label.width, None
            else:
                label = Label(text=
                              message['username'] + ":" + "\n" +
                              message['time']['date'])
                label.text_size = label.width, None

            self.add_widget(label)


class LoginLayout(GridLayout):
    """
    Contains:
        - username_textinput
        - password_textinput
        - Login Button
        - Signup Button
    """
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
        """
        Authorises username and password from username_textinput.text, password_textinput.text
        :param instance: Kivy regular on_press param
        """
        session.auth = (self.username_textinput.text, self.password_textinput.text)
        self.continue_app()

    def signup_func(self, instance):
        """
        Creates new user in the channel from username_textinput.text, password_textinput.text
        :param instance: Kivy regular on_press param
        :return:
        """
        requests.post(url=URL + "create_user",
                      json={"username": self.username_textinput.text, "password": self.password_textinput.text})

    def continue_app(self):
        """
        This function removes all of the login widgets and renders the next part -> ChannelsLayout + ActionsLayout
        """
        self.main_layout.remove_widget(self)  # noqa
        root = ScrollView(size_hint=(0.3, None), size=(Window.width, Window.height))
        channel_layout = ChannelsLayout(self.main_layout)
        root.add_widget(channel_layout)
        self.main_layout.add_widget(root)

        self.main_layout.add_widget(ActionsLayout(self.main_layout, channel_layout))

        def refresh_func(instance, channel_layout=channel_layout):
            try:
                last_channel_id = channel_layout.last_channel_id
                channel_layout.refresh()
                channel_layout.channel_id = last_channel_id
                channel_layout.refresh_message()
            except:
                pass

        Clock.schedule_interval(refresh_func, 0.5)
#       In order to have a flowing conversation, a thread is always auto refreshing the messages and channels


class MainLayout(BoxLayout):
    def __init__(self):
        BoxLayout.__init__(self)
        self.objects_list = []

    def add_widget(self, widget):  # noqa
        """
        This function adds widget self.objects_list and then regular kivy.add_widget
        :param widget: Kivy widget
        """
        self.objects_list.append(widget)
        BoxLayout.add_widget(self, widget)

    def delete_widgets(self):
        """
        This function removes all of the objects that were added to this object
        """
        for object in self.objects_list:
            self.remove_widget(object)


class MyApp(App):
    def build(self):
        """
        This function builds the main application
        """
        self.main_layout = MainLayout()
        self.main_layout.add_widget(LoginLayout(self.main_layout))

        return self.main_layout


if __name__ == "__main__":
    kivy_app = MyApp()
    kivy_app.run()
