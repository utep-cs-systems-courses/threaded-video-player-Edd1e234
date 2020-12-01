import threading
import cv2
import numpy as np
import base64
import queue

MAX = 10
DEBUG = True

# Blocking queue
class ImageQueue:
    def __init__(self, amount):
        self.thread_lock = threading.Lock()
        self.queue = []
        self.empty = threading.Semaphore(amount)
        self.full = threading.Semaphore(0)

    def put_image(self,image):
        
        # if 0, block until consumer release.
        # if 0, does not have room
        self.empty.acquire()
        self.thread_lock.acquire()
        self.queue.append(image)
        self.thread_lock.release()

        # Increments by 1
        self.full.release()

    def get(self):
        # if 0, block until release is called.
        # if 0, is empty
        self.full.acquire()
        self.thread_lock.acquire()
        image = self.queue.pop(0)
        self.thread_lock.release()

        # Makes room
        self.empty.release()
        return image

# color
image_consumer = ImageQueue(MAX)

# grayscale
image_producer = ImageQueue(MAX)

def extract_frames():
    count = 0

    vid_cap = cv2.VideoCapture("clip.mp4")

    # read first image
    success, image = vid_cap.read()

    while success and count < 9999:
        success, jpg_image = cv2.imencode(".jpg", image)

        # print("Extract")

        # Add to queue
        image_consumer.put_image(image)

        success, image = vid_cap.read()
        count += 1

    print("Finished extracting images")
    image_consumer.put_image(None)


def convert_images_to_grayscale():
    while True:
        # print("Grayscale")
        color_image = image_consumer.get()

        if color_image is None:
            break

        grayscale_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        image_producer.put_image(grayscale_image)
        
    print("Finished converting images")
    image_producer.put_image(None)


def display_images():
    while True:
        # print("Display")
        image = image_producer.get()

        if image is None:
            break

        cv2.imshow("Eddie's Video", image)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

    print("Finished displaying images")


extract_thread = threading.Thread(target=extract_frames)
convert_to_grayscale_thread = threading.Thread(target=convert_images_to_grayscale)
display_thread = threading.Thread(target=display_images)

extract_thread.start()
convert_to_grayscale_thread.start()
display_thread.start()

