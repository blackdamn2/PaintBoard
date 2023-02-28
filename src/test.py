import cv2 as cv
import numpy as np

src = cv.imread(r"..\img\girl.jpg", cv.IMREAD_COLOR)
cv.imshow('lenna', src)
cv.waitKey(0)

blurImg = cv.GaussianBlur(src, (0, 0), sigmaX=15)
cv.imshow("gray", blurImg)
cv.waitKey(0)

# gray = cv.cvtColor(src, cv.COLOR_RGB2GRAY)
# cv.imshow(gray)