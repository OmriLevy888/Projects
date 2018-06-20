import socket
import select
import re

from general_functions import *


SERVER_IP = '127.0.0.1'
SERVER_PORT = 6000


NO_PROCESS = -1
LOGIN = 0
SIGNUP = 1
PRIVATE_MSG_PRC = 2
MUTE_PRC = 3
BLOCK_PRC = 4
PROMOTE_PRC = 7
UNMUTE_PRC = 9


OK = str(0x100)
FAIL = str(0x101)


NOTIFICATION = '*'
STATUS_CHANGE = '%'
LOGIN_SIGNUP = '$'


NORMAL_MESSAGE = '00'
PRIVATE_MESSAGE = '01'
MUTE = '02'
BLOCK = '03'
KICK = '04'
BAN = '05'
PROMOTE = '06'
STATS = '07'
UNMUTE = '08'
UNBLOCK = '09'
UNBAN = '10'


NOTIFICATION_COLOUR = '000000'


commands = ['msg', 'admin', 'mute', 'kick', 'ban', 'unmute', 'block', 'unblock', 'stats']


class NetworkingData:
    server = None  # references the server
    chat_display = None  # references the chat display
    pending_messages = []  # holds messages to send to the server as strings
    processing = False  # indicates if a process is going on
    process = 0  # indicates the current process
    process_data = ''  # holds data related to the process
    sm = None  # references the screen manager
    username = ''  # the name of the user
    colour = ''  # the colour used for the user
    muted = False  # indicates if the user is muted


def tick(dt):
    """
    runs the networking processes
    :parm dt: the time since the last tick
    """
    rl, wl, xl = select.select([NetworkingData.server], [NetworkingData.server], [NetworkingData.server])

    if len(rl) > 0:
        receive_data()

    if len(wl) > 0:
        send_pending_messages()


def init_connection():
    """
    creates a connection with the server
    """
    server = socket.socket()
    server.connect((SERVER_IP, SERVER_PORT))
    NetworkingData.server = server


def set_sm(sm):
    """
    sets the screen manager
    """
    NetworkingData.sm = sm


def receive_data():
    """
    receives data from the server
    """
    try:
        msg_len = int(NetworkingData.server.recv(16))
    except:
        print 'LOST CONNECTION TO SERVER'
        return
    msg = NetworkingData.server.recv(msg_len)

    if NetworkingData.processing:
        execute_process(msg)
    elif msg.startswith(STATUS_CHANGE):
        handle_status_change(msg[1:])
    elif msg.startswith(NOTIFICATION):
        display_notification(msg[1:])
    else:
        type = msg[:2]
        msg = msg[2:]

        print 'TYPE', type

        if type == NORMAL_MESSAGE or type == PRIVATE_MESSAGE:
            print 'TYPE', type
            formatted_msg = format_server_msg(msg)
            NetworkingData.chat_display.text += formatted_msg


def display_notification(notification):
    """
    displays a notification
    """
    if notification.startswith(LOGIN_SIGNUP):
        name, colour = split_message(notification[1:])
        NetworkingData.chat_display.text += '[b][color=' + colour + ']' + name + '[/color] has joined the chat![/b]\n'
        return

    parts = split_message(notification)

    notification_type = parts[0]

    if notification_type == MUTE:
        NetworkingData.chat_display.text += '[b][color=' + NOTIFICATION_COLOUR + ']Server: ' + parts[1] + \
                                ' has muted ' + parts[2] + '[/color][/b]\n'
    elif notification_type == PROMOTE:
        NetworkingData.chat_display.text += '[b][color=' + parts[2] + ']' + parts[1] + '[/color] has promoted [color=' + \
                                parts[4] + ']' + parts[3] + '[/color] to admin status[/b]\n'


def split_message(msg):
    """
    separates the message 
    """
    parts = []

    count = ''
    current = ''
    ld = False
    for ch in msg:
        if type(count) is str or type(count) is unicode:
            if ch.isdigit():
                count += ch
                ld = True
            if ch == '-' and ld:
                count = int(count)
                ld = False
        else:
            current += ch
            count -= 1

            if count == 0:
                count = ''
                parts.append(current)
                current = ''

    return tuple(parts)


