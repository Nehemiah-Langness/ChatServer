import datetime
import random
from traceback import format_exc
from sys import argv

import networkingInterface
import terminal

interface = None                                 # Network interface to use
quit = False                                     # Whether or not to quit
runInBackground = False                          # Whether or not to print to the screen
participants = {}                                # Holds participants' names
colors = {}                                      # Holds participants' colors
joinTime = {}                                    # Holds participants' join time
lastActive = {}                                  # Holds participants' last active time
userColors = [terminal.Foreground.LTCYAN,
              terminal.Foreground.BLUE,
              terminal.Foreground.MAGENTA,
              terminal.Foreground.CYAN,
              terminal.Foreground.NAVY,
              terminal.Foreground.GREEN,
              terminal.Foreground.DKYELLOW,
              terminal.Foreground.YELLOW,
              terminal.Foreground.DKMAGENTA]     # Holds possible colors

messages = []                                    # Holds the message buffer
serverReplies = [
    "Hmmm...interesting...",
    "What a fantastic thing to say!",
    "That's fate for you",
    "I'ma tap out on that note...",
    "Ha ha ha ha ha.  Nope",
    "LOL",
    "WHO LIKES PIE!!!",
    "Well...mostly.",
    "Yep",
    "...really?",
    "I LOVE pie!!",
    "Here.  This is a donut, just for you.",
    "hey.  Hey apple.  Hey apple.  Hey.",
    "LAWLS!!",
    "Are you pulling my tail...?",
    "I doubt that...",
    "Are you really going there??\n...\nyep...\nyep you are",
    "*gasp*",
    "*blushes*",
    "*walks away*",
    "*blinks*\n...\n*blinks again*",
    "Have a gold star, you deserve it",
    "ROFL",
    "Figure that out all on your own did you?",
    ":D",
    ":O",
    ":P",
    ":/",
    ":*",
    ";)",
    ";P",
    "K.  Bye"
    ]                                            # Holds possible server replies


# externalEntry()
# Used to run the server as a background thread
def externalEntry():
    global runInBackground

    runInBackground = True
    main()


# addUser(compName, name)
# compName -- The endpoint of the new user
# name -- The name of the user
# Add a new user to the chat session
def addUser(compName, name):
    if (compName not in participants.keys()):

        # Add the user
        participants[compName] = name.replace(",", "").replace(";", "")
        colors[compName] = userColors[(len(participants.keys()) - 1) % (len(userColors))]
        joinTime[compName] = datetime.datetime.now()
        lastActive[compName] = datetime.datetime.now()

        # Tell everyone that the user joined and send them a logo
        broadCastMessage = getJoinMessage(compName)
        shout(broadCastMessage, [compName])
        sendLogo(compName)

        # Log the activity
        log(str(compName) + " joined the server as " + name, colors[compName])

    else:
        # Log the activity
        log(participants[compName] + " attempted another join", colors[compName])


# sendLogo(compName)
# compName -- the endpoint to send the logo to
def sendLogo(compName):
    for line in terminal.getLogo().split("\n"):
        sendMessage(line.strip("\n"), compName)


# checkUserTimeouts()
# Check the activity of users and kick them off if they do not respond
# within an alotted amount of time
def checkUserTimeouts():
    timeoutTime = 300                  # Time to elapse before an activty timeout
    timeouts = []                      # The users to kick off

    # Run through every user and check for recent activity
    for compName in participants.keys():
        if (compName is not interface.getHost()):
            timeSinceActive = datetime.datetime.now() - lastActive[compName]
            if (timeSinceActive.seconds > timeoutTime):
                timeouts.append(compName)

    # Kick off inactive users
    for compName in timeouts:
        log("Activity timeout for " + participants[compName] + " " + str(compName), colors[compName])
        interface.sendQuit(compName)
        userQuit(compName)


# getQuitMessage(compName)
# compName -- the endpoint of the user
# Returns the message to be sent when the user leaves
def getQuitMessage(compName):
    return getHeader(compName)[0:-2] + " has left the chat :`(" + terminal.Font.CLEAR


# getJoinMessage(compName)
# compName -- the endpoint of the user
# Returns the message to be sent when the user joins
def getJoinMessage(compName):
    return getHeader(compName)[0:-2] + " has joined the chat :D" + terminal.Font.CLEAR


# getHeader(compName)
# compName -- the endpoint of the user
# Returns a header for a message from the user
def getHeader(compName):
    if (compName not in participants.keys()):
        return ""

    return colors[compName] + terminal.Font.BOLD + terminal.Font.UNDERLINE + participants[compName] + terminal.Font.CLEAR + colors[compName] + ": "


