import socket
import select
import sqlite3
import random
import datetime
import time
import math


IP = '0.0.0.0'
PORT = 6000


CYCLE_SLEEP = 0.025  # time between each server cycle


OK = str(0x100)
FAIL = str(0x101)


NOTIFICATION = '*'
STATUS_CHANGE = '%'
LOGIN_SIGNUP = '$'


MUTE_DEFAULT_TIME = 0.1  # in minutes
BLOCK_DEFAULT_TIME = 0.1  # in minutes

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


BY_SOCKET = 0
BY_NAME = 1


sql_connection = sqlite3.connect('deps/user.db')
sql_cursor = sql_connection.cursor()


server = None
clients = []
pending_messages = []
muted_users = {}


class Client:
    username = ''
    sock = None
    logged_in = False
    colour = ''
    addrs = ''
    blockers = {}
    login_time = ''
    _login_time = None

    def __init__(self, username='', sock=None, logged_in=False, colour='', addrs='', login_time='', _login_time=None):
        self.username = username
        self.sock = sock
        self.logged_in = logged_in
        self.colour = colour
        self.addrs = addrs
        self.login_time = login_time
        self._login_time = _login_time

    def blocked_by(self, other):
        return other in self.blockers


class Message:
    receivers = []
    content = ''

    def __init__(self, receivers=list(), content=''):
        self.receivers = receivers
        self.content = content


def get_users(excluded=''):
    """
    gets all of the users and formats their names into a long string indicating which ones are admins, online and offline
    """
    sql_cursor.execute('SELECT * FROM users WHERE username!=:username', {'username': excluded})
    matches = sql_cursor.fetchall()

    if matches:
        all_users = [match[0] for match in matches]
        online = [client.username for client in clients if client.username in all_users]

        for online_user in online:
            all_users.remove(online_user)

        sql_cursor.execute('SELECT * FROM admins WHERE username!=:username', {'username': excluded})
        matches = sql_cursor.fetchall()

        if matches:
            admins = [match[0] for match in matches if match[0] in online]

            for admin in admins:
                online.remove(admin)

        else:
            admins = []

        admins = ''.join([format_part(admin) for admin in admins])
        online = ''.join([format_part(user) for user in online])
        all_users = ''.join([format_part(user) for user in all_users])

        complete_users = format_part(admins) + format_part(online) + format_part(all_users)

        return format_part(complete_users)


def get_client(val, type=BY_SOCKET):
    """
    gets the client object which contains the given socket
    """
    if type == BY_SOCKET:
        return next((clnt for clnt in clients if clnt.sock is val), None)
    elif type == BY_NAME:
        return next((clnt for clnt in clients if clnt.username == val), None)


def get_name(clnt):
    """
    gets the name of a client
    """
    return get_client(clnt).username


def get_random_colour():
    """
    generates a random colour
    """
    colors = ['00ff72', '56b4f7', '001dff', 'e3ff30', 'ff8c00', 'c41313', '6b12c4', 'ff26da']
    return random.choice(colors)


def get_formatted_time():
    """
    gets a formatted version of the current time and date
    """
    t = datetime.datetime.now()
    x = str(t.day).zfill(2) + '/' + str(t.month).zfill(2) + '/' + str(t.year)[-2:] + ' ' + str(t.hour).zfill(2) + ':' + str(t.minute).zfill(2)
    return x


def init_server():
    """
    initializes the server
    """
    global server
    server = socket.socket()
    server.bind((IP, PORT))
    server.listen(5)
    return server


def receive_data(source):
    """
    receives a single message from a source
    """
    try:
        msg_len = int(source.recv(16))
    except:
        disconnect_client(source)
        return ''
    msg = source.recv(msg_len)
    return msg


def disconnect_client(client):
    """
    disconnects a client
    """
    if not get_client(client).logged_in:
        clnt = get_client(client)
        clients.remove(clnt)
        client.close()
        return

    broadcast(NOTIFICATION + format_part(LEAVE) + format_part(get_name(client)) + format_part(get_client(client).colour), client)

    sql_cursor.execute('UPDATE users SET last_seen=:last_seen WHERE username=:username', {'last_seen': get_formatted_time(), 'username': get_name(client)})
    sql_connection.commit()

    now = datetime.datetime.now()
    delta = now - get_client(client)._login_time
    time_online = delta.seconds
    sql_cursor.execute('UPDATE users SET time_online=:time_online WHERE username=:username', {'time_online': time_online, 'username': get_name(client)})
    sql_connection.commit()

    messages_to_remove = []

    for message in pending_messages:
        if client in message.receivers:
            message.receivers.remove(client)

            if len(message.receivers) == 0:
                messages_to_remove.append(message)

    for message in messages_to_remove:
        pending_messages.remove(message)

    clnt = get_client(client)
    clients.remove(clnt)
    client.close()


