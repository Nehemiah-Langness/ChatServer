import threading
from sys import stdin
from time import sleep

def readInput(callback):
    while (True):
        userInput = stdin.readline()
        callback(userInput)

def startReader(callback):
    if (not callable(callback)):
        raise Exception("Callback is not a function")
    
    reader = threading.Thread(target=readInput, args=(callback,))
    reader.setDaemon(True)
    reader.start()

def printInput(text):
    print(text.lower())

def main():
    startReader(printInput)
    sleep(15)

if (__name__ == "__main__"):
    main()
