import socket
import select
import re
import datetime

from general_functions import *


SERVER_IP = '127.0.0.1'
SERVER_PORT = 6000


# indicates the current process
NO_PROCESS = -1
LOGIN = 0
SIGNUP = 1
PRIVATE_MSG_PRC = 2
MUTE_PRC = 3
BLOCK_PRC = 4
PROMOTE_PRC = 7
UNMUTE_PRC = 9
UNBLOCK_PRC = 10
KICK_PRC = 11
BAN_PRC = 12
UNBAN_PRC = 13
STATS_PRC = 14


# basic status indicators
OK = str(0x100)
FAIL = str(0x101)


# communication type indicators
NOTIFICATION = '*'
STATUS_CHANGE = '%'
LOGIN_SIGNUP = '$'


# request indicators P.S I know I could have used the same ones as the process indicators,
# but I prefer to keep things with different uses separated, even if they are practically the same
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
LEAVE = '11'


# indicates that the server has crashed, used to make sure no code is executed
crash = False


class NetworkingData:
    server = None  # references the server
    chat_display = None  # references the chat display
    user_display = None  # references the user display
    pending_messages = []  # holds messages to send to the server as strings
    processing = False  # indicates if a process is going on
    process = 0  # indicates the current process
    process_data = ''  # holds data related to the process
    sm = None  # references the screen manager
    ls = None  # references the login screen for popups
    username = ''  # the name of the user
    colour = ''  # the colour used for the user
    muted = False  # indicates if the user is muted
    admins = []  # contains the names of all online users who are admins
    online = []  # contains the names of all online users who are not admins
    offline = []  # contains the names of all users who are not connected


def tick(dt):
    """
    runs the networking processes
    :parm dt: the time since the last tick
    """
    global crash

    if crash:
        return

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
        global crash

        crash = True
        NetworkingData.sm.current = 'server_crash_screen'

        return

    msg = NetworkingData.server.recv(msg_len)

    if NetworkingData.processing:  # if currently processing
        execute_process(msg)
    elif msg.startswith(STATUS_CHANGE):  # if received a status change
        handle_status_change(msg[1:])
    elif msg.startswith(NOTIFICATION):  # if received a notification
        display_notification(msg[1:])
    else:
        type = msg[:2]
        msg = msg[2:]

        if type == NORMAL_MESSAGE or type == PRIVATE_MESSAGE:
            formatted_msg = format_server_msg(msg)
            NetworkingData.chat_display.text += formatted_msg


