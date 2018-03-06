"""
this module aim to generate train samples from a video
the generated samples can be fed to tensorflow and produce the model for equipment presence monitoring
"""

import cv2
import random
import argparse
import numpy as np
from pathlib import Path
from ..misc import Box


def generate_samples(video_path: Path, output_folder: Path, sample_size: int, box: Box):
    """
    generate pictures from a video
    :param video_path: path of the video file from which training images are cropped
    :param output_folder: folder to save the cropped images
    :param sample_size: sample size for train images
    :param box: bounding box in which the equipment exists
    :return: None
    """
    if not output_folder.exists():
        output_folder.mkdir()

    equipment_img_folder = output_folder / "equipment"
    background_img_folder = output_folder / "background"

    if not equipment_img_folder.exists():
        equipment_img_folder.mkdir()
    if not background_img_folder.exists():
        background_img_folder.mkdir()

    cap = cv2.VideoCapture(str(video_path))

    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_selected_index = random.sample(range(n_frames), sample_size)
    print(frame_selected_index)

    frame_index = 0
    while True:

        frame_index += 1
        print(frame_index)

        ret, frame = cap.read()
        if ret is False:
            break
        if frame_index not in frame_selected_index:
            continue

        equipment_img_path = equipment_img_folder / "{}.jpg".format(frame_index)
        background_img_path = background_img_folder / "{}.jpg".format(frame_index)

        equipment_img = frame[box.y:(box.y+box.h), box.x: (box.x+box.w)]

        # create a frame without equipment
        stacked_frame = np.concatenate((frame, frame), axis=1)
        fake_frame = frame.copy()
        fake_frame[box.y:(box.y+box.h), box.x: (box.x+box.w)] = \
            stacked_frame[box.y:(box.y+box.h), (box.x+box.w): (box.x + 2*box.w)]

        # create a background image from the fake image
        height, width, _ = fake_frame.shape
        x = random.choice(range(width-box.w))
        y = random.choice(range(height-box.h))
        background_img = fake_frame[y:(y+box.h), x:(x+box.w)]

        cv2.imwrite(str(equipment_img_path), equipment_img)
        cv2.imwrite(str(background_img_path), background_img)
        print("writing to {}".format(str(equipment_img_path)))


def main():
    parser = argparse.ArgumentParser(description="generate training samples")
    parser.add_argument("video_path", type=str, help="path of the video file")
    parser.add_argument("output_path", type=str, help="path of the output folder")
    parser.add_argument("x", type=int, help="x of the bounding box")
    parser.add_argument("y", type=int, help="y of the bounding box")
    parser.add_argument("w", type=int, help="w of the bounding box")
    parser.add_argument("h", type=int, help="h of the bounding box")
    parser.add_argument("sample_size", type=int, help="number of images to generate")

    args = parser.parse_args()

    generate_samples(Path(args.video_path), Path(args.output_path), args.sample_size,
                     Box(args.x, args.y, args.w, args.h))


if __name__ == "__main__":
    main()