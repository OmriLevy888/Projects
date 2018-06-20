from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.clock import Clock


from login_screen import LoginScreen
from chat import ChatScreen
import networking


TPS = 20  # network ticks per second


sm = ScreenManager()


class ChatApp(App):
    def build(self):
        Clock.schedule_interval(networking.tick, 1.0 / TPS)
        sm.add_widget(LoginScreen(id='login', name='login_screen'))
        sm.add_widget(ChatScreen(id='chat_screen', name='chat_screen'))
        return sm


def main():
    chat = ChatApp()
    networking.set_sm(sm)
    networking.init_connection()
    Builder.load_file('login.kv')
    chat.run()


if __name__ == '__main__':
    main()