def handle_status_change(change):
    """
    handles a status change
    """
    parts = split_message(change)

    change_type = parts[0]

    if change_type == MUTE:
        minutes = parts[2][:parts[2].index(',')]
        seconds = parts[2][parts[2].index(',') + 1:]

        if minutes == '0':
            NetworkingData.chat_display.text += '[color=' + NOTIFICATION_COLOUR + '][b]Server:[/b] ' + parts[1] + \
                                                ' has muted you for ' + seconds + ' seconds[/color]' + '\n'
        elif seconds == '0':
            NetworkingData.chat_display.text += '[color=' + NOTIFICATION_COLOUR + '][b]Server:[/b] ' + parts[1] + \
                                                ' has muted you for ' + minutes + ' minutes[/color]' + '\n'
        else:
            NetworkingData.chat_display.text += '[color=' + NOTIFICATION_COLOUR + '][b]Server:[/b] ' + parts[1] + \
                                        ' has muted you for ' + minutes + ' minutes and ' + seconds + ' seconds[/color]' + '\n'
        NetworkingData.muted = True
    elif change_type == UNMUTE:
        NetworkingData.chat_display.text += '[color=' + NOTIFICATION_COLOUR + '][b]Server:[/b] you are no longer ' + \
                                    'muted' + '\n'
        NetworkingData.muted = False
    elif change_type == PROMOTE:
        NetworkingData.chat_display.text += '[b][color=' + parts[2] + ']' + parts[1] + '[/color] has promoted you to admin status[/b]' + '\n'


def format_server_msg(message):
    """
    formats a text message from the server
    """
    print 'message to format', message
    parts = split_message(message)
    x = '[b]' + parts[0] + ':[/b] ' + parts[1] + '\n'
    print x
    return x


def execute_process(msg):
    """
    handles the current process
    """
    print 'hey there omri', msg
    print NetworkingData.process
    if NetworkingData.process == LOGIN or NetworkingData.process == SIGNUP:
        parts = split_message(msg)

        if parts[0] == OK:
            NetworkingData.colour = parts[1]
            NetworkingData.sm.current = 'chat_screen'

        else:
            print parts[1]
    elif NetworkingData.process == PRIVATE_MSG_PRC:
        print 'message', msg
        parts = split_message(msg)

        if parts[0] == OK:
            display_private_message(parts[1])
        else:
            print parts[1]
    elif NetworkingData.process == MUTE_PRC:
        process_mute_response(msg[2:])
    elif NetworkingData.process == PROMOTE_PRC:
        handle_promote_response(msg[2:])
    elif NetworkingData.process == UNMUTE_PRC:
        handle_unmute_response(msg[2:])
    elif NetworkingData.process == BLOCK_PRC:
        handle_block_response(msg[2:])

    NetworkingData.process = NO_PROCESS
    NetworkingData.processing = False
    NetworkingData.process_data = ''


def send_pending_messages():
    """
    sends pending messages
    """
    for message in NetworkingData.pending_messages:
        send_message(message)

    NetworkingData.pending_messages = []


def send_message(message):
    """
    sends a single message
    :param message: the message
    """
    if len(message) == 0 or message is None:
        print 'Error: - cannot send an empty message'
        return

    NetworkingData.server.send(str(len(message)).zfill(16))
    NetworkingData.server.send(message)


def login(username, password):
    """
    logs the user in
    :param username: the username 
    :param password: the password
    """
    login_msg = LOGIN_SIGNUP + format_part(username) + format_part(password)
    NetworkingData.pending_messages.append(login_msg)
    NetworkingData.processing = True
    NetworkingData.process = LOGIN
    NetworkingData.username = username


def signup(username, password, day, month, year):
    """
    signs the user up
    :param username: the username
    :param password: the password
    :param day: day of birth
    :param month: month of birth
    :param year: year of birth
    """
    signup_msg = LOGIN_SIGNUP + format_part(username) + format_part(password) + format_part(day) + format_part(month) + \
                    format_part(year)
    NetworkingData.pending_messages.append(signup_msg)
    NetworkingData.processing = True
    NetworkingData.process = SIGNUP


