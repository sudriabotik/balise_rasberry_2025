import cv2 as cv
import math

import numpy as np

import LineGraph
import HelperFuncs



class Settings :
	def __init__(self) :

		self.plankMinLength = 400
		self.plankMaxLength = 800
		self.negligibleLength = 20


"""

Use Canny to find the contours of the partially masked image

:param np.array image: The partially masked image
:param np.array mask: binary mask that was used to obscure the image

"""
def CreateContourImage(image, mask) :

	""" Since plank are red-ish, apply canny on the red channel """

	redChannel = cv.extractChannel(image, 2)

	redEdges = cv.Canny(redChannel, 5, 100)

	
	""" Also take edge from sudden changes in saturation """
	"""
	hsvImage = cv.cvtColor(image, cv.COLOR_BGR2HSV)
	saturation = cv.extractChannel(hsvImage, 2)

	saturationEdges = cv.Canny(saturation, 5, 40)


	edges = cv.bitwise_or(redEdges, saturationEdges)
	"""
	edges = redEdges

	""" Remove edges at the border that were likely caused by the transition from black to image """

	mask = cv.erode(mask, np.ones((3, 3)), iterations=2)
	edges = cv.bitwise_and(edges, mask)

	# cv.imshow("edges", edges)

	return edges


def GetContour(edges, image) :

	contours, _ = cv.findContours(edges, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

	contours = ApproxAllPolyDP(contours)

	graph = ConvertContoursFromCv(contours)

	"""

	drawnContours = cv.drawContours(image, contours, -1, color=[255, 0, 0], thickness=1)

	HelperFuncs.DisplayResizedImage(drawnContours, (800, 600), "raw contour")

	"""

	return graph

	

# obsolete
def DisplayContours(graph, image, color = [0, 255, 0], windowName = "contours", size = (800, 600)) :
	assert type(graph) == LineGraph.Graph

	contours = ConvertContoursToCv(graph)

	print(f"displaying contour of length {len(contours)}")

	drawnContours = cv.drawContours(image, contours, -1, color, thickness=1)

	#cv.imshow(windowName, drawnContours)
	HelperFuncs.DisplayResizedImage(drawnContours, size, windowName)


def CleanupContours(graph, settings) :
	assert type(graph) == LineGraph.Graph
	assert type(settings) == Settings

	LineGraph.Remove180Turns(graph)

	LineGraph.MergeByAngle(graph)

	LineGraph.MergePointsByDistance(graph, 5)

	LineGraph.CheckForDuplicateLines(graph)

	LineGraph.DeleteSegmentsByLength(graph, settings.negligibleLength)

	LineGraph.CleanUnusedPoints(graph) # likely there will be a lot of unused points by now

	LineGraph.BridgeGaps(graph, 0.1, 10) # seem to cause duplicate lines

	LineGraph.MergeByAngle(graph)

	LineGraph.DeleteSegmentsByLength(graph, settings.plankMinLength, settings.plankMaxLength)

	LineGraph.MergePointsByDistance(graph, 15)

	LineGraph.CleanUnusedPoints(graph)

	LineGraph.CheckForDuplicateLines(graph)

	return graph

# the less the score, the more chances the two parallel lines are from a plank
def FindPlanks(graph : LineGraph.Graph, maxScore = 50) :

	planks = []

	for i in range(graph.GetLenLines()) :

		line = graph.GetLine(i)

		bestLine, bestScore = LineGraph.FindBestParallelLine(graph, line)

		if bestScore >= maxScore :
			continue

		planks.append((line, bestLine))
	
	return planks


def DisplayPlanks(planks, image) :
	tempGraph = LineGraph.Graph()

	count = 0

	for plank in planks :
		tempGraph.AddLine(plank[0])
		tempGraph.AddLine(plank[1])
		count += 1
	
	print(f"displaying {count} planks")
	print(f"grah line : {tempGraph.GetLenLines()}")
	
	DisplayContours(tempGraph, image, color = [0, 0, 255])




""" Approximate all the contours (in opencv's format) """
def ApproxAllPolyDP(contours) :

	temp_contours = list(contours)

	for i in range(len(temp_contours)) :

		contour = temp_contours[i]

		contour = cv.approxPolyDP(contour, 10, False)

		temp_contours[i] = contour
	
	return temp_contours









""" ////// Functions that converts contours from a numpy array to classes /////// """

def ConvertContoursFromCv(contours) :

	graph = LineGraph.Graph()

	for contour in contours :

		if len(contour) <= 1 :
			continue

		""" openCV's contour has the points arrays in a seemingly useless array : [[20, 30]] ect"""

		start = graph.GetLenPoints()

		graph.NewPoint(int(contour[0][0][0]), int(contour[0][0][1]))
		

		for i in range(0, len(contour) - 1) :
			graph.NewPoint(int(contour[i+1][0][0]), int(contour[i+1][0][1]))

			graph.NewLine(graph.GetPoint(start + i), graph.GetPoint(start + i+1))
	
	print(f"Created new graph with {graph.GetLenPoints()} points and {graph.GetLenLines()} lines")

		
	return graph


def ConvertContoursToCv(graph) :

	contours = []

	for i in range(graph.GetLenLines()) :

		point1 = graph.GetLine(i).point1.ToArray()
		point2 = graph.GetLine(i).point2.ToArray()

		"""
		point1[0] = np.int32(point1[0])
		point1[1] = np.int32(point1[1])
		point2[0] = np.int32(point2[0])
		point2[1] = np.int32(point2[1])
		"""

		point1 = np.array(point1)
		point2 = np.array(point2)

		contours.append(np.array([[(point1), (point2)]]))
	contours = np.array(contours)

	return contours











def DebugDrawPoints(graph, image) :

	for i in range(graph.GetLenPoints()) :

		point = graph.GetPoint(i)

		image = cv.circle(image, (point.x, point.y), radius=0, color=(0, 0, 255), thickness=-1)
	
	#cv.imshow("debug points", image)
	#HelperFuncs.DisplayResizedImage(image, (800, 600), "debug points")