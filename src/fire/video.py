from .misc import Box
from typing import Optional
import cv2
import numpy as np
import threading


class ReadFrameError(Exception):
    pass


class VideoStreamClosed(Exception):
    pass


class VideoStream:

    def __init__(self, url: str, device_id: str, roi: Optional[Box] = None):
        """
        constructor

        :param url: url for the video stream
        :param device_id: str
        :param roi: region of interests in the video frames
        """
        self._video_url = url
        self._roi = roi
        self._device_id = device_id
        self._current_frame = None
        self._running = False
        self._thread = threading.Thread(target=self._update_current_frame)
        self._cap = None

    @property
    def device_id(self):
        return self._device_id

    def _update_current_frame(self):
        # cap = cv2.VideoCapture(self._video_url)
        # if cap.isOpen() is False:
        #

        while self._running is True:
            if self._cap.isOpened() is False:
                raise VideoStreamClosed()

            ret, frame = self._cap.read()
            self._current_frame = frame

        self._cap.release()

    def start(self):
        self._running = True
        cap = cv2.VideoCapture(self._video_url)
        if cap.isOpened() is False:
            raise VideoStreamClosed()
        else:
            _, self._current_frame = cap.read()
            self._cap = cap

        self._thread.start()

    def close(self):
        self._running = False

    def read_current_frame(self) -> Optional[np.ndarray]:
        """
        read current frame from camera

        :return: ndarray as the current frame
        """

        return self._current_frame

    def read_current_roi(self) -> Optional[np.ndarray]:
        """
        read current region of interests

        :return: ndarray as the current region of interests
        """
        if self._roi is None:
            raise ValueError("current roi is not set")
        current_frame = self.read_current_frame()
        if current_frame is None:
            return None
        box = self._roi
        current_roi = current_frame[box.y: (box.y+box.h), box.x: (box.x+box.w), :]
        return current_roi

    def __del__(self):
        self.close()