def send_data(receiver, message):
    """
    sends a single message
    """
    receiver.send(str(len(message)).zfill(16))
    receiver.send(message)


def split_message(msg):
    """
    separates the message 
    """
    parts = []

    current = ''
    count = ''
    ld = False
    for ch in msg:
        if type(count) is str or type(count) is unicode:
            if ch.isdigit():
                count += ch
                ld = True
            if ch == '-' and ld:
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


def valid_login(login):
    """
    checks if the login is valid
    """
    username, password = login
    sql_cursor.execute('SELECT * FROM users WHERE username=:username', {'username': username})
    matching = sql_cursor.fetchall()

    if matching is None or len(matching) == 0:
        return False, 'Error - no such user'

    success = False

    for match in matching:
        if match[1] == password:
            success = True
            break

    for client in clients:
        if client.logged_in and client.username == username:
            return False, 'Error - already signed in'

    sql_cursor.execute('SELECT * FROM banned WHERE username=:username', {'username': username})
    matching = sql_cursor.fetchall()

    if matching:
        return False, 'Error - user is banned'

    if success:
        return True, ''

    return False, 'Error - password not matching'


def valid_signup(signup):
    """
    checks if the signup is valid
    """

    username, password, day, month, year = signup
    day = int(day)
    month = int(month)
    year = int(year)
    sql_cursor.execute('SELECT * FROM users WHERE username=:username', {'username': username})
    matching = sql_cursor.fetchall()

    if matching is None or len(matching) == 0:
        last_seen = 'NA'
        time_online = 0
        sql_cursor.execute('INSERT INTO users VALUES (:username, :password, :day, :month, :year, :last_seen, :time_online)',
                        {'username': username,
                         'password': password,
                         'day': day,
                         'month': month,
                         'year': year,
                         'lsat_seen': last_seen,
                         'time_online': time_online})
        sql_connection.commit()
        return True, ''

    return False, 'Error - name already taken'


def process_read(rl):
    """
    processes read functionality
    """
    for sock in rl:
        if sock is server:
            connect_client()
        else:
            request = receive_data(sock)
            process_request(request, sock)


def connect_client():
    """
    connects a client to the chat
    """
    client, addrs = server.accept()
    colour = get_random_colour()
    clients.append(Client('', client, False, colour, addrs))


def process_request(request, source):
    """
    processes a request from a single source client
    """
    if request.startswith(LOGIN_SIGNUP):
        login_client(request, source)
    else:
        type = request[:2]
        request = request[2:]

        if type == NORMAL_MESSAGE:
            add_message(request, source)
        elif type == PRIVATE_MESSAGE:
            handle_private_msg(request, source)
        elif type == MUTE:
            handle_mute(request, source)
        elif type == BLOCK:
            handle_block(request, source)
        elif type == KICK:
            handle_kick(request, source)
        elif type == BAN:
            handle_ban(request, source)
        elif type == PROMOTE:
            handle_promote(request, source)
        elif type == STATS:
            handle_stats(request, source)
        elif type == UNMUTE:
            handle_unmute(request, source)
        elif type == UNBLOCK:
            handle_unblock(request, source)
        elif type == UNBAN:
            handle_unban(request, source)


def is_admin(username):
    """
    checks whether a user is an admin
    """
    sql_cursor.execute('SELECT * FROM admins WHERE username=:username', {'username': username})
    return sql_cursor.fetchone()


def handle_stats(request, src):
    """
    handles a request to get stats about a user
    """
    user_requesting, target = split_message(request)

    if not user_exists(target):
        pending_messages.append(Message([src],  format_part(FAIL) + format_part('no such user')))
    elif logged_in(target):
        trg_user = get_client(target, BY_NAME)
        x = is_admin(target)
        x = True if x else False
        msg = format_part('1') + format_part(str(trg_user.login_time)) + format_part(str(get_time_online(target))) + \
                                        format_part(str(int(x))) + format_part(trg_user.colour)
        pending_messages.append(Message([src], msg))
    else:
        x = is_admin(target)
        x = True if x else False
        msg = format_part('0') + format_part(str(get_last_seen(target))) + format_part(str(get_time_online(target))) + \
                                        format_part(str(int(x))) + format_part(get_random_colour())
        pending_messages.append(Message([src], msg))