def display_notification(notification):
    """
    displays a notification
    """
    if notification.startswith(LOGIN_SIGNUP):
        name, colour, admin = split_message(notification[1:])
        now = datetime.datetime.now()
        current_time = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)
        NetworkingData.chat_display.text += '[b][' + current_time + '] [color=' + colour + ']' + name + '[/color] has joined the chat![/b]\n'

        if admin == '1':
            NetworkingData.admins.append(name)
        else:
            NetworkingData.online.append(name)

        if name in NetworkingData.offline:
            NetworkingData.offline.remove(name)

        update_user_display()

        return

    parts = split_message(notification)

    notification_type = parts[0]

    if notification_type == MUTE:
        NetworkingData.chat_display.text += '[b]Server: ' + parts[1] + \
                                ' has muted ' + parts[2] + '[/b]\n'
    elif notification_type == PROMOTE:
        name = parts[1]
        NetworkingData.chat_display.text += '[b][color=' + parts[2] + ']' + name + '[/color] has promoted [color=' + \
                                parts[4] + ']' + parts[3] + '[/color] to admin status[/b]\n'

        NetworkingData.online.remove(name)
        NetworkingData.admins.append(name)

        update_user_display()
    elif notification_type == KICK:
        name = parts[1]
        NetworkingData.chat_display.text += '[b][color=' + parts[2] + ']' + name + '[/color] has kicked [color=' + \
                                parts[4] + ']' + parts[3] + '[/color][/b]\n'

        NetworkingData.online.remove(name)
        NetworkingData.offline.append(name)

        update_user_display()
    elif notification_type == BAN:
        name = parts[1]
        NetworkingData.chat_display.text += '[b][color=' + parts[2] + ']' + name + '[/color] has banned [color=' + \
                                parts[4] + ']' + parts[3] + '[/color][/b]\n'

        NetworkingData.online.remove(name)
        NetworkingData.offline.append(name)

        update_user_display()
    elif notification_type == LEAVE:
        name = parts[1]
        now = datetime.datetime.now()
        current_time = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)
        NetworkingData.chat_display.text += '[b][' + current_time + '] [color=' + parts[2] + ']' + name + '[/color] has left the chat\n'

        if name in NetworkingData.admins:
            NetworkingData.admins.remove(name)
        elif name in NetworkingData.online:
            NetworkingData.online.remove(name)

        NetworkingData.offline.append(name)

        update_user_display()


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
            elif ch == '-' and ld:
                count = int(count)
                ld = False

                if count == 0:
                    parts.append('')
                    count = ''
                    current = ''
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
            NetworkingData.chat_display.text += '[b]Server:[/b] ' + parts[1] + \
                                                ' has muted you for ' + seconds + ' seconds' + '\n'
        elif seconds == '0':
            NetworkingData.chat_display.text += '[b]Server:[/b] ' + parts[1] + \
                                                ' has muted you for ' + minutes + ' minutes' + '\n'
        else:
            NetworkingData.chat_display.text += '[b]Server:[/b] ' + parts[1] + \
                                        ' has muted you for ' + minutes + ' minutes and ' + seconds + ' seconds' + '\n'
        NetworkingData.muted = True
    elif change_type == UNMUTE:
        NetworkingData.chat_display.text += '[b]Server:[/b] you are no longer ' + 'muted' + '\n'
        NetworkingData.muted = False
    elif change_type == PROMOTE:
        NetworkingData.chat_display.text += '[b][color=' + parts[2] + ']' + parts[1] + '[/color] has promoted you to admin status[/b]\n'
    elif change_type == BLOCK:
        NetworkingData.chat_display.text += '[b][color=' + parts[2] + ']' + parts[1] + '[/color] has blocked you for ' + str(float(parts[3]) * 60) + ' seconds[/b]\n'
    elif change_type == UNBLOCK:
        NetworkingData.chat_display.text += '[b][color=' + parts[2] + ']' + parts[1] + '[/color] has unblocked you[/b]\n'
    elif change_type == KICK:
        handle_kick(parts)
    elif change_type == BAN:
        handle_ban(parts)


def handle_kick(parts):
    """
    handles being kicked
    """
    kicker, kicker_colour = parts[1], parts[2]

    NetworkingData.pending_messages = []
    NetworkingData.processing = False
    NetworkingData.process = 0
    NetworkingData.process_data = ''
    NetworkingData.username = ''
    NetworkingData.password = ''
    NetworkingData.muted = False

    NetworkingData.sm.current = 'login_screen'

    title = 'You have been kicked!'
    content = 'You have been kicked by [color=' + kicker_colour + ']' + kicker + '[/b][/color]'
    NetworkingData.ls.display_notification(title, content)


def format_server_msg(message):
    """
    formats a text message from the server
    """
    parts = split_message(message)
    now = datetime.datetime.now()
    current_time = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)
    x = '[b][' + current_time + '] ' + parts[0] + ':[/b] ' + parts[1] + '\n'
    return x


def execute_process(msg):
    """
    handles the current process
    """
    if NetworkingData.process == LOGIN or NetworkingData.process == SIGNUP:
        parts = split_message(msg)

        if parts[0] == OK:
            NetworkingData.colour = parts[1]
            NetworkingData.sm.current = 'chat_screen'

            if parts[2] == '1':
                NetworkingData.admins.append(NetworkingData.username + ' (ME)')
            else:
                NetworkingData.online.append(NetworkingData.username + ' (ME)')

            users = parts[3]
            admins, online, offline = split_message(users)

            if admins != '':
                for admin in split_message(admins):
                    NetworkingData.admins.append(admin)

            if online != '':
                for user in split_message(online):
                    NetworkingData.online.append(user)

            if offline != '':
                for user in split_message(offline):
                    NetworkingData.offline.append(user)

            update_user_display()

            NetworkingData.chat_display.text += '[b]Welcome!\nIf you need any help, type in >>help[/b]\n'

        else:
            NetworkingData.ls.login.error_display.text = parts[1]
    elif NetworkingData.process == PRIVATE_MSG_PRC:
        parts = split_message(msg)

        if parts[0] == OK:
            display_private_message(parts[1])
        else:
            NetworkingData.chat_display.text += '[b]Server:[/b] ' + parts[1] + '\n'
    elif NetworkingData.process == MUTE_PRC:
        process_mute_response(msg)
    elif NetworkingData.process == PROMOTE_PRC:
        handle_promote_response(msg)
    elif NetworkingData.process == UNMUTE_PRC:
        handle_unmute_response(msg)
    elif NetworkingData.process == BLOCK_PRC:
        handle_block_response(msg)
    elif NetworkingData.process == UNBLOCK_PRC:
        handle_unblock_response(msg)
    elif NetworkingData.process == KICK_PRC:
        handle_kick_response(msg)
    elif NetworkingData.process == BAN_PRC:
        handle_ban_response(msg)
    elif NetworkingData.process == UNBAN_PRC:
        handle_unban_response(msg)
    elif NetworkingData.process == STATS_PRC:
        handle_stats_response(msg)

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
    NetworkingData.username = username


