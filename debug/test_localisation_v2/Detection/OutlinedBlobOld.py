import cv2 as cv
import math

import numpy as np


upper_hsv = np.array([40, 255, 250])
lower_hsv = np.array([5, 100, 100])


def NoiseReduction(image) :

	return cv.GaussianBlur(image, 3, 0, 0)

""" Take a color image and return a binary mask with the colors we are interested in """
def FindAreaOfInterest(image) :

	hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

	mask = cv.inRange(hsv, lower_hsv, upper_hsv)

	cv.imshow("mask", mask)

	""" Erode to remove some noise, then inflate it to get the general area """

	kernel = np.ones((3, 3))
	kernel2 = np.ones((5, 5))

	mask = cv.erode(mask, kernel, iterations=6)

	mask = cv.dilate(mask, kernel2, iterations=20)

	cv.imshow("area mask", mask)

	bgrmask = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)


	masked_image = cv.bitwise_and(image, bgrmask)

	cv.imshow("masked image", masked_image)

	masked_image = cv.GaussianBlur(masked_image, (5, 5), 0, 0)

	return masked_image, mask


def GetContours(image, mask) :

	#greyScale = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
	redChannel = cv.extractChannel(image, 2)

	edges = cv.Canny(redChannel, 1, 100)

	""" Remove adges at the border that were likely caused by the transition from black to image """

	mask = cv.erode(mask, np.ones((3, 3)), iterations=2)

	print(edges.shape)
	print(mask.shape)

	#mask = cv.colorChange(mask, cv.COLOR_BGR2GRAY)
	edges = cv.bitwise_and(edges, mask)

	cv.imshow("edges", edges)

	contours, _ = cv.findContours(edges, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

	drawnContours = cv.drawContours(image, contours, -1, color=[0, 0, 255], thickness=1)

	contours = list(contours)


	""" Contour simplification"""

	print("approximating contours")
	contours = ApproxAllPolyDP(contours)

	contours = SimplifyContours(contours, 40)

	points, lines = PointsAndLinesFromContours(contours)

	print("merge colinear")
	ConnectColinearLines(points, lines)

	points, lines = MergePointsByDistance(points, lines, threshold=10)

	print("merge line by angles")
	#MergeLinesByAngle(points, lines, 10 / 180 * math.pi)

	

	contours = ContoursFromPointsAndLines(points, lines)


	contours = SimplifyContours(contours, 50)
	

	print("drawing now")
	
	drawnContours = cv.drawContours(image, contours, -1, color=[0, 255, 0], thickness=1)

	cv.imshow("contours", drawnContours)
	
	print(contours[0])

""" Return an array of points and an array of point indexes representing lines from openCV's array of contours """
def PointsAndLinesFromContours(contours) :

	points = []
	lines = []

	for contour in contours :

		if len(contour) <= 1 :
			continue

		""" openCV's contour has the points arrays in a seemingly useless array : [[20, 30]] ect"""
		points.append(contour[0][0])

		for x in range(1, len(contour)) :
			points.append(contour[x][0])
			lines.append([len(points) - 2, len(points) - 1])
		
	return points, lines


def ApproxAllPolyDP(contours) :

	temp_contours = list(contours)

	for i in range(len(temp_contours)) :

		contour = temp_contours[i]

		contour = cv.approxPolyDP(contour, 10, False)

		temp_contours[i] = contour
	
	return temp_contours



""" Reverse of the above function """
def ContoursFromPointsAndLines(points, lines) :

	contours = []

	for line in lines :
		if line == [-1, -1] :
			continue
		contours.append(np.array([[points[line[0]]], [points[line[1]]]]))
	linesToRemove = []
	contours = np.array(contours)

	return contours

def SimplifyContours(contours, minLineLength = 50) :

	index = 0

	print(f"simplifying contours {len(contours)}")

	contours = list(contours)

	while index < len(contours) :

		
	
		contour = list(contours[index])

		x = 0
		while x < len(contour) - 1 :

			segmentLen = math.sqrt(math.pow(contour[x][0][0] - contour[x + 1][0][0], 2) + math.pow(contour[x][0][1] - contour[x + 1][0][1], 2))
			
			""" In this case the line segment is too short to be worth keeping """
			if segmentLen < minLineLength :
				contour.pop(x+1)
				continue

			x += 1
		
		


		
		if len(contour) <= 1 :
			contours.pop(index)
			continue

		contours[index] = np.array(contour)

		index += 1
	
	print("done simplifying")

	#contours = np.array(contours)
	
	return contours


def MergePointsByDistance(points : list, lines : list, threshold = 5) :

	remapSrc = []
	remapDst = []

	removalIndexes = []

	thresholdSquare = threshold ** 2

	print("started merging points")
	print(len(points))

	i = 0
	while i < len(points) - 1 :

		j = i + 1

		while j < len(points) :

			if (points[j][0] - points[i][0])**2 + (points[j][1] - points[i][1])**2 < thresholdSquare :

				remapSrc.append(j)
				remapDst.append(i)
			
			j += 1
		
		i += 1
	

	""" The list of points stay full of garbage points """
	"""
	for index in remapSrc :
		points.pop(index)
	"""

	""" Now remap the lines to all points that got merged """
	for i in range(len(lines)) :

		if lines[i][0] in remapSrc :
			lines[i][0] = remapDst[remapSrc.index(lines[i][0])]
		
		if lines[i][1] in remapSrc :
			lines[i][1] = remapDst[remapSrc.index(lines[i][1])]
	
	print("done merging points")
	
	return points, lines


def ConnectColinearLines(points, lines, directionThreshold = 0.05, positionThreshold = 10, maxDistance = 200) :

	

	for i in range(len(lines) - 1) :

		line1 = lines[i]

		for j in range(i + 1, len(lines)) :

			line2 = lines[j]

			line1dir = GetLineDirection(points, line1)
			line2dir = GetLineDirection(points, line2)

			#print(f"dir diff {abs(line1dir - line2dir)}")
			if (abs(line1dir - line2dir) > directionThreshold) :
				continue

			#print(f"pos diff {abs(GetLineElevation(points, line1, line1dir) - GetLineElevation(points, line2, line2dir))}")
			if (abs(GetLineElevation(points, line1, line1dir) - GetLineElevation(points, line2, line2dir)) > positionThreshold) :
				continue

			""" Find the two farthest away points """

			
			
			point1 = points[line1[0]]
			point2 = points[line2[0]]
			minDist = 99999
			maxDist = 0
			for pointTest1 in line1 :
				for pointTest2 in line2 :
					dist = GetDistance(points[pointTest1], points[pointTest2])

					if dist > maxDist :
						maxDist = dist
					
					if dist < minDist :
						point1 = pointTest1
						point2 = pointTest2
						minDist = dist
			
			if minDist > maxDistance :
				continue

			print("merge")

			lines.append([point1, point2])
	


def FindLinesConnectedToPoint(lines, pointIndex) :

	results = []
	print(f"searching for {pointIndex}")

	for i in range(len(lines)) :
		if pointIndex in lines[i] :
			print(f"added {lines[i]}")
			results.append(i)
	
	return results

def GetOppositePoint(line, pointIndex) :
	if line[0] == pointIndex :
		return line[1]
	else :
		return line[0]



def MergeLinesByAngle(points, lines, maxAngle = 0.1) :

	print(f"merging line by angle for {len(points)} points and {len(lines)} lines")	

	

	for i in range(len(points)):

		linesToAdd = []

		attachedLines = FindLinesConnectedToPoint(lines, i)

		if len(attachedLines) <= 1 :
			continue

		for x in range(len(attachedLines) - 1) :
			for y in range(x+1, len(attachedLines)) :

				""" ignore dummy lines """

				if lines[attachedLines[x]] == [-1, -1] or lines[attachedLines[y]] == [-1, -1] :
					continue

				dir1 = GetLineDirection(points, lines[attachedLines[x]])
				dir2 = GetLineDirection(points, lines[attachedLines[y]])

				if (abs(dir1 - dir2) < maxAngle) :

					print(f"merge by angle : {lines[attachedLines[x]]} and {lines[attachedLines[y]]}")

					""" merge the lines"""
					linesToAdd.append([GetOppositePoint(lines[attachedLines[x]], i), GetOppositePoint(lines[attachedLines[y]], i)])

					""" turns the first line into a dummy line """

					lines[attachedLines[x]] = [-1, -1]

					""" turns the second line into a dummy line """

					lines[attachedLines[y]] = [-1, -1]
		
		lines += linesToAdd

		

		


def GetLineDirection(points, line) :

	point1 = points[line[0]]
	point2 = points[line[1]]

	deltaX = abs(point2[0] - point1[0])
	deltaY = abs(point2[1] - point1[1])

	if (deltaX == 0) :
		return math.pi/2
	
	return math.atan(deltaY/deltaX)


def GetLineElevation(points, line, dir) :

	return points[line[0]][1] * math.cos(dir) - points[line[0]][0] * math.sin(dir)


def GetDistance(point1, point2) :

	return math.sqrt( (point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 )