from helper import logger
import cv2
import numpy as np
import imutils


class ImageTemplate:
    def __init__(self, image_path):
        logger.debug('%s: template path=%s' % (self.__class__, image_path))
        self._template = cv2.imread(image_path, 0)
        (self._height, self._width) = self._template.shape[:2]

    def match(self, image_path, threshold):
        logger.debug('ImageTemplate.match: image_path=%s, threshold=%s' % (image_path, threshold))
        image = cv2.imread(image_path, 0)

        # first try with same width
        resized = imutils.resize(image, width=self._width)
        r = image.shape[1] / float(self._width)
        result = cv2.matchTemplate(resized, self._template, cv2.TM_CCOEFF_NORMED)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
        logger.debug('ratio=%s, maxVal=%s, maxLoc=%s' % (r, maxVal, maxLoc))
        found = (maxVal, maxLoc, r)

        for scale in np.linspace(0.2, 1.0, 20)[::-1]:
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(image, width=int(image.shape[1] * scale))
            r = image.shape[1] / float(resized.shape[1])

            # if the resized image is smaller than the template, then break
            # from the loop
            if resized.shape[0] < self._height or resized.shape[1] < self._width:
                break
            # detect edges in the resized, grayscale image and apply template
            # matching to find the template in the image
            result = cv2.matchTemplate(resized, self._template, cv2.TM_CCOEFF_NORMED)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
            logger.debug('ratio=%s, maxVal=%s, maxLoc=%s' % (r, maxVal, maxLoc))

            # if we have found a new maximum correlation value, then ipdate
            # the bookkeeping variable
            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)

        # unpack the bookkeeping variable and compute the (x, y) coordinates
        # of the bounding box based on the resized ratio
        (maxVal, maxLoc, r) = found
        if maxVal < threshold:
            logger.debug('found maxVal=%s, less than threshold' % maxVal)
            return (None, None), (None, None)
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + self._width) * r), int((maxLoc[1] + self._height) * r))
        return (startX, startY), (endX, endY)
