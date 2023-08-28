# import libraries
import cv2
import time
import os


# Process the captured image, first convert to grayscale, then apply Gaussian blur.
def get_processedImage(image_ndarray):
    image_ndarray_1 = cv2.cvtColor(image_ndarray, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur to the image to avoid the impact of small changes in brightness, vibration, etc. on the effect.
    filter_size = 21
    image_ndarray_2 = cv2.GaussianBlur(image_ndarray_1, (filter_size, filter_size), 0)
    return image_ndarray_2


# Get the string representation of the current time
import time


def get_timeString():
    now_timestamp = time.time()
    now_structTime = time.localtime(now_timestamp)
    timeString_pattern = '%Y %m %d %H:%M:%S'
    now_timeString = time.strftime(timeString_pattern, now_structTime)
    return now_timeString


# Based on the difference between two images, draw a box and date and time on the second image.
def get_drawedDetectedImage(first_image_ndarray, second_image_ndarray):
    if second_image_ndarray is None or first_image_ndarray is None:
        return None
    first_image_ndarray_2 = get_processedImage(first_image_ndarray)
    second_image_ndarray_2 = get_processedImage(second_image_ndarray)
    # cv2.absdiff to calculate the absolute value of the difference between two images
    absdiff_ndarray = cv2.absdiff(first_image_ndarray_2, second_image_ndarray_2)
    # cv2.threshold performs image dilation
    threshold_ndarray = cv2.threshold(absdiff_ndarray, 25, 255, cv2.THRESH_BINARY)[1]
    # cv2.dilate findContours finds contours in the image
    dilate_ndarray = cv2.dilate(threshold_ndarray, None, iterations=2)
    # cv2.findContours finds contours in the image
    contour_list = cv2.findContours(threshold_ndarray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    copy_image_ndarray = second_image_ndarray.copy()
    height, width, _ = copy_image_ndarray.shape
    contour_minArea = int(height * width * 0.001)
    for contour in contour_list:
        if cv2.contourArea(contour) < contour_minArea:
            continue
        else:
            x1, y1, w, h = cv2.boundingRect(contour)
            x2, y2 = x1 + w, y1 + h
            leftTop_coordinate = x1, y1
            rightBottom_coordinate = x2, y2
            bgr_color = (0, 0, 255)
            thickness = 2
            cv2.rectangle(copy_image_ndarray, leftTop_coordinate, rightBottom_coordinate, bgr_color, thickness)
            time_string = get_timeString()
            text = 'Moving object detected at %s! x=%d, y=%d' % (time_string, x1, y1)
            print(text)
    time_string = get_timeString()
    bgr_color = (0, 0, 255)
    thickness = 2
    cv2.putText(copy_image_ndarray, time_string, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, bgr_color, thickness)
    return copy_image_ndarray


# Main function
from sys import exit

if __name__ == '__main__':
    cameraIndex = 0
    # Instantiate a video stream object
    camera = cv2.VideoCapture(cameraIndex)
    is_successful, first_image_ndarray = camera.read()
    if not is_successful:
        print(
            "The camera is not successfully connected, possible reasons: 1. The camera does not support direct calling from the cv2 library; 2. If there are multiple cameras, set the correct cameraIndex.")
        exit()
    while True:
        is_successful, second_image_ndarray = camera.read()
        windowName = 'cv2_display'
        drawed_image_ndarray = get_drawedDetectedImage(first_image_ndarray, second_image_ndarray)
        cv2.imshow(windowName, drawed_image_ndarray)
        # After showing the image, wait for 1 second and receive key presses
        pressKey = cv2.waitKey(1)
        # Pressing Esc or q will exit the loop
        if 27 == pressKey or ord('q') == pressKey:
            cv2.destroyAllWindows()
            break
        # Over time, the current frame becomes the previous frame for the next frame
        first_image_ndarray = second_image_ndarray
        # Release the camera
    camera.release() 