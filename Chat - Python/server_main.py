import socket
import select
import sqlite3
import random
import time
import datetime
import math


"""
            TODO:
                ~make sure to uncomment the call to make_admin in the handle_promote_request function
"""


IP = '0.0.0.0'
PORT = 6000


CYCLE_SLEEP = 0.025


OK = str(0x100)
FAIL = str(0x101)


NOTIFICATION = '*'
STATUS_CHANGE = '%'
LOGIN_SIGNUP = '$'


MUTE_DEFAULT_TIME = 3
BLOCK_DEFAULT_TIME = 3
BAN_DEFAULT_TIME = 3

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

    def __init__(self, username='', sock=None, logged_in=False, colour='', addrs=''):
        self.username = username
        self.sock = sock
        self.logged_in = logged_in
        self.colour = colour
        self.addrs = addrs

    def blocked_by(self, other):
        return other in self.blockers


class Message:
    receivers = []
    content = ''

    def __init__(self, receivers=list(), content=''):
        self.receivers = receivers
        self.content = content


def get_client(val, type=BY_SOCKET):
    """
    gets the client object which contains the given socket
    """
    if type == BY_SOCKET:
        return next((clnt for clnt in clients if clnt.sock is val), None)
    elif type == BY_NAME:
        return next((clnt for clnt in clients if clnt.username == val), None)


def get_random_colour():
    """
    generates a random colour
    """
    colors = ['00ff72', '56b4f7', '001dff', 'e3ff30', 'ff8c00', 'c41313', '6b12c4', 'ff26da']
    return random.choice(colors)


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
        print 'LOST CONNECTION TO CLIENT'
        disconnect_client(source)
        return ''
    msg = source.recv(msg_len)
    print msg
    return msg


def disconnect_client(client):
    """
    disconnects a client
    """
    print 'DISCONNECTED CLIENT'

    messages_to_remove = []

    for message in pending_messages:
        if client in message.receivers:
            message.receivers.remove(client)

            if len(message.receivers) == 0:
                messages_to_remove.append(message)

    for message in messages_to_remove:
        pending_messages.remove(message)

    client.close()
    clnt = get_client(client)
    clients.remove(clnt)


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
        sql_cursor.execute('INSERT INTO users VALUES (:username, :password, :day, :month, :year)', {'username': username,
                                                                                                    'password': password,
                                                                                                    'day': day,
                                                                                                    'month': month,
                                                                                                    'year': year})
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
    print 'CONNECTING CLIENT'
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

        print type

        if type == NORMAL_MESSAGE:
            add_message(request, source)
        elif type == PRIVATE_MESSAGE:
            handle_private_msg(request, source)
        elif type == MUTE:
            handle_mute(request, source)
        elif type == BLOCK:
            handle_block(request, source)
        elif type == KICK:
            pass
        elif type == BAN:
            pass
        elif type == PROMOTE:
            handle_promote(request, source)
        elif type == STATS:
            pass
        elif type == UNMUTE:
            handle_unmute(request, source)
        elif type == UNBLOCK:
            pass
        elif type == UNBAN:
            pass


def is_admin(username):
    """
    checks whether a user is an admin
    """
    sql_cursor.execute('SELECT * FROM admins WHERE username=:username', {'username': username})
    return sql_cursor.fetchone()


def handle_block(request, src):
    """
    handles a block request
    """
    print request
    source, target = split_message(request)

    if not logged_in(target):
        print 'not logged in'
        pending_messages.append(Message([src], BLOCK + format_part(FAIL) + format_part('user not connected')))
    else:
        trg_user = get_client(target, BY_NAME)

        if src in trg_user.blockers:
            print 'already muted'
            pending_messages.append(Message([src], BLOCK + format_part(FAIL) + format_part('user already blocked')))
        else:
            src_user = get_client(src)

            block(src, trg_user, BLOCK_DEFAULT_TIME)

            pending_messages.append(Message([src], BLOCK + format_part(OK) + format_part(trg_user.colour)))
            pending_messages.append(Message([trg_user.sock], STATUS_CHANGE + BLOCK + format_part(src_user.username) + format_part(src_user.colour) + format_part(BLOCK_DEFAULT_TIME)))

            broadcast(NOTIFICATION + )



def handle_unmute(request, src):
    """
    handles an unmute request
    """
    print request
    source, target = split_message(request)

    if not is_admin(source):
        print 'user is not an admin'
        pending_messages.append(Message([src], UNMUTE + format_part(FAIL) + format_part('you must be an admin to unmute someone')))
        return

    if not logged_in(target):
        print 'not logged in'
        pending_messages.append(Message([src], UNMUTE + format_part(FAIL) + format_part('user not connected')))
    elif target not in muted_users.keys():
        print 'user is not muted'
        pending_messages.append(Message([src], UNMUTE + format_part(FAIL) + format_part('user is not muted')))
    else:
        unmute(target)
        src_user = get_client(src)
        trg_user = get_client(target, BY_NAME)

        pending_messages.append(Message([src], UNMUTE + format_part(OK) + format_part(trg_user.colour)))
        pending_messages.append(Message([trg_user.sock], STATUS_CHANGE + format_part(UNMUTE) + format_part(source) + format_part(src_user.colour)))

        broadcast(NOTIFICATION + format_part(UNMUTE) + format_part(source) + format_part(src_user.colour) + \
                        format_part(target) + format_part(trg_user.colour), [src, trg_user.sock])