def process_message(msg):
    """
    processes a message
    :param msg: the message to be sent
    :return: a status code indicating whether the message will be sent or not, and why
    """
    if NetworkingData.muted:
        return '[color=' + NOTIFICATION_COLOUR + '][b]Server:[/b] you are currently muted'

    if is_command(msg):
        valid, parts = process_command(msg)

        if not valid:
            return parts
    else:
        formatted_msg = format_text_msg(msg)
        NetworkingData.pending_messages.append(formatted_msg)

    if not NetworkingData.processing:
        return OK

    return FAIL


def is_command(msg):
    """
    checks whether the message is a command
    """
    return msg.startswith('>>')


def process_command(cmd):
    """
    processes a command
    """
    valid, parts = split_command(cmd)

    if not valid:
        print parts
        return False, parts

    cmd_type = parts[0]

    if cmd_type == 'msg':
        print 'msg'
        send_private_message(parts)
    elif cmd_type == 'mute':
        print 'mute'
        mute_user(parts)
    elif cmd_type == 'promote':
        print 'promote'
        promote_user(parts)
    elif cmd_type == 'unmute':
        print 'unmute'
        unmute_user(parts)
    elif cmd_type == 'block':
        print 'block'
        block_user(parts)

    return True, ''


def split_command(cmd):
    """
    splits a command
    """
    match = re.search(r'>>(\w+) <([\w -]+)> (.+)', cmd)

    if match:
        return two_arg_command(match)

    match = re.search(r'>>(\w+) <([\w -]+)>', cmd)

    if match:
        return one_arg_command(match)


def two_arg_command(match):
    command = match.group(1).lower()

    if command == 'msg':
        if match.group(2) == NetworkingData.username:
            return False, '[color=' + NOTIFICATION_COLOUR + '][b]Error[/b] - you cannot send a private message to yourself[/color]'

        return True, (command, match.group(2), match.group(3))

    if command == 'mute':
        if match.group(2) == NetworkingData.username:
            return False, '[color=' + NOTIFICATION_COLOUR + '][b]Error[/b] - you cannot mute yourself[/color]'

        if not is_number(match.group(3)):
            print match.group(3)
            return False, 'Error - must enter a valid amount of time'

        if match.group(3).startswith('-'):
            return False, 'Error - cannot mute a user for a negative amount of time'

        return True, (command, match.group(2), match.group(3))

    return False, 'Error - unknown command'


def one_arg_command(match):
    command = match.group(1).lower()

    if command == 'mute':
        if match.group(2) == NetworkingData.username:
            return False, '[color=' + NOTIFICATION_COLOUR + '][b]Error[/b] - you cannot mute yourself[/color]'

        return True, (command, match.group(2))

    if command == 'promote':
        if match.group(2) == NetworkingData.username:
            return False, '[color=' + NOTIFICATION_COLOUR + '][b]Error[/b] - you cannot promote yourself to admin'

        return True, (command, match.group(2))

    if command == 'unmute':
        if match.group(2) == NetworkingData.username:
            return False, '[color=' + NOTIFICATION_COLOUR + '][b]Error[/b] - you cannot unmute yourself[/color]'

        return True, (command, match.group(2))

    if command == 'block':
        if match.group(2) == NetworkingData.username:
            return False, '[color=' + NOTIFICATION_COLOUR + '][b]Error[/b] - you cannot block yourself'

        return True, (command, match.group(2))

    return False, 'Error - unknown command'


def format_text_msg(msg):
    """
    formats a message
    """
    return '00' + format_part(NetworkingData.username) + format_part(msg)


def send_private_message(parts):
    """
    sends a private message
    """
    private_msg = PRIVATE_MESSAGE + format_part(NetworkingData.username) + format_part(parts[1]) + format_part(parts[2])
    NetworkingData.process_data = private_msg
    NetworkingData.processing = True
    NetworkingData.process = PRIVATE_MSG_PRC
    NetworkingData.pending_messages.append(private_msg)


