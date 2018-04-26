import logging
import threading
from typing import Optional
from queue import Queue, Empty

import cv2
import numpy as np
import time

from .misc import Box

logger = logging.getLogger(__name__)


class ReadFrameError(Exception):
    pass


class VideoStreamClosedError(Exception):
    pass


class VideoStream:
    def __init__(self, url: str, device_id: str, n_frame_skip: int = 2, roi: Optional[Box] = None):
        """
        constructor

        :param url: url for the video stream
        :param device_id: str
        :param n_frame_skip: number of frames to skip before decode a frame
        :param roi: region of interests in the video frames
        """
        self._video_url = url
        self._roi = roi
        self._device_id = device_id
        # self._current_frame = None
        self._q = Queue(16)  # a buffer to store the latest frames
        self._running = False
        self._thread = threading.Thread(target=self._update_current_frame)
        # self._thread = Process(target=self._update_current_frame)
        self._cap = None
        self._n_frame_skip = n_frame_skip

    @property
    def device_id(self):
        return self._device_id

    def _connect(self):
        logger.info("try to connect to {}".format(self._device_id))
        self._cap = cv2.VideoCapture(self._video_url)
        if self._cap.isOpened() is False:
            raise VideoStreamClosedError("fail to open connection to device {}".format(self._device_id))

    def _disconnect(self):
        if self._cap is not None:
            self._cap.release()

    def _reconnect(self):
        self._disconnect()
        self._connect()

    def _update_current_frame(self):

        while self._running is True:
            logger.debug("queue size: {}".format(self._q.qsize()))

            if self._cap.isOpened() is False:
                raise VideoStreamClosedError("lost connection to device {}".format(self._device_id))

            for _ in range(self._n_frame_skip):  # grab frames but do not decode to save computational resource
                self._cap.grab()

            if self._cap.grab():
                if not self._q.full():
                    ret, frame = self._cap.retrieve()
                    if ret is True:
                        self._q.put(frame)
            else:
                self._reconnect()

            # for _ in range(10):  # try to read frame for 10 times
            #     ret, frame = self._cap.read()
            #     if ret is True:
            #         break
            #     else:
            #         time.sleep(0.1)

            # if frame is None:  # reconnect if cannot read a frame
            #     self._reconnect()
            # else:
            #     self._current_frame = frame

        self._cap.release()

    def start(self):
        self._running = True
        self._connect()

        self._thread.start()

    def close(self):
        self._running = False

    def read_current_frame(self) -> Optional[np.ndarray]:
        """
        read current frame from camera

        :return: ndarray as the current frame
        """
        try:
            frame = self._q.get(block=True, timeout=300)
        except Empty as e:
            self.close()
            raise e

        return frame

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
        height, width, _ = current_frame.shape
        # current_roi = current_frame[box.y: (box.y+box.h), box.x: (box.x+box.w), :]
        current_roi = current_frame[int(height * box.ymin): int(height * box.ymax),
                      int(width * box.xmin): int(width * box.xmax), :]
        return current_roi

    def __del__(self):
        self.close()
