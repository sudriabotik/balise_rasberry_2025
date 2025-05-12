import cv2 as cv

import numpy as np

import HelperFuncs


upper_hsv = np.array([50, 255, 255])
lower_hsv = np.array([0, 50, 50])



def NoiseReduction(image) :

	return cv.GaussianBlur(image, 3, 0, 0)


""" Take a color image, find the areas of interest that contains the hsv color we seek, 
then return the image with all the unintresting parts blacked out """

def FindAreaOfInterest(image) :

	hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

	mask = cv.inRange(hsv, lower_hsv, upper_hsv)

	#cv.imshow("mask", mask)


	""" Erode to remove some noise, then inflate it to get the general area """

	kernel = np.ones((3, 3))
	kernel2 = np.ones((5, 5))

	mask = cv.erode(mask, kernel, iterations=6)
	mask = cv.dilate(mask, kernel2, iterations=20)

	#cv.imshow("area mask", mask)

	""" In order to apply bitwise_and to the original image, the mask must have the same dimensions (3 channels) """
	bgrmask = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)

	""" Make all uninterest"""
	masked_image = cv.bitwise_and(image, bgrmask)

	#cv.imshow("masked image", masked_image)
	HelperFuncs.DisplayResizedImage(masked_image, (800, 600), "masked image")

	masked_image = cv.GaussianBlur(masked_image, (5, 5), 0, 0)

	return masked_image, mask


# mask should be rgb, even if it is a binary operation
def ApplyMask(image, mask) :

	masked_image = cv.bitwise_and(image, mask)

	return masked_image