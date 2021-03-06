import threading
import cv2
import numpy as np
import base64
import queue

print("Running...")

thread_lock = threading.Lock()

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
        self.semaphore.acquire()
        thread_lock.acquire()
        self.queue.put(image)
        thread_lock.release()

    def get_image(self):
        # Check before that its empty when retrieving images.
        self.semaphore.release()
        thread_lock.acquire()
        image = self.queue.get()
        thread_lock.release()
        
        return image


# Contains color images. 
image_consumer = imageQueue(10)

# Contains grayscale images.
image_producer = imageQueue(10)

def extract_frames():
    count = 0

    vid_cap = cv2.VideoCapture("clip.mp4")

    # read first image
    success, image = vid_cap.read()

    while success and count < 9999:
        success, jpg_image = cv2.imencode('.jpg', image)

        jpg_as_text = base64.b64encode(jpg_image)
        
        # Add to queue
        image_consumer.add_image(image)

        success, image = vid_cap.read()
        count += 1

    print("Finished extracting images")
    image_consumer.add_image(None)


def convert_images_to_grayscale():
    while True:
        if image_consumer.is_empty():
            continue
        
        color_image = image_consumer.get_image()

        if color_image is None:
            break

        grayscale_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        image_producer.add_image(grayscale_image)

    print("Finished converting images")
    image_producer.add_image(None)

def display_images():
    while True:
        if image_producer.is_empty():
            continue

        image = image_producer.get_image()

        if image is None:
            break

        cv2.imshow("Eddie's Video", image)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

    print("Finished displaying images")

extract_thread = threading.Thread(target=extract_frames)
grayscale_thread = threading.Thread(target=convert_images_to_grayscale)
display_thread = threading.Thread(target=display_images)

extract_thread.start()
grayscale_thread.start()
display_thread.start()
