from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
import sys


class ServerCrashScreen(Screen):
    def exit(self):
        Clock.schedule_once(sys.exit, 0.2)