def process_message(msg):
    """
    processes a message
    :param msg: the message to be sent
    :return: a status code indicating whether the message will be sent or not, and why
    """
    if NetworkingData.muted:
        return '[b]Server:[/b] you are currently muted'

    if is_command(msg):
        valid, parts = process_command(msg)

        if valid and parts == 'help':
            return FAIL

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
        return False, parts

    cmd_type = parts[0]

    if cmd_type == 'msg':
        send_private_message(parts)
    elif cmd_type == 'mute':
        mute_user(parts)
    elif cmd_type == 'promote':
        promote_user(parts)
    elif cmd_type == 'unmute':
        unmute_user(parts)
    elif cmd_type == 'block':
        block_user(parts)
    elif cmd_type == 'unblock':
        unblock_user(parts)
    elif cmd_type == 'kick':
        kick_user(parts)
    elif cmd_type == 'ban':
        ban_user(parts)
    elif cmd_type == 'unban':
        unban_user(parts)
    elif cmd_type == 'stats':
        stats(parts)
    elif cmd_type == 'help':
        display_help(parts[1])
        return True, 'help'

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

    if cmd == '>>help':
        return True, ('help', '')

    return False, 'Error - invalid command syntax'


def two_arg_command(match):
    """
    splits commands with two arguments
    """
    command = match.group(1).lower()

    if command == 'msg':
        if match.group(2) == NetworkingData.username:
            return False, '[b]Error[/b] - you cannot send a private message to yourself'

        return True, (command, match.group(2), match.group(3))

    if command == 'mute':
        if match.group(2) == NetworkingData.username:
            return False, '[b]Error[/b] - you cannot mute yourself'

        if not is_number(match.group(3)[1:-1]):
            return False, 'Error - must enter a valid amount of time'

        if match.group(3).startswith('-'):
            return False, 'Error - cannot mute a user for a negative amount of time'

        return True, (command, match.group(2), match.group(3))

    if command == 'block':
        if match.group(2) == NetworkingData.username:
            return False, '[b]Error[/b] - you cannot block yourself'

        if not is_number(match.group(3)[1:-1]):
            return False, 'Error - must be a valid amount of time'

        return True, (command, match.group(2), match.group(3))

    return False, 'Error - unknown command'


def one_arg_command(match):
    """
    splits command with one argument
    """
    command = match.group(1).lower()

    if command == 'mute':
        if match.group(2) == NetworkingData.username:
            return False, '[b]Error[/b] - you cannot mute yourself'

        return True, (command, match.group(2))

    if command == 'promote':
        if match.group(2) == NetworkingData.username:
            return False, '[b]Error[/b] - you cannot promote yourself to admin'

        return True, (command, match.group(2))

    if command == 'unmute':
        if match.group(2) == NetworkingData.username:
            return False, '[b]Error[/b] - you cannot unmute yourself'

        return True, (command, match.group(2))

    if command == 'block':
        if match.group(2) == NetworkingData.username:
            return False, '[b]Error[/b] - you cannot block yourself'

        return True, (command, match.group(2))

    if command == 'unblock':
        if match.group(2) == NetworkingData.username:
            return False, '[b]Error[/b] - you cannot block yourself'

        return True, (command, match.group(2))

    if command == 'kick':
        if match.group(2) == NetworkingData.username:
            return False, '[b]Error[/b] - you cannot kick yourself'

        return True, (command, match.group(2))

    if command == 'ban':
        if match.group(2) == NetworkingData.username:
            return False, '[b]Error[/b] - you cannot ban yourself'

        return True, (command, match.group(2))

    if command == 'unban':
        if match.group(2) == NetworkingData.username:
            return False, '[b]Error[/b] - you cannot unban yourself'

        return True, (command, match.group(2))

    if command == 'stats':
        return True, (command, match.group(2))

    if command == 'help':
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
    if len(parts) == 2:
        mute_request = MUTE + format_part(NetworkingData.username) + format_part(parts[1])
    elif len(parts) == 3:
        t = float(parts[2][1:-1])
        mute_request = MUTE + format_part(NetworkingData.username) + format_part(parts[1]) + format_part(str(t))
    else:
        print 'Error - unknown error occurred'
        return

    NetworkingData.processing = True
    NetworkingData.process_data = parts[1]
    NetworkingData.process = MUTE_PRC
    NetworkingData.pending_messages.append(mute_request)


