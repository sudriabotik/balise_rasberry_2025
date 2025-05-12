import cv2 as cv
import numpy as np

import OutlinedBlobOld as OutlinedBlobOld
import AreaFinder
import PlankOutliner

import TransformCalculator

img = "Samples/IMG_7238.jpg"

img = cv.imread(img)

originalImageShape = img.shape
adjustedDimension = (img.shape[1] // 3, img.shape[0] // 3)

img = cv.resize(img, adjustedDimension)

#cv.imshow("original", img)

manualMask = cv.imread("Samples/IMG_7238_MASK.jpg")
manualMask = cv.resize(manualMask, adjustedDimension)

img = AreaFinder.ApplyMask(img, manualMask)


maskedImage, mask = AreaFinder.FindAreaOfInterest(img)

edges = PlankOutliner.CreateContourImage(maskedImage, mask)

graph = PlankOutliner.GetContour(edges, maskedImage)

matrix = [[-1.3555123745161954,-3.5198608172223507,2474.789539871236],
[0.6166758677006765,-5.241246362554725,2400.0280532163742],
[-0.0001552378527276072,-0.003591894762254132,1.0]]

matrix = np.array(matrix)

graph.ApplyMatrixTransform(matrix)


# draw the warped image for visualisation and debugging, make sure the settings are the same than the ones the matrix was created with
settings = TransformCalculator.BoardTransformSettings()
settings.coordPerPixels = 2
settings.boardSize = np.array([2500, 2500])
settings.offsetCoords = np.array([-400, -400])
warpedImage = TransformCalculator.WarpImagePerspective(settings, matrix, img)
PlankOutliner.DisplayContours(graph, warpedImage, color=[200, 0, 0], windowName="warpedContours")


settings = PlankOutliner.Settings()
settings.plankMinLength = 80
settings.plankMaxLength = 200
settings.negligibleLength = 15

graph = PlankOutliner.CleanupContours(graph, settings)

PlankOutliner.DisplayContours(graph, warpedImage, size=(warpedImage.shape[1], warpedImage.shape[0]))
PlankOutliner.DebugDrawPoints(graph, warpedImage)

planks = PlankOutliner.FindPlanks(graph, 20)
PlankOutliner.DisplayPlanks(planks, warpedImage)


cv.imshow("final", warpedImage)

cv.waitKey(0)