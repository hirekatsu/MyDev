# coding: utf-8

import cv2
import numpy as np
import imutils

print cv2.__version__

# img = cv2.imread('bin/T061_C0001.screen.png', 0)
# img2 = img.copy()
# template = cv2.imread('bin/ww_bookmarks_icon.png', 0)
# w, h = template.shape[::-1]
#
# methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
#             'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
#
# for meth in methods:
#     img = img2.copy()
#     method = eval(meth)
#
#     # Apply template Matching
#     res = cv2.matchTemplate(img, template, method)
#     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#
#     if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
#         top_left = min_loc
#     else:
#         top_left = max_loc
#     bottom_right = (top_left[0] + w, top_left[1] + h)
#
#     print meth
#     print 'top_left=%s, bottom_right=%s' % (top_left, bottom_right)
#
# cv2.rectangle(img, top_left, bottom_right, 255, 2)
# cv2.imshow("Image", img)
# cv2.waitKey(0)
# ##### -----------------------------------------------------------------

template = cv2.imread('./bin/ss/google_main.png', 0)
(tH, tW) = template.shape[:2]
image = cv2.imread(r'K:\_AC\160404_test3997\TA160406_095059.out\ss\_sc_101009.png', 0)

resized = imutils.resize(image, width=tW)
result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
(_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
r = image.shape[1] / float(tW)
found = (maxVal, maxLoc, r)
print '%s / %s' % (maxVal, r)
clone = np.dstack([resized, resized, resized])
cv2.rectangle(clone, (maxLoc[0], maxLoc[1]), (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
cv2.imshow("Visualize", clone)
cv2.waitKey(0)
print '----------'

for scale in np.linspace(0.2, 1.0, 20)[::-1]:
    # resize the image according to the scale, and keep track
    # of the ratio of the resizing
    resized = imutils.resize(image, width=int(image.shape[1] * scale))
    r = image.shape[1] / float(resized.shape[1])

    # if the resized image is smaller than the template, then break
    # from the loop
    if resized.shape[0] < tH or resized.shape[1] < tW:
        break
    # detect edges in the resized, grayscale image and apply template
    # matching to find the template in the image
    result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
    (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

    print '%s @ %s' % (maxVal, scale)
    # check to see if the iteration should be visualized
    if True:
        # draw a bounding box around the detected region
        clone = np.dstack([resized, resized, resized])
        cv2.rectangle(clone, (maxLoc[0], maxLoc[1]), (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
        cv2.imshow("Visualize", clone)
        cv2.waitKey(0)

    # if we have found a new maximum correlation value, then ipdate
    # the bookkeeping variable
    if found is None or maxVal > found[0]:
        found = (maxVal, maxLoc, r)

# unpack the bookkeeping varaible and compute the (x, y) coordinates
# of the bounding box based on the resized ratio
(_, maxLoc, r) = found
(startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
(endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

# draw a bounding box around the detected result and display the image
cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
cv2.imshow("Image", image)
cv2.waitKey(0)
