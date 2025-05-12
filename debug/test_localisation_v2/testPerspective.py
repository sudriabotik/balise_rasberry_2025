import Detection.TransformCalculator as TransformCalculator

import cv2 as cv
import numpy as np

img = cv.imread("Samples/IMG_7238.jpg")
img = cv.resize(img, (img.shape[1] // 3, img.shape[0] // 3)) # resize for faster processing ?? 

points_image_src = [
    
    [2250, 2040],
    [1890, 2375],
    [1000, 2136],
    [1460, 1890]
    
]

points_image_src = np.array(points_image_src)
points_image_src = points_image_src // 3 # resize for faster processing ??
points_image_src = np.float32(points_image_src)

points_image_redresser = [
    [800, 500],
    [800, 1000],
    [200, 1000],
    [200, 500]
]

points_image_redresser = np.array(points_image_redresser)
points_image_redresser = np.float32(points_image_redresser)

settings = TransformCalculator.BoardTransformSettings()
settings.coordPerPixels = 2
settings.boardSize = np.array([2500, 2500])
settings.offsetCoords = np.array([-400, -400])

mat, dst = TransformCalculator.GeneratePerspectiveMatrix(settings, pointsBoardPos=points_image_redresser, pointsPxPos=points_image_src)

warped = TransformCalculator.WarpImagePerspective(settings, mat, img)

for i in range(len(dst)) :
    warped = cv.circle(warped, (int(dst[i][0]), int(dst[i][1])), radius=20, color=(255, 0, 0), thickness=-1)

for i in range(len(points_image_src)) :
    img = cv.circle(img, (int(points_image_src[i][0]), int(points_image_src[i][1])), radius=20, color=(255, 0, 0), thickness=-1)

cv.imshow("original", img)
cv.imshow("warped", warped)

print(mat)

pythonMat = "["
for line in mat :
    pythonMat += "["
    for number in line :
        pythonMat += str(number)
        pythonMat += ","
    pythonMat = pythonMat[:-1]
    pythonMat += "],\n"
pythonMat = pythonMat[:-2]
pythonMat += "]"
print(pythonMat)

cv.waitKey(0)