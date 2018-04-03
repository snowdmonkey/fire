from .misc import Box
from typing import Optional
import cv2
import numpy as np


class ReadFrameError(Exception):
    pass


class VideoStream:

    def __init__(self, url: str, roi: Optional[Box] = None):
        """
        constructor

        :param url: url for the video stream
        :param roi: region of interests in the video frames
        """
        self._video_url = url
        self._roi = roi

    def read_current_frame(self) -> np.ndarray:
        """
        read current frame from camera

        :return: ndarray as the current frame
        """
        cap = cv2.VideoCapture(self._video_url)
        ret, frame = cap.read()
        cap.release()
        if ret is False:
            raise ReadFrameError("fail to read a frame from video source")
        return frame

    def read_current_roi(self) -> np.ndarray:
        """
        read current region of interests

        :return: ndarray as the current region of interests
        """
        if self._roi is None:
            raise ValueError("current roi is not set")
        current_frame = self.read_current_frame()
        box = self._roi
        current_roi = current_frame[box.y: (box.y+box.h), box.x: (box.x+box.w), :]
        return current_roi