def display_private_message(receiver_colour):
    """
    displays a private message on the screen
    """
    un, receiver, msg = split_message(NetworkingData.process_data[2:])
    username = '[color=' + NetworkingData.colour + ']ME[/color]'
    receiver_name = '[color=' + receiver_colour + ']' + receiver + '[/color]'
    now = datetime.datetime.now()
    current_time = str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)
    message = '[b][' + current_time + '] ' + username + ' > ' + receiver_name + ':[/b] ' + msg

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
        NetworkingData.chat_display.text += '[b]Server:[/b] successfully muted ' + NetworkingData.process_data + '\n'
    elif parts[0] == FAIL:
        NetworkingData.chat_display.text += '[b]Server:[/b] ' + parts[1] + '\n'


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

        NetworkingData.online.remove(NetworkingData.process_data)
        NetworkingData.admins.append(NetworkingData.process_data)

        update_user_display()
    elif parts[0] == FAIL:
        NetworkingData.chat_display.text += '[b]Server:[/b] failed to promote [b]' + \
                                    NetworkingData.process_data + '[/b] - ' + parts[1] + '\n'


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
        NetworkingData.chat_display.text += '[b]Server:[/b] failed to unmute [b]' + NetworkingData.process_data + '[/b] - ' + \
                                            parts[1] + '\n'


def block_user(parts):
    """
    blocks a user
    """
    target = parts[1]

    if len(parts) == 3:
        duration = parts[2][1:-1]
        block_request = BLOCK + format_part(NetworkingData.username) + format_part(target) + format_part(duration)
    else:
        block_request = BLOCK + format_part(NetworkingData.username) + format_part(target)

    NetworkingData.processing = True
    NetworkingData.process = BLOCK_PRC
    NetworkingData.process_data = target

    NetworkingData.pending_messages.append(block_request)


def handle_block_response(response):
    """
    handles a block response
    """
    parts = split_message(response)

    if parts[0] == OK:
        NetworkingData.chat_display.text += '[b]You have blocked [color=' + parts[1] + ']' + NetworkingData.process_data + '[/color][/b]\n'
    elif parts[0] == FAIL:
        NetworkingData.chat_display.text += '[b]Server[/b]: failed to block [b]' + NetworkingData.process_data + '[/b] - ' + parts[1] + '\n'


def unblock_user(parts):
    """
    unblocks a user
    """
    target = parts[1]
    NetworkingData.processing = True
    NetworkingData.process = UNBLOCK_PRC
    NetworkingData.process_data = target
    request = UNBLOCK + format_part(NetworkingData.username) + format_part(target)
    NetworkingData.pending_messages.append(request)


def handle_unblock_response(response):
    """
    handles a response to an unblock request
    """
    status, data = split_message(response)

    if status == FAIL:
        NetworkingData.chat_display.text += '[b]Server[/b]: failed to unblock [b]' + NetworkingData.process_data + '[/b] - ' + data + '\n'
    else:
        NetworkingData.chat_display.text += '[b]You have unblocked [color=' + data + ']' + NetworkingData.process_data + '[/color][/b]\n'


def kick_user(parts):
    """
    kicks a user
    """
    target = parts[1]
    NetworkingData.processing = True
    NetworkingData.process = KICK_PRC
    NetworkingData.process_data = target
    request = KICK + format_part(NetworkingData.username) + format_part(target)
    NetworkingData.pending_messages.append(request)


def handle_kick_response(response):
    """
    handles a response to a rick request
    """
    status, data = split_message(response)

    if status == FAIL:
        NetworkingData.chat_display.text += '[b]Server[/b]: failed to kick [b]' + NetworkingData.process_data + '[/b] - ' + data + '\n'
    else:
        NetworkingData.chat_display.text += '[b]You have kicked [color=' + data + ']' + NetworkingData.process_data + '[/color][/b]\n'

        NetworkingData.online.remove(NetworkingData.process_data)
        NetworkingData.offline.append(NetworkingData.process_data)

        update_user_display()


