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
import threading
import _thread
import queue
import random
#https://www.safaribooksonline.com/library/view/python-cookbook/0596001673/ch09s07.html
#https://stackoverflow.com/questions/13481276/threading-in-python-using-queue
#https://www.troyfawkes.com/learn-python-multithreading-queues-basics/

q = queue

class Threads(threading.Thread, q):
    def _init_(self, q):
        threading.Thread._init_(self)
        self.queue = q
        
    def run(self):
        while True:
            self.q.get()
            self.q.task_done()

start = time.time()

def main():
        for i in range(10):
            t = Threads()
            t.setDaemon(True)
            t.start()
            q.join()



class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print("Got file change from watcher")
        displayFrame.updateImage()
        
def watcherThread():
    
    wm = pyinotify.WatchManager()
    wm.add_watch('/home/pi/spibox/capture/primout', pyinotify.IN_CREATE, rec = True, auto_add = True)
    notifier = pyinotify.Notifier(wm, EventHandler())
    
    print("Starting watch")
    notifier.loop()
#_thread.start_new_thread(watcherThread, ())




def startPrimitive():
    if not pirActive:
    
        print("Primitive started")
        #subprocess.call('/home/pi/go/bin/primitive -i /home/pi/spibox/capture/spi_output_1.png -o /home/pi/spibox/capture/primout/primitive_output%d.png -nth 5 -s 256 -n 100', shell=True )
        print("Primitive completed")
        #Starts Primitive and outputs picture
        pirActive = False




class DisplayFrame:
    
    root = Tk()
    
    def _init_(self, master, queue):
        self.queue = queue
        Frame._init_(self)
        #w, h = 700, 700
        self.grid()
        
    def displayPicture(self):
        print('Building display frame')
        
        self.img1 = PhotoImage(file = '/home/pi/spibox/capture/spi_output_1.png')
        self.img1Label = Label(image = self.img1, width = 256, height = 256)
        self.img1Label.grid(row = "1")
        #Top image, doesn't change
    
        self.text = Text(fg = "White", bg = "Red", bd = 5, width = 35, height = 1)
        self.text.insert(INSERT, "Maryville Cyber Fusion Center")
        self.text.tag_configure("center", justify = "center")
        self.text.tag_add("center", 1.0, "end")
        self.text.grid(row = "2")
        #Middle banner with text
    
        self.img2 = PhotoImage(file = '/home/pi/spibox/capture/loading.png')
        self.img2Label = Label(image = self.img2, bg = "Black", width = 256, height = 256)
        self.img2Label.grid(row = "3")
        #Bottom image
        
        main()
        q.put(watcherTread())
        #_thread.start_new_thread( watcherThread, () )
        #_thread.start_new_thread( startPrimitive, () )
        #print("after start watcherThread")
        DisplayFrame.root.mainloop()
        print("after starting tkinter main loop")
        
        
    def updateImage(self):
        print("Bottom image should update")
        
        fileList = glob.glob('/home/pi/spibox/capture/primout/*')
        latestFile = max(fileList, key = os.path.getctime)
        print(latestFile)
        
        self.img3 = PhotoImage(file = latestFile)
        self.img2Label.configure(image = self.img3)
        self.img2Label.image = self.img3
        #Updates bottom image (img 2)
        
displayFrame = DisplayFrame()




def get_file_name() -> str:
    return 'spi_output'    
    #Names picture file output

PIR = 4
def photo():
    for i in range(1,2):
        capturename = get_file_name()
        print('Motion detected! Taking snapshot')
        cmd="raspistill -w 256 -h 256 -n -t 10 -q 10 -e png -th none -o /home/pi/spibox/capture/" + capturename+"_%d.png" % (i)
        camerapid = subprocess.call(cmd,shell=True)
        displayFrame.displayPicture()
        #Takes picture
        #Opens display frame

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR, GPIO.IN, GPIO.PUD_DOWN)

try:
    print ("Turning on motion sensor")
 
    # Loop until PIR indicates nothing is happening
    while GPIO.input(PIR)==1:
        Current_State  = 0
 
    print ("Sensor ready")
 
    while True:
        print('Waiting for movement')
        GPIO.wait_for_edge(PIR,GPIO.RISING)
        photo()

except KeyboardInterrupt:
    print ("Bye for now")
    # Reset GPIO
    GPIO.cleanup()