try:
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
except:
    print("Unable to initialize virtual terminal")


# Class holding constants for font manipulation
class Font:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ITALIC = '\033[3m'
    CLEAR = '\033[0m'

# Class holding constants for text color modification
class Foreground:
    GREY = '\033[90m'
    RED = '\033[91m'
    LIME = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BLACK = '\033[30m'
    DKRED = '\033[31m'
    GREEN = '\033[32m'
    DKYELLOW = '\033[33m'
    NAVY = '\033[34m'
    DKMAGENTA = '\033[35m'
    LTCYAN = '\033[36m'
    LTGREY = '\033[37m'

# Class holding constants for background color modification
class Background:
    GREY = '\033[100m'
    RED = '\033[101m'
    LIME = '\033[102m'
    YELLOW = '\033[103m'
    BLUE = '\033[104m'
    MAGENTA = '\033[105m'
    CYAN = '\033[106m'
    WHITE = '\033[107m'
    BLACK = '\033[40m'
    DKRED = '\033[41m'
    GREEN = '\033[42m'
    DKYELLOW = '\033[43m'
    NAVY = '\033[44m'
    DKMAGENTA = '\033[45m'
    LTCYAN = '\033[46m'
    LTGREY = '\033[47m'

# Clear()
# Clear the terminal window and place the cursor at the bottom of the screen
# Assumes window is less than 100 lines tall
def clear():
    print(Font.CLEAR + '\033[2J' + '\033[100;1H')


# getInput([prompt])
# prompt - Optional: Text to display before asking the user for input - defaults to empty string
# Displays the prompt before asking the user for input.
# Returns the user input
def getInput(prompt=""):

    data = input(Background.WHITE + Foreground.BLACK + '\033[0K' + prompt)
    print(Font.CLEAR)
    return data


# printInput([prompt])
# prompt - Optional: Text to display before asking the user for input - defaults to empty string
# Displays the prompt without recieving input
def printInput(prompt=""):
    print(Background.WHITE + Foreground.BLACK + '\033[0K' + prompt + Font.CLEAR)

# error(message)
# message - the error message to display
# Displays message as an error on the terminal screen
def error(message):
    print(Foreground.LTGREY + Background.RED + message + Font.CLEAR)

# getLogo
# Returns a string that will display the logo when printed
def getLogo():
    m = Background.DKRED
    l = Background.BLUE
    d = Background.NAVY
    g = Background.GREY
    r = Background.RED
    y = Background.YELLOW
    o = Background.DKYELLOW
    w = Background.WHITE

    # pixel data
    data = [
    l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, d,
    l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, l, d, d,
    l, l, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, d, d,
    l, l, g, g, g, g, y, o, g, g, g, g, y, o, g, g, g, g, d, d,
    l, l, g, g, g, g, y, o, g, g, g, g, y, o, g, g, g, g, d, d,
    l, l, g, g, g, g, o, o, g, g, g, g, o, o, g, g, g, g, d, d,
    l, l, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, d, d,
    l, l, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, d, d,
    l, l, g, g, g, g, g, g, g, y, o, g, g, g, g, g, g, g, d, d,
    l, l, g, g, g, g, g, g, g, o, o, g, g, g, g, g, g, g, d, d,
    l, l, g, g, o, g, g, g, g, g, g, g, g, g, g, y, g, g, d, d,
    l, l, g, g, o, g, g, g, g, g, g, g, g, g, g, y, g, g, d, d,
    l, l, y, y, o, g, g, g, g, g, g, g, g, g, g, y, y, o, d, d,
    l, l, y, y, o, g, g, y, y, y, y, y, o, g, g, y, y, o, d, d,
    l, l, y, y, o, g, g, y, y, y, y, y, o, g, g, y, y, o, d, d,
    l, l, g, o, o, g, g, y, w, w, w, w, o, g, g, o, o, g, d, d,
    l, l, g, g, g, g, g, y, w, w, w, w, o, g, g, g, g, g, d, d,
    l, l, g, g, g, g, g, g, y, w, w, o, g, g, g, g, g, g, d, d,
    l, l, g, g, g, g, g, g, y, w, w, o, g, g, g, g, g, g, d, d,
    l, l, g, g, g, g, g, g, g, o, o, g, g, g, g, g, g, g, d, d,
    l, l, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, d, d,
    l, d, d, d, d, d, d, d, d, d, d, d, d, d, d, d, d, d, d, d,
    d, d, d, d, d, d, d, d, d, d, d, d, d, d, d, d, d, d, d, d
    ]

    # run through pixel data and build a string from it
    row = 0
    string = ""
    for pixel in data:
        string += pixel + "  "
        row += 1

        if (row == 20):
            string += Font.CLEAR + "\n"
            row = 0

    return string

# logo()
# Print the logo to the screen
def logo():
    print(getLogo())
