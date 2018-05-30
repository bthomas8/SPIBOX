# SPIBOX 
This repository contains a program built upon a Raspberry-Pi SPIBOX script with the following functionality:
-Allow the SPIBOX to capture pictures via PIR motion sensing
-Folder monitoring
-Store picture in monitored folder
-Display original picture in top frame of a 2 frame Tkinter GUI
-Send the picture to Primitive for processing
-Update bottom picture frame (of GUI) with processed image iterations
-Terminate GUI when processing is complete and restart process

Incorporates file monitoring via pyinotify, multi-threading, queues, Tkinter, and Primitive image processing (GO language).