def get_last_seen(user):
    """
    gets the last time a user has been seen
    """
    sql_cursor.execute("SELECT * FROM users WHERE username=:username", {'username': user})
    matching = sql_cursor.fetchone()

    if matching:
        return matching[5]


def get_time_online(user):
    """
    gets the amount of time a user has spend online
    """
    if logged_in(user):
        now = datetime.datetime.now()
        delta = now - get_client(user, BY_NAME)._login_time
        minutes = str(int(math.floor(delta.seconds / 60)))
        seconds = str(int(math.floor(delta.seconds % 60)))

        if minutes != '0':
            x = minutes + ' minutes'

            if seconds != '0':
                x += ' and ' + seconds + ' seconds'
        else:
            x = seconds + ' seconds'

        return x

    sql_cursor.execute("SELECT * FROM users WHERE username=:username", {'username': user})
    matching = sql_cursor.fetchone()

    if matching:
        x = matching[6]
        minutes = str(int(math.floor(x / 60)))
        seconds = str(int(math.floor(x)) % 60)

        if minutes != '0':
            x = minutes + ' minutes'

            if seconds != '0':
                x += ' and ' + seconds + ' seconds'
        else:
            x = seconds + ' seconds'

        return x


def handle_unban(request, src):
    """
    handles a request to unban a user
    """
    user_unbanning, target = split_message(request)

    if not is_admin(user_unbanning):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('you must be an admin to unban someone')))
    elif not is_banned(target):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('you cannot unban a user who is not banned')))
    else:
        clr = get_random_colour()

        pending_messages.append(Message([src], format_part(OK) + format_part(clr)))

        unban(target)


def handle_ban(request, src):
    """
    handles a request to ban a user
    """
    user_banning, target = split_message(request)

    if not is_admin(user_banning):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('you must be an admin to ban someone')))
    elif is_banned(target):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('you cannot ban a user who is already banned')))
    elif is_admin(target):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('you cannot ban another admin')))
    else:
        admin = get_client(src)

        if logged_in(target):
            trg_user = get_client(target, BY_NAME)

            now = datetime.datetime.now()
            delta = now - trg_user._login_time
            time_online = delta.seconds
            sql_cursor.execute('UPDATE users SET time_online=:time_online WHERE username=:username', {'time_online': time_online, 'username': target})
            sql_connection.commit()

            if logged_in(target):
                for message in pending_messages:
                    if trg_user.sock in message.receivers:
                        message.receivers.remove(trg_user.sock)

                pending_messages.append(Message([trg_user.sock], STATUS_CHANGE + format_part(BAN) + format_part(admin.username) + format_part(admin.colour)))

                trg_user.username = ''
                trg_user.logged_in = False
                trg_user.blockers = {}
                trg_user.login_time = ''
                trg_user._login_time = None

            clr = trg_user.colour
        else:
            clr = get_random_colour()

        pending_messages.append(Message([src], format_part(OK) + format_part(clr)))

        broadcast(NOTIFICATION + format_part(BAN) + format_part(user_banning) + format_part(admin.colour) + \
                  format_part(target) + format_part(clr), [src] if not logged_in(target) else [src, trg_user.sock])

        ban(target)


def is_banned(user):
    """
    checks if a user is banned
    """
    sql_cursor.execute('SELECT * FROM banned WHERE username=:username', {'username': user})
    matching = sql_cursor.fetchall()

    if matching:
        return True

    return False


def user_exists(user):
    """
    checks if a user exists
    """
    sql_cursor.execute('SELECT * FROM users WHERE username=:username', {'username': user})
    matching = sql_cursor.fetchall()

    if matching:
        return True

    return False


def handle_kick(request, src):
    """
    handles a request to kick a user
    """
    user_kicking, user_to_kick = split_message(request)

    if not logged_in(user_to_kick):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('user not connected')))
    elif not is_admin(user_kicking):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('you must be an admin to kick someone')))
    elif is_admin(user_to_kick):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('cannot kick an admin')))
    else:
        trg_user = get_client(user_to_kick, BY_NAME)
        pending_messages.append(Message([src], format_part(OK) + format_part(trg_user.colour)))

        kick_user(trg_user, get_client(src))

        broadcast(NOTIFICATION + format_part(KICK) + format_part(user_kicking) + format_part(get_client(src).colour) + \
                  format_part(user_to_kick) + format_part(trg_user.colour), [src, trg_user.sock])


