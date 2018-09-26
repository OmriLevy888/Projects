A short overview:
	In order to user the chat, the server must be turned on first. The server is in server_main.py. To open a client, run
	the application.py file. Note: application.py depends on server_crash.py, server_crash.kv, chat.py, chat.kv,
	login_screen.ph, login.kv, general_functions.py and the images in deps/images. The server depends on the user.db found
	in deps. Since the client programme uses kivy for graphics and a little bit of logic with the Clock module (scheduling
	intreval calls), the kivy library is required. I have not provided a copy of Kivy, since some of the dependencies of
	Kivy are too big to be uploaded to the Moodle, but here (https://kivy.org/doc/stable/installation/installation-windows.html#install-win-dist)
	you can find the installation for Kivy, it's as simple as use pip to install the dependencies and then the library 
	itself, sorry for the size of the library, I didn't think about the fact you would also have to run it (I am fairly 
	certain the you can skip gstream, since I don't recall using any of its functionality, and since it is the biggest 
	dependency, about 120 MB, it should shrink things down, though if you do skip on it, and something breaks on Kivy's side,
	it would be the most logical explanation.) Note: I do not possess any of the kivy library, which is produced by the kivy 
	team, and uses an MIT free distribution liscence.

	I have decided not to include certain commands, such as view-managers, since there is a list of all active online admins
	to the left of the chat at all times and it seemed useless in my opinion once I have it there. I also decided to change
	stats a bit, instead of stats returning information about all users, I decided to make it a bit more verbose, and for
	it to return infomation about one user only. I assume the reason you wanted this command was to see how we handle 
	passing lists, and I do have something of the sort when a user logs in and has to receive a list of all the users and
	their statuses (i.e. online, offline and admin). Another missing command is the quit command, since either pressing the
	X button or pressing the quit button at the top left of the screen (near the users list display) would do the same.

	I have also added a few new commands, in particular block, which allows a user to not receive messages from a certain
	user, and even set time limits. The command can be used by non admins, so if someone is spamming the chat, there is no
	need to wait for an admin to mute them, it is possible to simple block them. This also blocks private messages. There
	is an unblock command that stops blocking a user. Another pair is the ban and unban commands, only an admin can use
	them and if an admin decides to ban a user, they won't be able to login until an admin uses the unban command. If the
	user being banned is online at the time of being banned, they are removed from the chat and return to the login screen.

	Another system is the login system, a user can signup and login, although things such as birthdate have no use, it was
	simply for me to try different widgets in kivy and get a feel of how to use them. The users are saved in an sql database
	accessed through sqlite3. The database is located in deps, and has 3 tables: users, admins, banned. I know I could have
	had it all in one table and simply have a boolean status for indicating whther someone is an admin or not, another another
	boolean for indicating whether the user is banned or not, but these tables were made before I know you could add collumns
	to a table, so I guess this has to do.

Protocol description:
	The protocol is a bit weird, far from being efficent, but it works and it's simple enough to be able to glance at a
	message and know what it contains. Each communication is comprised of "parts" - a part is basically any string, prefixed
	with a number and a dash separating them. The commonly used format_part function converts a string to a "part". The
	number before the dash is the length of the string after the dash. Note: the number is in ascii, so each digit takes
	a byte, this was made for simplicity sake when separating the message on the receiving end.
	
	Example:
		my_string = 'hello'
		part = format_part(my_string)
		print part  # this will print '5-hello'
	
	This protocol makes it easy to be able to send everything, even empty strings when needed. When separating the parts,
	a function called split_message is used, which goes over the string, as long as it sees numbers, if it encounters a
	dash and the character before it was a digit, it now knows the amount of characters to read, until the next number,
	meaning that any string is possible to pass.
	
	P.S. Before sending a message, another packet, of length 16 containing a number is send, this one indicates the length
	of the entire message, so that one read is enough to receive everything, only then the packet is transformed and split
	into its parts.
	
	There are also some special indicators which do not get formatted, but rather are used to know the general type of the
	packet. They are:
		Notification = *
		STATUS_CHANGE = %
		LOGIN_SIGNUP = $
	When a message is received, it is checked to see which is the first character, to help separate the code and lead to
	different paths according to the message. Notification indicated anything that happened on the server side, and is used
	to notify users, for example, when one user decides to ban another, other users have no idea of it, if the ban is
	successful, a notification message is broadcasted to all but the two parties involved in the ban, to let them know of
	it. Status change is similar to the notification, but it is meant to indicate a change about a user which happened as
	a result of a command, for example, being banned would result in receiving a status change message, same for being
	promoted or muted. A login signup is meant to indicate a user who is not yet in chat and is currently in the process
	of connecting to the chat room.
	
	Last but not least, there is one place where I do send a list, and that is when a user is loggin in, in order to fill
	in the users list display at the top left (the one with Admins:.....Online:.....Offline:.....). It is passed in a bit
	of an inefficent way, but it functions as so: P.S - this is done in a function called get_users in server_main.py
	-3 lists are created on the server side:
		-admins = all the admins who are currently online
		-online = all users who are currently online and are not admins
		-offline = all users who are currently offline
	-each list is then converted into a string, where each element is formatted as a "part"
	-the three strings are then concatenated into a bigger string, where each one of the strings describing a list is
		formatted as a "part"
	-the final string is then once again formatted as a "part" of the final message, and send with it