def ban_user(parts):
    """
    bans a user
    """
    target = parts[1]
    NetworkingData.processing = True
    NetworkingData.process = BAN_PRC
    NetworkingData.process_data = target
    request = BAN + format_part(NetworkingData.username) + format_part(target)
    NetworkingData.pending_messages.append(request)


def unban_user(parts):
    """
    unbans a user
    """
    target = parts[1]
    NetworkingData.processing = True
    NetworkingData.process = UNBAN_PRC
    NetworkingData.process_data = target
    request = UNBAN + format_part(NetworkingData.username) + format_part(target)
    NetworkingData.pending_messages.append(request)


def handle_ban_response(response):
    """
    handles a response to a ban request
    """
    status, data = split_message(response)

    if status == FAIL:
        NetworkingData.chat_display.text += '[b]Server[/b]: failed to ban [b]' + NetworkingData.process_data + '[/b] - ' + data + '\n'
    else:
        NetworkingData.chat_display.text += '[b]You have banned [color=' + data + ']' + NetworkingData.process_data + '[/color][/b]\n'

        if NetworkingData.process_data in NetworkingData.online:
            NetworkingData.online.remove(NetworkingData.process_data)
            NetworkingData.offline.append(NetworkingData.process_data)

            update_user_display()


def handle_ban(parts):
    """
    handles a ban
    """
    admin, admin_colour = parts[1], parts[2]

    NetworkingData.pending_messages = []
    NetworkingData.processing = False
    NetworkingData.process = 0
    NetworkingData.process_data = ''
    NetworkingData.username = ''
    NetworkingData.password = ''
    NetworkingData.muted = False

    NetworkingData.sm.current = 'login_screen'

    title = 'You have been banned'
    content = 'You have been banned by [b][color=' + admin_colour + ']' + admin + '[/color][/b]'
    NetworkingData.ls.display_notification(title, content)


def handle_unban_response(response):
    """
    handles a response to an unban request
    """
    status, data = split_message(response)

    if status == FAIL:
        NetworkingData.chat_display.text += '[b]Server[/b]: failed to unban [b]' + NetworkingData.process_data + '[/b] - ' + data + '\n'
    else:
        NetworkingData.chat_display.text += '[b]You have unbanned [color=' + data + ']' + NetworkingData.process_data + '[/color][/b]\n'


def stats(parts):
    """
    requests stats about a user
    """
    target = parts[1]
    NetworkingData.processing = True
    NetworkingData.process_data = target
    NetworkingData.process = STATS_PRC
    request = STATS + format_part(NetworkingData.username) + format_part(target)
    NetworkingData.pending_messages.append(request)


def handle_stats_response(response):
    """
    handles a response to a stats request
    """
    x = split_message(response)
    online, last_seen, time_online, is_admin, colour = x

    if online == '0':
        # not online
        msg = ''

        if is_admin == '1':
            msg = 'Admin '

        msg += '[color=' + colour + ']' + NetworkingData.process_data + '[/color] is not online. They were last seen online on ' + last_seen + ' and have ' + \
                'been online for a total time of ' + time_online + '\n'

        NetworkingData.chat_display.text += msg
    elif online == '1':
        # is online
        msg = ''

        if is_admin == '1':
            msg = 'Admin '

        msg += '[color=' + colour + ']' + NetworkingData.process_data + '[/color] is online. They logged in on ' + last_seen + ' and have been online for ' + \
                'a total time of ' + time_online + '\n'
        NetworkingData.chat_display.text += msg
    else:
        print 'Error'


def update_user_display():
    """
    updates the user display
    """
    NetworkingData.admins = list(set(NetworkingData.admins))
    NetworkingData.online = list(set(NetworkingData.online))
    NetworkingData.offline = list(set(NetworkingData.offline))

    NetworkingData.admins.sort()
    NetworkingData.online.sort()
    NetworkingData.offline.sort()

    NetworkingData.user_display.text = '\n     [b]Admins:[/b]' + ''.join(['\n        -' + admin for admin in NetworkingData.admins])
    NetworkingData.user_display.text += '\n\n     [b]Online:[/b]' + ''.join(['\n        -' + online for online in NetworkingData.online])
    NetworkingData.user_display.text += '\n\n     [b]Offline:[/b]' + ''.join(['\n        -' + offline for offline in NetworkingData.offline])