def handle_unblock(request, src):
    """
    handles a request to unblock a user
    """
    user_unblocking, user_to_unblock = split_message(request)

    if not logged_in(user_to_unblock):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('user not connected')))
    else:
        trg_user = get_client(user_to_unblock, BY_NAME)

        if src not in trg_user.blockers.keys():
            pending_messages.append(Message([src], format_part(FAIL) + format_part('user is not blocked')))
        else:
            unblock(src, trg_user)
            src_user = get_client(src)

            pending_messages.append(Message([src], format_part(OK) + format_part(trg_user.colour)))
            pending_messages.append(Message([trg_user.sock], STATUS_CHANGE + format_part(UNBLOCK) + \
                                            format_part(user_unblocking) + format_part(src_user.colour)))


def handle_block(request, src):
    """
    handles a block request
    """
    req = split_message(request)

    if len(req) == 2:
        source, target = req
        duration = BLOCK_DEFAULT_TIME
    elif len(req) == 3:
        source, target, duration = req
    else:
        pending_messages.append(Message([src], format_part(FAIL) + format_part('unkown error occurred')))
        return

    if not logged_in(target):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('user not connected')))
    elif is_admin(target):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('cannot block an admin')))
    else:
        trg_user = get_client(target, BY_NAME)

        if src in trg_user.blockers.keys():
            pending_messages.append(Message([src], format_part(FAIL) + format_part('user already blocked')))
        else:
            src_user = get_client(src)

            block(src, trg_user, float(duration))

            pending_messages.append(Message([src], format_part(OK) + format_part(trg_user.colour)))
            pending_messages.append(Message([trg_user.sock], STATUS_CHANGE + format_part(BLOCK) + format_part(src_user.username) + \
                                            format_part(src_user.colour) + format_part(str(duration))))


def handle_unmute(request, src):
    """
    handles an unmute request
    """
    source, target = split_message(request)

    if not is_admin(source):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('you must be an admin to unmute someone')))
        return

    if not logged_in(target):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('user not connected')))
    elif target not in muted_users.keys():
        pending_messages.append(Message([src], format_part(FAIL) + format_part('user is not muted')))
    else:
        unmute(target)
        src_user = get_client(src)
        trg_user = get_client(target, BY_NAME)

        pending_messages.append(Message([src], format_part(OK) + format_part(trg_user.colour)))
        pending_messages.append(Message([trg_user.sock], STATUS_CHANGE + format_part(UNMUTE) + format_part(source) + format_part(src_user.colour)))

        broadcast(NOTIFICATION + format_part(UNMUTE) + format_part(source) + format_part(src_user.colour) + \
                        format_part(target) + format_part(trg_user.colour), [src, trg_user.sock])


def handle_promote(request, src):
    """
    handles a promote request
    """
    user_reqeusting, user_to_promote = split_message(request)

    if not is_admin(user_reqeusting):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('you must be an admin to promote someone')))
        return

    if not logged_in(user_to_promote):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('user not connected')))
    elif is_admin(user_to_promote):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('user already admin')))
    else:
        make_admin(user_to_promote)
        src_user = get_client(src)
        trg_user = get_client(user_to_promote,  BY_NAME)

        pending_messages.append(Message([src], format_part(OK) + format_part(trg_user.colour)))
        pending_messages.append(Message([trg_user.sock], STATUS_CHANGE + format_part(PROMOTE) + \
                        format_part(user_reqeusting) + format_part(src_user.colour)))

        promote_msg = NOTIFICATION + format_part(PROMOTE) + format_part(src_user.username) + \
                        format_part(src_user.colour) + format_part(user_to_promote)+ format_part(trg_user.colour)
        broadcast(promote_msg, [src, trg_user.sock])


def kick_user(target, admin):
    """
    kicks a user
    """
    target.logged_in = False

    for message in pending_messages:
        if target.sock in message.receivers:
            message.receivers.remove(target.sock)

    sql_cursor.execute('UPDATE users SET last_seen=:last_seen WHERE username=:username', {'last_seen': get_formatted_time(), 'username': target.username})
    sql_connection.commit()

    now = datetime.datetime.now()
    delta = now - target._login_time
    time_online = delta.seconds
    sql_cursor.execute('UPDATE users SET time_online=:time_online WHERE username=:username', {'time_online': time_online, 'username': target.username})
    sql_connection.commit()

    target.username = ''
    target.blockers = {}
    target.logged_in = False
    target.login_time = ''
    target._login_time = None

    pending_messages.append(Message([target.sock], STATUS_CHANGE + format_part(KICK) + format_part(admin.username) + format_part(admin.colour)))


