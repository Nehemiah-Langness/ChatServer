from os import name as osName
from sys import stdin
from select import select
from multiprocessing import Process
from textwrap import TextWrapper
from traceback import format_exc

import networkingInterface
import terminal
from server import externalEntry

if (osName != "nt"):
    from multiprocessing import set_start_method

messages = []                          # Holds the sent messages
errors = []                            # Holds the logged errors
interface = None                       # The network interface
quit = False                           # Whether or not to quit
refresh = False                        # whether or not to redraw the screen
wrapper = TextWrapper(width=60, break_long_words=False)    # The object to handle text wrapping


# notify(message)
# message -- The message to add
# Adds a message from the client to be displayed witu server messages
def notify(message):
    addMessage(terminal.Foreground.LIME + message + terminal.Font.CLEAR)


# addMessage(message)
# message -- the message to add
# Adds a message to the buffer
def addMessage(message):
    global messages

    messages.append(message)

    # Keep only between 40 to 80 messages
    if (len(messages) >= 80):
        messages = messages[-40:]

    # Notify user there is a message
    print("\007")


# addError(message)
# message -- the error message
# Add an error to the log
def addError(message):
    errors.append(message)


# isData(message)
# message -- the string to check
# Returns whether or not the string contains alpha-numeric data
def isData(message):
    isData = True                      # Assume the string is data
    index = 0                          # Index in the string to check
    length = len(message)              # Length of the string
    isEscape = False                   # Whether or not an escape sequence is being retrieved

    # Look until the end or a alpha-numeric character is reached
    while ((index < length) and (isData)):
        if (isEscape):
            if (message[index] == "m"):
                isEscape = False
        else:
            if (message[index] == "\033"):
                isEscape = True
            else:
                char = ord(message[index])
                if (char > 33 and char < 127):
                    isData = False
        index += 1

    return isData


# drawMessages()
# Draws the messages in the buffer to the screen
def drawMessages():
    for message in messages[-40:]:
        # Don't wrap data
        if (isData(message)):
            print(message)

        else:
            for line in wrapper.wrap(message):
                print(line)


# printErrors()
# Draw the logged errors to the screen
def printErrors():
    for message in errors:
        terminal.error(message)


# iniateHandshake(userName)
# userName -- the username to connect with
# Attempt to join the server and recieve a response
# Returns if it is successful
def initiateHandshake(userName):
        print("Testing connection...")

        # Send a join and the request a participant list
        data = testServerReachable("J:" + userName, "L:")
        if (data is not None):
            notify("Ready to internet!  Your server says:")
            handleMessage(data)
            return True
        else:
            return False


# testServerReachable(message, ping)
# message -- the message to atttempt to send to the server
# ping -- a message to send that will generate a response
def testServerReachable(message, ping):

        data = None

        # Attempt to send a message to the server
        if (message is not None):
            print("Sending message...")
            if (interface.testSend(message)):
                data = ("M:Server reachable", interface.getHost())

            else:
                addError("Unable to contact server :(")
                return None

        # Attempt to recieve a message from the server after sending a ping
        if (ping is not None):
            print("Pinging...")
            data = interface.testRecieve(pingMessage=ping)

            if (data is None):
                addError("Server was unresponsive :(")

        return data


# getInput()
# Return a line from stdin and process it
# Sets the refresh flag to true
def getInput():
    global refresh

    userInput = stdin.readline().strip('\n')
    parseUserInput(userInput)
    refresh = True


# parseUserInput(command)
# command -- the input from the user
# Parse the input from the user and execute any commands
def parseUserInput(command):
    global quit

    if (command == ""):
        return
    elif (command[0] == "\\"):
        interface.sendPacket("", interface.getHost(), command[1:])
    elif (command.upper() == "Q:"):
        # Handle tye quit message
        quit = True
    elif (command[0:2].upper() == "S:"):
        # Handle a shutdown command
        interface.sendShutdown(command[2:])
    elif (command.upper() == "P:" or command.upper() == "L:"):
        # Ping the server
        print("Pinging...")
        data = interface.testRecieve(pingMessage="L:")
        if (data is None):
            notify("Server was unresponsive :(")
        else:
            notify("Server is responsive!!")
    else:
        # Assume that the message is a chat message
        interface.sendMessage(command)


# screenRefresh()
# Clear the terminal and then redraw the messages and the input bar
def screenRefresh():
    terminal.clear()
    drawMessages()
    print()
    terminal.printInput("Enter your message (\"Q:\" to exit)")


