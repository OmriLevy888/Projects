from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # disables kivy touch emulation, without this,
                                                            # right click would be interpreted as touches,
                                                            # meaning they would leave a red dot which is
                                                            # used to test touch and multi touch support
                                                            # for mobile development

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.clock import Clock


from login_screen import LoginScreen
from chat import ChatScreen
from server_crash import ServerCrashScreen
import networking


TPS = 20  # network ticks per second


sm = ScreenManager()


class ChatApp(App):
    def build(self):
        global tick_evnt

        tick_evnt = Clock.schedule_interval(networking.tick, 1.0 / TPS)
        sm.add_widget(LoginScreen(id='login', name='login_screen'))
        sm.add_widget(ChatScreen(id='chat_screen', name='chat_screen'))
        sm.add_widget(ServerCrashScreen(id='server_crash', name='server_crash_screen'))
        return sm


def main():
    chat = ChatApp()  # create the app
    networking.set_sm(sm)  # assign the screen manager
    networking.init_connection()  # initialize connection to server
    Builder.load_file('login.kv')  # load login file
    Builder.load_file('server_crash.kv')  # load server crash file
    chat.run()  # run app


if __name__ == '__main__':
    main()
