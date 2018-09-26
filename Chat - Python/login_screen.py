from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

import networking


class TermsPopup(Popup):
    pass


class InfoPopup(Popup):
    def __init__(self, title, content, **kwargs):
        super(InfoPopup, self).__init__(**kwargs)
        self.title = title
        self.lbl.text = content


class LoginScreen(Screen):
    def set_info_popup(self):
        networking.NetworkingData.ls = self

    def display_notification(self, title='', content=''):
        info_popup = InfoPopup(title, content)
        info_popup.open()


class Login(GridLayout):
    def login(self, username, password):
        if username == 'username' or password == 'password':
            return

        if not networking.NetworkingData.processing:
            networking.login(username, password)


class Signup(GridLayout):
    def signup(self, username, password, day, month, year, checked):
        if checked:
            if username == 'username' or password == 'password':
                return

            if not self.valid_username(username):

                return

            if not self.valid_date(day, month, year):
                return

            if not networking.NetworkingData.processing:
                networking.signup(username, password, day, month, year)

    def valid_date(self, day, month, year):
        return not (day == 'DD' or month == 'MM' or year == 'YYYY')

    def valid_username(self, username):
        content = None

        if len(username) < 4:
            content = 'Username has to be at least 4 characters long'
        elif username[0] == '@':
            content = 'Username cannot start with @'
        elif len(username) > 16:
            content = 'Username cannot be more than 16 characters'

        if content:
            title = 'Invalid username'
            content += '\n\n-Username must be at least 4 characters long and no more than 16\n-Username cannot start with @'
            networking.NetworkingData.ls.display_notification(title, content)

            return False

        return True


class Username(TextInput):
    first = True

    def clear(self):
        if self.first:
            self.text = ''
            self.first = False
        elif self.text == '':
            self.text = 'username'
            self.first = True


class Password(TextInput):
    first = True

    def clear(self):
        if self.first:
            self.text = ''
            self.password = True
            self.first = False
        elif self.text == '':
            self.text = 'password'
            self.password = False
            self.first = True


class DateOfBirth(GridLayout):
    day = ''
    month = ''
    year = ''

    def update_day(self, day):
        self.day = day
        self.check_date()

    def update_month(self, month):
        self.month = month
        self.check_date()

    def update_year(self, year):
        self.year = year
        self.check_date()

    def check_date(self):
        if self.day == '' or self.month == '' or self.year == '':
            return

        months_30 = ['4', '6', '9', '11']
        if self.month == '2' and int(self.day) > 29:
            self.activate_error()
        elif self.month == '2' and int(self.day) == 29 and not self.leap_year():
            self.activate_error()
        elif self.month in months_30 and int(self.day) == 31:
            self.activate_error()
        else:
            self.error.info.text = ''

    def activate_error(self):
        self.error.info.text = 'Please enter a valid date'

    def leap_year(self):
        if self.year == '':
            return True
        return (int(self.year) - 1952) % 4 == 0


class Terms(GridLayout):
    def open_terms(self):
        terms_popup = TermsPopup()
        terms_popup.open()
