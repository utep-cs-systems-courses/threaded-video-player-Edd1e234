#!/usr/bin/env python3

from threading import Thread
import threading
import cv2
import numpy as np
import base64
import queue

thread_lock = threading.Lock()
frame_buffer = []

class ExtractFrames(Thread):
    def __init__(self, file_name):
        Thread.__init__(self)
        self.vidcap = cv2.VideoCapture(file_name)

    def run(self, max_frames_to_load=72):
        print("Running Extract Frames")

        # Initialize frame count
        count = 0

        success, image = self.vidcap.read()
        while success and count < max_frames_to_load:
            # Get a jpg encoded frame
            success, jpg_image = cv2.imencode('.jpg', image)

            # Encode the frame as base 64 to make debugging easier
            jpg_as_text = base64.b64encode(jpg_image)            

            # Add the frame to the buffer, lock threads...
            thread_lock.acquire()
            frame_buffer.append(image)
            thread_lock.release()

            success, image = self.vidcap.read()

            count += 1

        # None signals there is no more frames to parse. 
        thread_lock.acquire()
        frame_buffer.append(None)
        thread_lock.release()
        print("Finished reading images")

class DisplayFrames(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print("Runing display frames")

        # Initialize frame count
        count = 0

        # Go through each frame in the buffer until the buffer is empty.
        while 1:
            print("Enter the top")
            
            # Should never be empty....
            thread_lock.acquire()
            if len(frame_buffer) is 0:               
                thread_lock.release()
                continue

            # If None queue is empty. 
            if frame_buffer[0] is None:
                thread_lock.release()
                break
            thread_lock.release()
            
            # Get next frame.
            thread_lock.acquire()
            print("Get Frame")
            frame = frame_buffer.pop(0)
            thread_lock.release()

            # Display the image in a window called "video" and wait before
            # displaying the next frame

            cv2.imshow("Eddie's Video", frame)
            if cv2.waitKey(42) and 0xFF == ord("q"):
                break
            count += 1

        print("Finished displaying all frames")

        # Cleanup the windows
        cv2.destroyAllWindows()

file_name = 'clip.mp4'
extract_frames = ExtractFrames(file_name)
display_frames = DisplayFrames()

extract_frames.start()
display_frames.start()