def mute_user(parts):
    """
    mutes a user
    """
    print 'starting mute'
    if len(parts) == 2:
        mute_request = MUTE + format_part(NetworkingData.username) + format_part(parts[1])
    elif len(parts) == 3:
        mute_request = MUTE + format_part(NetworkingData.username) + format_part(parts[1]) + format_part(parts[2])
    else:
        print 'Error - unknown error occurred'

    NetworkingData.processing = True
    NetworkingData.process_data = parts[1]
    NetworkingData.process = MUTE_PRC
    NetworkingData.pending_messages.append(mute_request)


def display_private_message(receiver_colour):
    """
    displays a private message on the screen
    """
    un, receiver, msg = split_message(NetworkingData.process_data[2:])
    username = '[b][color=' + NetworkingData.colour + ']Me[/color]'
    receiver_name = '[color=' + receiver_colour + ']' + receiver + '[/color]'

    message = username + ' > ' + receiver_name + ':[/b] ' + msg

    NetworkingData.chat_display.text += message + '\n'


def format_part(part):
    """
    formats a single part of a message
    """
    return str(len(part)) + '-' + part


def process_mute_response(response):
    """
    processes a response to a mute request
    """
    parts = split_message(response)

    if parts[0] == OK:
        NetworkingData.chat_display.text += '[color=' + NOTIFICATION_COLOUR + '][b]Server:[/b] successfully muted ' + \
                                        NetworkingData.process_data + '\n'
    elif parts[0] == FAIL:
        NetworkingData.chat_display.text += '[color=' + NOTIFICATION_COLOUR + '][b]Server:[/b] ' + parts[1] + \
                                        '[/color]' + '\n'


def promote_user(parts):
    """
    promotes a user to admin status
    """
    user_to_promote = parts[1]
    NetworkingData.processing = True
    NetworkingData.process = PROMOTE_PRC
    NetworkingData.process_data = user_to_promote
    promote_msg = PROMOTE + format_part(NetworkingData.username) + format_part(user_to_promote)
    NetworkingData.pending_messages.append(promote_msg)


def handle_promote_response(response):
    """
    handles a response to a promote request
    """
    parts = split_message(response)

    if parts[0] == OK:
        NetworkingData.chat_display.text += '[b]You have promoted [color=' + parts[1] + ']' + NetworkingData.process_data + \
                                    '[/color] to be an admin[/b]\n'
    elif parts[0] == FAIL:
        NetworkingData.chat_display.text += '[color=' + NOTIFICATION_COLOUR + '][b]Server:[/b] failed to promote [b]' + \
                                    NetworkingData.process_data + '[/b] - ' + parts[1]


def unmute_user(parts):
    """
    unmutes a user
    """
    user_to_unmute = parts[1]
    NetworkingData.processing = True
    NetworkingData.process = UNMUTE_PRC
    NetworkingData.process_data = user_to_unmute
    unmute_request = UNMUTE + format_part(NetworkingData.username) + format_part(user_to_unmute)
    NetworkingData.pending_messages.append(unmute_request)


def handle_unmute_response(response):
    """
    handles an unmute response
    """
    parts = split_message(response)

    if parts[0] == OK:
        NetworkingData.chat_display.text += '[b]You have unmuted [color=' + parts[1] + ']' + NetworkingData.process_data + \
                                    '[/color][/b]\n'
    elif parts[0] == FAIL:
        NetworkingData.chat_display.text += '[color=' + NOTIFICATION_COLOUR + '][b]Server:[/b] failed to unmute [b]' + \
                                    NetworkingData.process_data + '[/b] - ' + parts[1] + '[/color]\n'


def block_user(parts):
    """
    blocks a user
    """
    target = parts[1]
    NetworkingData.processing = True
    NetworkingData.process = BLOCK_PRC
    NetworkingData.process_data = target
    block_request = BLOCK + format_part(NetworkingData.username) + format_part(target)
    NetworkingData.pending_messages.append(block_request)


def handle_block_response(response):
    """
    handles a block response
    """
    parts = split_message(response)

    if parts[0] == OK:
        NetworkingData.chat_display.text += '[b]You have blocked [color=' + parts[1] + ']' + NetworkingData.process_data + '[/color][/b]\n'
    elif parts[0] == FAIL:
        NetworkingData.chat_display.text += '[b]Server[/b]: failed to block [b]' + NetworkingData.process_data + '[/b] - ' + parts[1]

