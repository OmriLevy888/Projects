from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

import sys

import networking


OK = str(0x100)
FAIL = str(0x101)


tb = None


class ChatScreen(Screen):
    def submit_text(self, text_bar, text):
        global tb
        tb = text_bar
        Clock.schedule_once(set_focus)

        if text == '':
            return

        text_bar.text = ''
        status = networking.process_message(text)

        if status == OK:
            print networking.NetworkingData.colour
            self.grid.display.text += '[color=' + networking.NetworkingData.colour + '][b]Me:[/b][/color] ' + text + '\n'
        else:
            display_error(status)

    def quit(self):
        sys.exit()

    def set_display(self, display):
        networking.NetworkingData.chat_display = display


def add_line(line):
    tb.text += line + '\n'


def set_focus(dt):
    tb.focus = True


def display_error(msg):
    if msg != FAIL:
        networking.NetworkingData.chat_display.text += msg + '\n'