def make_admin(username):
    """
    promotes a user to admin status
    """
    sql_cursor.execute('INSERT INTO admins VALUES (:username)', {'username': username})
    sql_connection.commit()


def handle_mute(req, src):
    """
    handles a mute request
    """
    if not is_admin(get_client(src).username):
        pending_messages.append(Message([src], format_part(FAIL) + format_part('you must be an admin to mute someone')))
        return

    parts = split_message(req)

    user_to_mute = parts[1]

    if logged_in(user_to_mute):
        if len(parts) == 2:
            mute_length = mute(user_to_mute)
        elif len(parts) == 3:
            mute_length = mute(user_to_mute, float(parts[2]))
        else:
            print 'Error - unknown error occurred'

        pending_messages.append(Message([src], format_part(OK)))
        target = get_client(user_to_mute, BY_NAME)
        pending_messages.append(Message([target.sock], STATUS_CHANGE + format_part(MUTE) + format_part(get_client(src).username) + format_part(mute_length)))
        broadcast(NOTIFICATION + format_part(MUTE) + format_part(get_client(src).username) + format_part(target.username), [src, target.sock])
    else:
        pending_messages.append(Message([src], format_part(FAIL) + format_part('user not connected')))


def broadcast(message, excluded=None):
    """
    sends a message to every, may specify excluded users
    """
    if not excluded:
        receivers = [client.sock for client in clients if client.logged_in]
    elif type(excluded) is socket.socket:
        receivers = [client.sock for client in clients if client.sock is not excluded and client.logged_in]
    elif type(excluded) is list:
        receivers = [client.sock for client in clients if client.sock not in excluded and client.logged_in]

    pending_messages.append(Message(receivers, message))


def logged_in(user):
    """
    checks whether a user is logged in
    """
    for client in clients:
        if client.username == user and client.logged_in:
            return True

    return False


def handle_private_msg(msg, source):
    """
    handles a private message
    """
    sender, receiver_name, message = split_message(msg)

    target = get_client(receiver_name, BY_NAME)

    if not target:
        send_data(source, format_part(FAIL) + format_part('Error - found no such user'))
        return

    src = get_client(source)

    if src.blocked_by(target.sock):
        send_data(source, format_part(FAIL) + format_part('Error - you are blocked by the receiver'))
        return

    pending_messages.append(Message([source], format_part(OK) + format_part(target.colour)))

    prefix = ''
    if is_admin(sender):
        prefix = '@'

    usernames = '[color=' + src.colour + ']' + prefix + sender + '[/color] > [color=' + target.colour + ']ME[/color]'
    formatted_message = PRIVATE_MESSAGE + format_part(usernames) + format_part(message)
    pending_messages.append(Message([target.sock], formatted_message))


def format_part(part):
    """formats a single part"""
    return str(len(part)) + '-' + part


def add_message(message, source):
    """
    adds a message to the pending messages list
    """
    src = get_client(source)
    receivers = [client.sock for client in clients if client.sock is not source and client.sock not in src.blockers.keys() and client.logged_in]
    colour = src.colour
    parts = split_message(message)
    username = parts[0]
    prefix = ''
    if is_admin(username):
        prefix = '@'
    formatted_message = '[color=' + colour + '][b]' + prefix + username + '[/b][/color]'
    formatted_message = NORMAL_MESSAGE + str(len(formatted_message)) + '-' + formatted_message + str(len(parts[1])) + '-' + parts[1]
    pending_messages.append(Message(receivers, formatted_message))