# handleMessage(data)
# Process the message recieved from the host
def handleMessage(data):
    global quit

    # Drop packets not from the host
    if (data[2] != interface.getHost()):
        addError("Packet recieved not from server - Recieved from " + str(data[1]) + " | Server "+ str(interface.getHost()))
        return

    # Save the command and message
    command = data[0]
    message = data[1]

    # Shutdown command
    if (command == "S"):
        addError("Server shut down")
        quit = True

    # Message command
    elif (command == "M"):
        addMessage(message)

    # Join command
    elif (command == "J"):
        pass

    # List command
    elif (command == "L"):
        pass

    # Quit command
    elif (command == "Q"):
        addError("Kicked by server")
        quit = True

    # Participant list command
    elif (command == "P"):
        notify("Here's who's here")
        for participant in message.split(";"):
            info = participant.split(",")
            if (len(info) == 3):
                addMessage(info[0] + " @ " + info[1] + " joined at " + info[2] + terminal.Font.CLEAR)
            else:
                # Accomodate for servers that don't send extra info
                addMessage(participant + " is present")


# startServer()
# Start a daemonic server process as a child of this process
def startServer():
    if (osName != "nt"):
        set_start_method("spawn")
        
    serv = Process(target=externalEntry)
    serv.daemon = True
    serv.start()


# killServer()
# Connect to the currently configured host and send the shutdown message
def killServer():
    interface.connectToHost()
    interface.testSend("J:Ninja Killer")
    interface.testSend("S:sudo, die")


# getHostFromUser()
# Ask the user for the host.  Default to the current if none provided
# Returns the host name
def getHostFromUser():
    terminal.clear()
    print("What is the host name (" + interface.getHost()[0] + ")?")
    newhost = terminal.getInput(">> ")
    if (newhost == ""):
        newhost = interface.getHost()[0]
    return newhost


# getPortFromUser()
# Ask the user for the port.  Default to the current if none provided
# Returns the host port
def getPortFromUser():
    terminal.clear()
    print("What is the host port (" + str(interface.getHost()[1]) + ")?")
    newport = terminal.getInput(">> ")
    if (newport == ""):
        newport = interface.getHost()[1]
    else:
        newport = int(newport)
    return newport


# getUserNameFromUser()
# Request a user name from the user
# Response can be a client command
# Return the entered username
def getUserNameFromUser():
    userName = ""
    while (userName == "" or userName[0:5] == "sudo,"):
        print("What is your name?")
        userName = terminal.getInput(">> ")
        terminal.clear()

        # If it is a sudo command, do it
        if (userName[0:5] == "sudo,"):
            handleSudoCommand(userName[6:])

    return userName


# Perform tasks based on what is up
def handleSudoCommand(command):

    # Spawn a host process
    if (command == "I'm the host"):
        startServer()
        print("You are the host, master")

    # Kill the current host
    if (command == "remove the host"):
        killServer()
        print("The server is not a problem anymore, master")

def exitWhenUserReady():
    printErrors()
    terminal.getInput("Press any key to continue...")

# main()
# Do the whole thing
def main():
    global interface
    global quit
    interface = networkingInterface.Interface()

    # Get configuration
    newhost = getHostFromUser()
    newport = getPortFromUser()

    terminal.clear()
    print("Host is set to be", newhost, "using port", newport)
    interface.configure(newhost, newport)


    # Get user info
    userName = getUserNameFromUser()

    # Connect to the host
    if (interface.connectToHost()):
        if (not initiateHandshake(userName)):
            exitWhenUserReady()
            return
    else:
        addError("Unable to internet :(")
        exitWhenUserReady()
        return

    # Create the inputs
    socket = interface.getSocket()
    inputList = [socket, stdin]
    screenRefresh()


    # Main loop
    while (not quit):

        try:
            # Listen and process information
            rIn, rOut, rEr = select(inputList, [], [])
            for activity in rIn:
                if (activity is stdin):
                    getInput()

                elif (activity is socket):
                    handleMessage(interface.recieve())
            screenRefresh()

        except KeyboardInterrupt:
            # Handle a ctrl+c
            quit = True
            addError("Manual shutdown")

        except:
            # Display any errors
            notify(format_exc())

    # Gracefully shut down and show logged errors
    terminal.clear()
    interface.sendQuit()
    exitWhenUserReady()
    

if (__name__ == "__main__"):
    main()
