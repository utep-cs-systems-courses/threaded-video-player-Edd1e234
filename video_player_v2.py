import threading
import cv2
import numpy as np
import base64
import queue
import time

print("Running...")

thread_lock = threading.Lock()
AMOUNT = 10
FILE_NAME = "clip.mp4"
MAX_FRAMES = 9999

class imageQueue():
    def __init__(self, amount):
        self.semaphore = threading.Semaphore(amount)
        self.queue = queue.Queue()

    def is_empty(self):
        thread_lock.acquire()
        queue_empty = self.queue.empty()
        thread_lock.release()
        
        return queue_empty

    def add_image(self, image):
        # Sub from slots, add to the image
        self.semaphore.acquire()
        thread_lock.acquire()
        self.queue.put(image)
        thread_lock.release()

    def get_image(self):
        # Add to slots, pop image
        self.semaphore.release()
        thread_lock.acquire()
        image = self.queue.get()
        thread_lock.release()
        
        return image


# Contains color images. 
image_consumer = imageQueue(AMOUNT)
image_producer = imageQueue(AMOUNT)

def extract_frames():
    count = 0

    vid_cap = cv2.VideoCapture(FILE_NAME)

    # read first image
    success, image = vid_cap.read()

    while success and count < MAX_FRAMES:
        success, jpg_image = cv2.imencode('.jpg', image)

        # Not needed. 
        jpg_as_text = base64.b64encode(jpg_image)
        
        # Add to queue
        image_consumer.add_image(image)

        success, image = vid_cap.read()
        count += 1

    print("Exiting extract thread")
    image_consumer.add_image(None)


def convert_images_to_grayscale():
    while True:
        # Frames have not been loaded 
        if image_consumer.is_empty():
            continue
        
        color_image = image_consumer.get_image()

        # No more frames
        if color_image is None:
            break

        grayscale_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        image_producer.add_image(grayscale_image)

    print("Exiting grayscale thread")
    image_producer.add_image(None)

def display_images():
    while True:
        # Frames have not been loaded
        if image_producer.is_empty():
            continue

        image = image_producer.get_image()

        # No more frames
        if image is None:
            break

        cv2.imshow("Eddie's Video", image)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

    print("Exiting display thread")

# Threads
extract_thread = threading.Thread(target=extract_frames)
grayscale_thread = threading.Thread(target=convert_images_to_grayscale)
display_thread = threading.Thread(target=display_images)

extract_thread.start()
grayscale_thread.start()
display_thread.start()

# Destroy all objects properly, final thread should be the main
while display_thread.is_alive():
    time.sleep(1)

print("Exiting main thread")




