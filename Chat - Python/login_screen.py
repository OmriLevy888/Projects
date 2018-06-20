from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

import networking


class TermsPopup(Popup):
    pass


class LoginScreen(Screen):
    pass


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

            if not networking.NetworkingData.processing:
                networking.NetworkingData.username = username
                networking.signup(username, password, day, month, year)
        else:
            print 'MUST CHECK TERMS'


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
    def update_terms(self, value):
        print value

    def open_terms(self):
        terms_popup = TermsPopup()
        terms_popup.open()
