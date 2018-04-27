import time
import sys
import datetime
import subprocess
import os
import RPi.GPIO as GPIO
import glob
import os
import tkinter
import tkinter as Tk
from tkinter import *
from PIL import *
import pyinotify
from threading import Thread
import _thread
import queue



#Set queue
def processes(q):
    print('running processes')
    while True:
        if not q.empty():
            f = q.get()
            f()
            q.task_done()
            print('Task complete')



#Starts primitive and outputs image iterations
def startPrimitive():
        print("Primitive started")
        #subprocess.call('/home/pi/go/bin/primitive -i /home/pi/spibox/capture/spi_output_1.png -o /home/pi/spibox/capture/primout/primitive_output%d.png -nth 5 -s 256 -n 100', shell=True )
        print("Primitive completed")



#GUI parameters and funcs to build GUI
class DisplayFrame:
    
    root = Tk()
    
    def _init_(self, master, q):
        self.q = q
        Frame._init_(self)
        #w, h = 700, 700
        self.grid()
    
    #May use this to help refresh latestFile within displayPicture
    def imageFinder():
        latestFile = max(glob.glob('/home/pi/spibox/capture/primout/*'), key = os.path.getctime)
        return latestFile
        
    #Builds the GUI picture frame
    def displayPicture(self):
        print('Building display frame')
        
        #Top image
        self.img1 = PhotoImage(file = '/home/pi/spibox/capture/spi_output_1.png')
        self.img1Label = Label(image = self.img1, width = 256, height = 256)
        self.img1Label.grid(row = "1")
        
        #Middle text banner
        self.text = Text(fg = "White", bg = "Red", bd = 5, width = 35, height = 1)
        self.text.insert(INSERT, "Maryville Cyber Fusion Center")
        self.text.tag_configure("center", justify = "center")
        self.text.tag_add("center", 1.0, "end")
        self.text.grid(row = "2")
        
        #Need to find a way for this to update
        while True:
            latestFile = max(glob.glob('/home/pi/spibox/capture/primout/*'), key = os.path.getctime)
            print(latestFile)
            break
        
        #Bottom image
        self.img2 = PhotoImage(file = latestFile)
        self.img2Label = Label(image = self.img2, bg = "Black", width = 256, height = 256)
        self.img2Label.grid(row = "3")
        
        DisplayFrame.root.mainloop()
        print("Tkinter main loop ended")
        main()
        
    #Try to update img2 
    def updateImage(self):
        displayFrame = DisplayFrame()
        
        #latestFile = max(glob.glob('/home/pi/spibox/capture/primout/*'), key = os.path.getctime)
        #print(latestFile)
        #self.img2 = PhotoImage(file = latestFile)
        #self.img2Label.configure(image = self.img2)
        
        print("Bottom image should update")
        displayFrame.displayPicture()



#EventHandler, watcherThread set up watcher via pyinotify  
class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        displayFrame = DisplayFrame()
        print("Got file change from watcher")
        displayFrame.updateImage()
        
    def _init_(self, q):
        self.q = q



def watcherThread():
    displayFrame = DisplayFrame()
    
    print("Starting watch")
    wm = pyinotify.WatchManager()
    wm.add_watch('/home/pi/spibox/capture/primout', pyinotify.IN_CREATE, rec = True, auto_add = True)
    notifier = pyinotify.Notifier(wm, EventHandler())
    notifier.loop()



#Names initial picture output
def get_file_name() -> str:
    return 'spi_output'    
 

#Takes photo, calls TK
def photo(displayFrame, q):
    for i in range(1,2):
        capturename = get_file_name()
        print('Motion detected! Taking snapshot')
        cmd="raspistill -w 256 -h 256 -n -t 10 -q 10 -e png -th none -o /home/pi/spibox/capture/" + capturename+"_%d.png" % (i)
        camerapid = subprocess.call(cmd,shell=True)
        q.put(startPrimitive)
        displayFrame.displayPicture()
        

 
#Motion sensor start up
def start_motion_sensor(pir_pin):
    print ("Turning on motion sensor")
    while GPIO.input(pir_pin)==1:
        Current_State = 0
    print ("Sensor ready")


#Detects motion 
def wait_for_motion(PIR, displayFrame, q):
    while True:
        print("Waiting for movement")
        GPIO.wait_for_edge(PIR,GPIO.RISING)
        photo(displayFrame, q)


#Starts threaded processes and main loop
def main():
    PIR = 4
    q = queue.Queue(maxsize = 5)
    q_threads = 1
    displayFrame = DisplayFrame()
    
#maybe declare latestFile here and pass into disPic?
    
    for i in range(q_threads):
        t1 = Thread(target = processes, args = (q,))
        t2 = Thread(target = watcherThread)
        t1.setDaemon(True)
        t2.setDaemon(True)
        t1.start()
        t2.start()
    q.join()
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR, GPIO.IN, GPIO.PUD_DOWN)
    
    while True:
        try:
            start_motion_sensor(PIR)
            wait_for_motion(PIR, displayFrame, q)
        
        except KeyboardInterrupt:
            print ("Bye for now")
            # Reset GPIO
            GPIO.cleanup()
        
    
    
if __name__ == '__main__':
    main()


#https://www.tutorialspoint.com/python3/python_multithreading.htm