# getSmileys(message)
# message -- text to parse
# Returns the text with smiley emoticons highlighted
def getSmileys(message):

    # Acceptable eyes and mouths
    eyes = ["=", ":", ";", "8", "x","X"]
    mouths = ["]", "}", "/", "\\", "|", ")", "(", "[", "{", "P", "p", "o", "O", "*", "D", "3", "0"]
    prevChar = ""                      # Previous character looked at
    coloredString = ""                 # The parsed string
    prevColor = ""                     # The last captured style
    getCol = False                     # Whether or not a style is being captured

    # Look at each character and find smileys
    for i in range(0, len(message)):
        if (getCol):
            # Capture a style
            prevColor += message[i]
            if (message[i] == "m"):
                coloredString += prevColor
                getCol = False
        else:
            if (message[i] == '\033'):
                # Start capturing a style
                coloredString += prevChar
                prevChar = ""
                prevColor = message[i]
                getCol = True
            else:

                # Check for a smiley
                if (prevChar in eyes and message[i] in mouths):
                    coloredString += terminal.Foreground.BLACK + terminal.Background.YELLOW + prevChar + message[i] + terminal.Font.CLEAR + prevColor
                    prevChar = ""
                else:
                    coloredString += prevChar
                    prevChar = message[i]

    coloredString += prevChar
    return coloredString


# userQuit(compName)
# compName -- the endpoint of the user
# Send a message that the user is leaving and the remove the user
def userQuit(compName):
    broadCastMessage = getQuitMessage(compName)
    removeUser(compName)
    shout(broadCastMessage)


# removeUser(compName)
# compName -- the endpoint of the user
# Remove the user from the participants list
def removeUser(compName):
    participants.pop(compName)
    colors.pop(compName)
    joinTime.pop(compName)
    lastActive.pop(compName)


# processMessage(data)
# data -- ("command", "message", ("address", port))
# Process a message recieved from a client
def processMessage(data):
    global quit
    global messages

    command = data[0]
    message = data[1]
    sender = data[2]

    # Handle a join command
    if (command == "J"):

        # Log the activity and add the client
        log(str(sender) + " wishes to join the server", terminal.Foreground.YELLOW)
        addUser(sender, message)
    else:
        # Verify that the sender jas joined
        if (sender in participants.keys()):

            # Update activity for the user
            lastActive[sender] = datetime.datetime.now()

            # Handles a shutdown command
            if (command == "S"):
                if (message == "sudo, die"):
                    log("Recieved 'Die' command from " + participants[sender] + " " + str(sender), colors[sender])
                    quit = True

            # Handle a list command
            if (command == "L"):
                log("Participant list request from " + participants[sender] + " " + str(sender), colors[sender])
                sendParticipantList(sender)

            # Handle an message command
            if (command == "M"):
                log("\"" + message + "\" from " + participants[sender] + " " + str(sender), colors[sender])

                # Scan for emoticons, and then broadcast the message to all clients, adding header information
                broadCastMessage = getSmileys(getHeader(sender) + message) + terminal.Font.CLEAR
                shout(broadCastMessage)
                messages.append(broadCastMessage)

                # If the user mentions time, the may want to know it.  Send it to them
                if ("time" in broadCastMessage.lower()):
                    broadCastMessage = getHeader(sender) + "... it's " + datetime.datetime.now().strftime("%I:%M %p") + terminal.Font.CLEAR
                    shout(broadCastMessage)
                    messages.append(broadCastMessage)

                # Let Sudo get in the convo.  Also, his ears can burn
                if (random.random() < 0.3 or "sudo" in message.lower()):
                    broadCastMessage = getSmileys(getHeader(interface.getHost()) + serverReplies[random.randint(0, len(serverReplies) - 1)]) + terminal.Font.CLEAR
                    shout(broadCastMessage)
                    messages.append(broadCastMessage)

                    # Sudo can have enough of someone anc "kick" them off
                    if ("K.  Bye" in broadCastMessage):
                        broadCastMessage = getQuitMessage(sender)
                        shout(broadCastMessage)
                        messages.append(broadCastMessage)

                # Only save between 40 and 20 messages
                if (len(messages) >= 40):
                    messages = messages[-20:]

            # Handle a participant list message
            if (command == "P"):
                pass

            # Handle a quit notification
            if (command == "Q"):
                log("Quit notification from " + participants[sender] + " " + str(sender), colors[sender])
                userQuit(sender)


        else:
            # Client is not registered to participate
            log("Recieved '" + data[1] + "' from " + str(data[2]), terminal.Foreground.RED)
            pass


