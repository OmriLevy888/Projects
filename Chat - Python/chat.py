from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
import datetime
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
            now = datetime.datetime.now()
            current_time = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)
            self.grid.display.text += '[b][' + current_time + '] [color=' + networking.NetworkingData.colour + ']Me:[/b][/color] ' + text + '\n'
        else:
            display_error(status)

    def quit(self):
        Clock.schedule_once(sys.exit, 0.2)

    def set_display(self, display):
        networking.NetworkingData.chat_display = display

    def set_user_display(self, display):
        networking.NetworkingData.user_display = display


def set_focus(dt):
    tb.focus = True


def display_error(msg):
    if msg != FAIL:
        networking.NetworkingData.chat_display.text += msg + '\n'
