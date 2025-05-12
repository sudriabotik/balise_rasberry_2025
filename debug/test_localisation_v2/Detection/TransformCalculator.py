import cv2 as cv
import numpy as np

class BoardTransformSettings :

    def __init__(self) :

        # the pixel density of the final image in terms of the board coordinates
        self.coordPerPixels = 2

        # the size of the board portion that will appear
        self.boardSize = np.array([1000, 1000])

        # the coordinates at which the board starts in the final image, without taking into account the padding
        self.offsetCoords = np.array([0, 0])
        

""" points should be in the order : top left, bottom left, bottom right, top right (in the board coordinates) (not sure the order is important)"""
def GeneratePerspectiveMatrix(settings : BoardTransformSettings, pointsPxPos : np.ndarray, pointsBoardPos : np.ndarray) :

    # the position position relative to the coordinate offset
    pointsLocalBoardPos = np.float32([np.subtract(pointBoardPos, settings.offsetCoords) for pointBoardPos in pointsBoardPos])

    dstPoints = np.array([
        pointsLocalBoardPos[0],
        pointsLocalBoardPos[1],
        pointsLocalBoardPos[2],
        pointsLocalBoardPos[3]
    ])

    print(dstPoints)
    for i in range(len(dstPoints)) : dstPoints[i] = [dstPoints[i][0] / settings.coordPerPixels, dstPoints[i][1] / settings.coordPerPixels]
    print(dstPoints)
    

    matrix = cv.getPerspectiveTransform(pointsPxPos, dstPoints)

    return matrix, dstPoints


def WarpImagePerspective(settings : BoardTransformSettings, matrix : np.matrix, image) :

    warpedImage = cv.warpPerspective(image, matrix, settings.boardSize // settings.coordPerPixels)

    return warpedImage