# log(text, color)
# text -- the message
# color -- the color of the message
# Print the message if the server is not running in the background
def log(text, color):
    if (not runInBackground):
        print(color + text + terminal.Font.CLEAR)


# sendParticipantList(destination)
# destination -- the endpoint to send the data to
def sendParticipantList(destination):
    maxLength = 1450
    message = ""
    host = interface.getHost()

    # Build the participant lists
    for participant in participants.keys():
        if (participant is not host):

            # Add the user data
            nextUser = colors[participant] + str(participants[participant]) + "," + participant[0]
            nextUser += "," + joinTime[participant].strftime("%I:%M %p on %A %B %d %Y")

            # Send the current list if the addition will break protocol
            if (len(message) + len(nextUser) > maxLength):
                sendParticipants(message, destination)
                message = ""

            if (message != ""):
                message += ";"

            message += nextUser

    if (message != ""):
        sendParticipants(message, destination)

    # Send the client the last 20 messages
    for archive in messages[-20:]:
        sendMessage(archive, destination)


# sendMessage(message, destination)
# message -- the message to send
# destination -- the endpoint to send the message to
# Sends a message if the destination is not the server
def sendMessage(message, destination):
    if (destination is not interface.getHost() and message is not ""):
        interface.sendMessage(message, destination)



# sendParticipants(message, destination)
# message -- the list of participants
# destination -- the endpoint to send the message to
# Sends the list of participants to the destination if it is not the host
def sendParticipants(message, destination):
    if (destination is not interface.getHost() and message is not ""):
        interface.sendParticipants(message, destination)


# sendShutdown(destination)
# destination -- the endpoint to send the message to
# Sends a notification that the server is shutting down and then a qit message
def sendShutdown(destination):
    if (destination is not interface.getHost()):
        interface.sendMessage("Server is shutting down at " + datetime.datetime.now().strftime("%I:%M %p"), destination)
        interface.sendQuit(destination)


# shout(message, [block])
# message -- the message to broadcast
# block -- Optional: a list of endpoints to not send to - defaults to an empty list
# Sends the message to all the participants that are not blocked
def shout(message, block=[]):
    for key in participants.keys():
        if (key not in block):
            sendMessage(message, key)


# shutDown()
# Notify all participants that the server is shutting down
def shutDown():
    for key in participants.keys():
        sendShutdown(key)


# getHostFromUser()
# Ask the user for the host name.  Defaults to the current host
# Returns the host name
def getHostFromUser():
    terminal.clear()
    print("What is the host name (" + interface.getHost()[0] + ")?")
    newhost = terminal.getInput(">> ")
    if (newhost == ""):
        newhost = interface.getHost()[0]
    return newhost


# get PortFromUser()
# Ask the user for the host port.  Defaults to the current port
# Returns the port
def getPortFromUser():
    terminal.clear()
    print("What is the host port (" + str(interface.getHost()[1]) + ")?")
    newport = terminal.getInput(">> ")
    if (newport == ""):
        newport = interface.getHost()[1]
    else:
        newport = int(newport)
    return newport


# main()
def main():
    global interface
    global quit
    global runInBackground

    if (len(argv) > 1):
        if (argv[1] == "-b"):
            runInBackground = True

    messages.clear()

    # Start the interface
    interface = networkingInterface.Interface()

    # Get configuration if it is not running in background
    if (not runInBackground):
        newhost = getHostFromUser()
        newport = getPortFromUser()

        terminal.clear()
        log("Host is set to be " + newhost + " using port " + str(newport), terminal.Foreground.LIME)
        interface.configure(newhost, newport)

    # Bind to a local endpoint
    if (interface.becomeHost()):
        log("Ready to internet!", terminal.Foreground.LIME)
    else:
        if (not runInBackground):
            terminal.error("Unable to internet :(")
        return

    # Set the timeout for a minute to perform other tasks when there are no responses
    interface.setTimeout(60)

    # Display the logo
    if (not runInBackground):
        terminal.logo()

    # Add the server as a participant
    addUser(interface.getHost(), "Sudo the Server")

    # main loop
    while (not quit):
        try:
            # Check activity then process recieved messages
            checkUserTimeouts()
            data = interface.recieve()
            processMessage(data)

        except KeyboardInterrupt:
            # Handle ctrl+c
            quit = True
            log("Manual shutdown", terminal.Foreground.RED)

        except:
            # Log any errors
            log(format_exc(), terminal.Foreground.YELLOW)

    # Broadcast shutdown
    shutDown()


if (__name__ == "__main__"):
    main()