def login_client(info, client):
    """
    logs a client in
    """
    info = info[1:]
    parts = split_message(info)

    if len(parts) == 2:
        valid, status = valid_login(parts)

        if valid:
            x = is_admin(parts[0])
            x = True if x else False

            send_data(client, format_part(OK) + format_part(get_client(client).colour) + format_part(str(int(x))) + get_users(parts[0]))
            get_client(client).logged_in = True
            get_client(client).username = parts[0]
            get_client(client).login_time = get_formatted_time()
            get_client(client)._login_time = datetime.datetime.now()

            broadcast(NOTIFICATION + LOGIN_SIGNUP + format_part(parts[0]) + format_part(get_client(client).colour) + format_part(str(int(x))), [client])
        else:
            send_data(client, format_part(FAIL) + format_part(status))
    elif len(parts) == 5:
        valid, status = valid_signup(parts)

        if valid:
            x = is_admin(parts[0])
            x = True if x else False

            send_data(client, format_part(OK) + format_part(get_client(client).colour) + format_part(str(int(x))))
            get_client(client).logged_in = True
            get_client(client).username = parts[0]
            get_client(client).login_time = get_formatted_time()
            get_client(client)._login_time = datetime.datetime.now()

            broadcast(NOTIFICATION + LOGIN_SIGNUP + format_part(parts[0]) + format_part(get_client(client).colour) + format_part(str(int(x))) + get_users(parts[0]), [client])
        else:
            send_data(client, format_part(FAIL) + format_part(status))
    else:
        send_data(client, FAIL)


def send_pending_messages(wl):
    """
    sends pending message
    """
    messages_to_remove = []  # holds sent messages

    for message in pending_messages:  # for every message
        received = []

        for receiver in message.receivers:  # for every receiver
            if receiver in wl:  # if the receiver can receive data
                send_data(receiver, message.content)  # send the data
                received.append(receiver)

        for receiver in received:  # for every receiver who has received the data
            message.receivers.remove(receiver)  # remove the receiver

        if len(message.receivers) == 0:  # if there are no more receivers to send the data to
            messages_to_remove.append(message)  # mark the message as sent

    for message in messages_to_remove:  # for every message marked as sent
        pending_messages.remove(message)  # remove the message


def mute(user, time=MUTE_DEFAULT_TIME):
    """
    mutes a user for a given amount of time (minutes)
    """
    if user in muted_users.keys():
        muted_users[user] += time * 60
    else:
        muted_users[user] = time * 60

    mute_length = muted_users[user]
    minutes = int(math.floor(mute_length / 60))
    seconds = int(math.floor(mute_length % 60))

    return str(minutes) + ',' + str(seconds)


def block(blocker, user, time=BLOCK_DEFAULT_TIME):
    """
    blocks a user
    """
    user.blockers[blocker] = time * 120  # for some reason the block timer went down twice as fast as
                                         # the other ones so I multiplied it by 120 instead of 60 since
                                         # I was running low on time


def unmute(user):
    """
    unmutes a user
    """
    del muted_users[user]


def unblock(blocker, user):
    """
    unblocks a user
    """
    del user.blockers[blocker]


def ban(username):
    """
    bans a user
    """
    sql_cursor.execute('INSERT INTO banned VALUES(:username)', {'username': username})
    sql_connection.commit()

    last_seen = get_formatted_time()
    sql_cursor.execute('UPDATE users SET last_seen=:last_seen WHERE username=:username', {'last_seen': last_seen, 'username': username})
    sql_connection.commit()


def unban(username):
    """
    unbans a user
    """
    sql_cursor.execute('DELETE FROM banned WHERE username=:username', {'username': username})
    sql_connection.commit()


def tick(dt):
    """
    progresses time reliant processes
    """
    no_longer_mutes = []

    for user in muted_users.keys():
        muted_users[user] -= dt

        if muted_users[user] <= 0:
            no_longer_mutes.append(user)

    for user in no_longer_mutes:
        del muted_users[user]
        pending_messages.append(Message([get_client(user, BY_NAME).sock], STATUS_CHANGE + format_part(UNMUTE)))

    for user in clients:
        no_longer_blocking = []

        for blocker in user.blockers:
            user.blockers[blocker] -= dt

            if user.blockers[blocker] <= 0:
                no_longer_blocking.append(blocker)

        for blocker in no_longer_blocking:
            del user.blockers[blocker]


def main():
    init_server()

    last = datetime.datetime.now()
    now = datetime.datetime.now()
    dt = 0

    while True:
        last = now
        now = datetime.datetime.now()
        dt = (now - last).microseconds / 1e6

        clnts = [client.sock for client in clients]
        rl, wl, xl = select.select(clnts + [server], clnts + [server], clnts + [server])

        if len(rl) > 0:
            process_read(rl)

        if len(wl) > 0:
            send_pending_messages(wl)

        tick(dt)

        time.sleep(CYCLE_SLEEP)


if __name__ == '__main__':
    main()