def display_help(command=''):
    """
    display help
    """
    commands_help = {'msg': '[b]Private message[/b]\n'
                            '[b]Description:[/b] sends a message to the receiver which is only visible to them\n'
                            '[b]Syntax:[/b] >>msg <name> content\n'
                            '[b]Requirements:[/b] none'
                            '[b]Example:[/b] >>msg <test> hey test, did you know we are the only two who can see this message?\n',
                     'block': '[b]Block[/b]\n'
                              '[b]Description:[/b] blocks all messages from a user, i.e. will not see a user\'s messages or private messages.'
                              'the time parameter is optional and is passed in number of minutes, it default to 3\n'
                              '[b]Syntax:[/b] >>block <name> <time>\n'
                              '[b]Requirements:[/b] none\n'
                              '[b]Example:[/b] >>block <test> <5>\n',
                     'unblock': '[b]Unblock[/b]\n'
                                '[b]Description:[/b] unblocks a blocked user\n'
                                '[b]Syntax:[/b] >>unblock <name>\n'
                                '[b]Requirements:[/b] none'
                                '[b]Example:[/b] >>unblock <test>\n',
                     'mute': '[b]Mute[/b]\n'
                             '[b]Description:[/b] Mutes a user so that no one will see their messages in chat. the time parameter is an optional'
                             'parameter and sets the amount of time the user will be muted, in minutes, defaults to 3\n'
                             '[b]Syntax:[/b] >>mute <name> <time>\n'
                             '[b]Requirements:[/b] must be admin\n'
                             '[b]Example:[/b] >>mute <test> <45>\n',
                     'unmute': '[b]Unmute[/b]\n'
                               '[b]Description:[/b] unmutes a muted user\n'
                               '[b]Syntax:[/b] >>unmute <name>\n'
                               '[b]Requirements:[/b] must be admin\n'
                               '[b]Example:[/b] >>unmute <test>\n',
                     'ban': '[b]Ban[/b]\n'
                            '[b]Description:[/b] bans a user from the chat. the user won\'t be able to log into the chat when banned. takes an'
                            'optional time parameter in minutes, defaults to 3\n'
                            '[b]Syntax:[/b] >>ban <name> <time>\n'
                            '[b]Requirement:[/b] must be admin\n'
                            '[b]Example:[/b] >>ban <test>\n',
                     'unban': '[b]Unban[/b]\n'
                              '[b]Description:[/b] unbans a banned user\n'
                              '[b]Syntax:[/b] >>unban <name>\n'
                              '[b]Requirements:[/b] must be admin\n'
                              '[b]Example:[/b] >>unban <test>\n',
                     'promote': '[b]Promote[/b]\n'
                                '[b]Description:[/b] promotes a user to admin status\n'
                                '[b]Syntax:[/b] >>promote <name>\n'
                                '[b]Requirements:[/b] must be admin\n'
                                '[b]Example:[/b] >>promote <test>\n',
                     'kick': '[b]Kick[/b]\n'
                             '[b]Description:[/b] kicks a user from the chat, they will be able to login again at any time\n'
                             '[b]Syntax:[/b] >>kick <name>\n'
                             '[b]Requirements:[/b] must be admin\n'
                             '[b]Example:[/b] >>kick <test>',
                     'stats': '[b]Stats[/b]\n'
                              '[b]Description:[/b] displays information about a particular user\n'
                              '[b]Syntax:[/b] >>stats <name>\n'
                              '[b]Requirements:[/b] none\n'
                              '[b]Example:[/b] >>stats <test>\n'}

    if command == '':
        NetworkingData.chat_display.text += '\n[b]HELP[/b]\n' \
                                            '[b]Note:[/b] you can type >>help <command> where the command is the shortened one found in the list bellow to get' \
                                            'information about a specific command, i.e to get information about private messages, type >>help <msg>\n' \
                                            '[b]Private message[/b] - >>msg <name> content\n' \
                                            '[b]Block[/b] - >>block <name> <time>\n' \
                                            '[b]Unblock[/b] - >>unblock <name>\n' \
                                            '[b]Mute[/b] - >>mute <name> <time>\n' \
                                            '[b]Unmute[/b] - >>unmute <name>\n' \
                                            '[b]Ban[/b] - >>ban <name>\n' \
                                            '[b]Umbam[/b] - >>unban <name>\n' \
                                            '[b]Promote[/b] - >>promote <name>\n' \
                                            '[b]Kick[/b] - >>kick <name>\n' \
                                            '[b]Stats[/b] - >>stats <name>\n'
    elif command in commands_help.keys():
        NetworkingData.chat_display.text += commands_help[command]
    else:
        NetworkingData.chat_display.text += '[b]Error[/b] - unknown command'
