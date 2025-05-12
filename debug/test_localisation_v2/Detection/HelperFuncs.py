import cv2 as cv

def DisplayResizedImage(image, newSize : tuple, windowName : str) :

    temp = cv.resize(image, newSize)
    cv.imshow(windowName, temp)