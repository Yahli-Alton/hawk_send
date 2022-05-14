import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class MyGridLayout(GridLayout):

    def __init__(self, **kwargs):
        super(MyGridLayout, self).__init__(**kwargs)

        #colums

        self.cols = 1

        #widgets

        self.add_widget(Label(text = "enter your message: "))

        self.name = TextInput(multiline = True)
        self.add_widget(self.name)

        self.send = Button(text = "send", font_size = 25)
        self.add_widget(self.send)

class MyApp(App):
    def build(self):
        return MyGridLayout()

if __name__ == "__main__":
    a = MyApp()
    a.run()