def handle_promote(request, src):
    """
    handles a promote request
    """
    user_reqeusting, user_to_promote = split_message(request)

    if not is_admin(user_reqeusting):
        print 'not admin'
        pending_messages.append(Message([src], PROMOTE + format_part(FAIL) + format_part('you must be an admin to promote someone')))
        return

    if not logged_in(user_to_promote):
        print 'not logged in'
        pending_messages.append(Message([src], PROMOTE + format_part(FAIL) + format_part('user not connected')))
    elif is_admin(user_to_promote):
        print 'user already admin'
        pending_messages.append(Message([src], PROMOTE + format_part(FAIL) + format_part('user already admin')))
    else:
        #make_admin(user_to_promote)
        src_user = get_client(src)
        trg_user = get_client(user_to_promote,  BY_NAME)

        pending_messages.append(Message([src], PROMOTE + format_part(OK) + format_part(trg_user.colour)))
        pending_messages.append(Message([trg_user.sock], STATUS_CHANGE + format_part(PROMOTE) + \
                        format_part(user_reqeusting) + format_part(src_user.colour)))

        promote_msg = NOTIFICATION + format_part(PROMOTE) + format_part(src_user.username) + \
                        format_part(src_user.colour) + format_part(user_to_promote)+ format_part(trg_user.colour)
        broadcast(promote_msg, [src, trg_user.sock])


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
        print 'not admin'
        pending_messages.append(Message([src], MUTE + format_part(FAIL) + format_part('you must be an admin to mute someone')))
        return

    parts = split_message(req)

    user_to_mute = parts[1]

    if logged_in(user_to_mute):
        print 'logged in'
        if len(parts) == 2:
            mute_length = mute(user_to_mute)
        elif len(parts) == 3:
            mute_length = mute(user_to_mute, float(parts[2]))
        else:
            print 'Error - unknown error occurred'

        pending_messages.append(Message([src], MUTE + format_part(OK)))
        target = get_client(user_to_mute, BY_NAME)
        pending_messages.append(Message([target.sock], STATUS_CHANGE + format_part(MUTE) + format_part(get_client(src).username) + format_part(mute_length)))
        broadcast(NOTIFICATION + format_part(MUTE) + format_part(get_client(src).username) + format_part(target.username), [src, target.sock])
    else:
        print 'not logged in'
        pending_messages.append(Message([src], MUTE + format_part(FAIL) + format_part('user not connected')))


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
        if client.username == user:
            return True

    return False


def handle_private_msg(msg, source):
    """
    handles a private message
    """
    sender, receiver_name, message = split_message(msg)

    target = get_client(receiver_name, BY_NAME)

    if not target:
        print 'FOUND NO SUCH USER'
        send_data(source, format_part(FAIL) + format_part('Error - found no such user'))
        return

    src = get_client(source)

    if src.blocked_by(target.sock):
        print 'BLOCKED BY RECEIVER'
        send_data(source, format_part(FAIL) + format_part('Error - you are blocked by the receiver'))
        return

    pending_messages.append(Message([source], format_part(OK) + format_part(target.colour)))

    usernames = '[color=' + src.colour + ']' + sender + '[/color] > [color=' + target.colour + ']ME[/color]'
    formatted_message = PRIVATE_MESSAGE + format_part(usernames) + format_part(message)
    print formatted_message
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
    formatted_message = '[color=' + colour + '][b]' + parts[0] + '[/b][/color]'
    formatted_message = NORMAL_MESSAGE + str(len(formatted_message)) + '-' + formatted_message + str(len(parts[1])) + '-' + parts[1]
    print formatted_message
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
            print 'VALID LOGIN'
            send_data(client, str(len(OK)) + '-' + OK + str(len(get_client(client).colour)) + '-' + get_client(client).colour)
            get_client(client).logged_in = True
            get_client(client).username = parts[0]

            broadcast(NOTIFICATION + LOGIN_SIGNUP + format_part(parts[0]) + format_part(get_client(client).colour), [client])
        else:
            send_data(client, format_part(FAIL) + format_part(status))
    elif len(parts) == 5:
        valid, status = valid_signup(parts)

        if valid:
            print 'VALID SIGNUP'
            send_data(client, format_part(OK) + format_part(get_client(client).colour))
            get_client(client).logged_in = True
            get_client(client).username = parts[0]

            broadcast(NOTIFICATION + LOGIN_SIGNUP + format_part(parts[0]) + format_part(get_client(client).colour), [client])
        else:
            send_data(client, format_part(FAIL) + format_part(status))
    else:
        print 'Error - failed to log in / sign up'
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
                print get_client(receiver).username, message.content
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
    user.blockers[blocker] = time


def ban(user, time=BAN_DEFAULT_TIME):
    """
    bans a user
    """
    pass


def promote(user):
    """
    promotes a user to admin status
    """
    pass


def kick(user):
    """
    kicks a user
    """
    pass


def unmute(user):
    """
    unmutes a user
    """
    del muted_users[user]


def unblock(blocker, user):
    """
    unblocks a user
    """
    pass


def stats(user=''):
    """
    displays stats about a user
    """
    pass


def unban(user):
    """
    unbans a user
    """
    pass


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


def main():
    init_server()

    last = datetime.datetime.now()
    now = datetime.datetime.now()
    temp = datetime.datetime.now()
    dt = 0

    while True:
        temp = now
        now = datetime.datetime.now()
        dt = (now - last).microseconds / 1e6
        last = temp

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
