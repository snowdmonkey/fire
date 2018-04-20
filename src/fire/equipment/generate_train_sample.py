import cv2
import numpy as np
import random
import argparse
import time
from fire.misc import Box
from pathlib import Path
from typing import Tuple
from ..video import VideoStream


def generate_equipment_n_background(img: np.ndarray, box: Box) -> Tuple[np.ndarray, np.ndarray]:
    """
    generate a pair of positive and negative samples of an equipment
    :param img: raw img as ndarray
    :param box: region of interest, i.e., where position of the equipment in the raw image
    :return: an image of the equipment and an image of the background
    """
    height, width, _ = img.shape

    equipment_img = img[int(box.ymin * height):int(box.ymax * height), int(box.xmin * width):int(box.xmax * width)]

    # create a frame without equipment
    stacked_frame = np.concatenate((img, img), axis=1)
    fake_img = img.copy()
    fake_img[int(box.ymin * height):int(box.ymax * height), int(box.xmin * width):int(box.xmax * width)] = \
        stacked_frame[int(box.ymin * height):int(box.ymax * height),
        int(box.xmax * width):(int(box.xmax * width) * 2 - int(box.xmin * width))]

    # create a background image from the fake image
    height, width, _ = fake_img.shape
    box_width = int(box.xmax * width) - int(box.xmin * width)
    box_height = int(box.ymax * height) - int(box.ymin * height)

    x = random.choice(range(width - box_width))
    y = random.choice(range(height - box_height))
    background_img = fake_img[y:(y + box_height), x:(x + box_width)]

    return equipment_img, background_img


def generate_from_folder(img_folder: Path, box: Box):

    equipment_img_folder = img_folder / "equipment"
    background_img_folder = img_folder / "background"

    equipment_img_folder.mkdir(exist_ok=True)
    background_img_folder.mkdir(exist_ok=True)

    for img_path in img_folder.glob("*.jpg"):

        equipment_img_path = equipment_img_folder / img_path.name
        background_img_path = background_img_folder / img_path.name

        img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)

        equipment_img, background_img = generate_equipment_n_background(img, box)

        cv2.imwrite(str(equipment_img_path), equipment_img)
        cv2.imwrite(str(background_img_path), background_img)
        print("writing to {}".format(str(equipment_img_path)))


def generate_from_video(video_path: Path, output_folder: Path, sample_size: int, box: Box):
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
        # print(frame_index)

        ret, frame = cap.read()
        if ret is False:
            break
        if frame_index not in frame_selected_index:
            continue

        equipment_img_path = equipment_img_folder / "{}.jpg".format(frame_index)
        background_img_path = background_img_folder / "{}.jpg".format(frame_index)

        equipment_img, background_img = generate_equipment_n_background(frame, box)

        cv2.imwrite(str(equipment_img_path), equipment_img)
        cv2.imwrite(str(background_img_path), background_img)
        print("writing to {}".format(str(equipment_img_path)))


def generate_from_stream(stream_url: str, output_folder: Path, sample_size: int, interval: float, box: Box):
    """
    generate training images from a live video stream
    :param stream_url: rtsp or rtmp url of the stream
    :param output_folder: folder to save the images for training
    :param sample_size: how many images in each class
    :param interval: how many seconds between two frames to take
    :param box: bounding box of the equipment
    :return: None
    """
    equipment_img_folder = output_folder / "equipment"
    background_img_folder = output_folder / "background"

    equipment_img_folder.mkdir(exist_ok=True, parents=True)
    background_img_folder.mkdir(exist_ok=True, parents=True)

    video = VideoStream(url=stream_url, device_id="")
    video.start()

    for i in range(sample_size):
        frame = video.read_current_frame()

        equipment_img_path = equipment_img_folder / "{}.jpg".format(i)
        background_img_path = background_img_folder / "{}.jpg".format(i)

        equipment_img, background_img = generate_equipment_n_background(frame, box)

        cv2.imwrite(str(equipment_img_path), equipment_img)
        cv2.imwrite(str(background_img_path), background_img)
        print("writing to {}".format(str(equipment_img_path)))

        time.sleep(interval)

    video.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser("generate train samples for equipment existence training check")
    subparsers = parser.add_subparsers(dest="subcommand")

    from_video_parser = subparsers.add_parser("from_video")
    from_video_parser.add_argument("video_path", type=str)
    from_video_parser.add_argument("output_folder", type=str)
    from_video_parser.add_argument("sample_size", type=int)

    from_stream_parser = subparsers.add_parser("from_stream")
    from_stream_parser.add_argument("video_url", type=str)
    from_stream_parser.add_argument("output_folder", type=str)
    from_stream_parser.add_argument("sample_size", type=int)
    from_stream_parser.add_argument("interval", type=float)

    from_folder_parser = subparsers.add_parser("from_folder")
    from_folder_parser.add_argument("folder_path", type=str)

    parser.add_argument("xmin", type=float)
    parser.add_argument("xmax", type=float)
    parser.add_argument("ymin", type=float)
    parser.add_argument("ymax", type=float)

    args = parser.parse_args()

    if args.subcommand == "from_video":
        generate_from_video(video_path=Path(args.video_path),
                            output_folder=Path(args.output_folder),
                            sample_size=args.sample_size,
                            box=Box(xmin=args.xmin, xmax=args.xmax, ymin=args.ymin, ymax=args.ymax))
    elif args.subcommand == "from_stream":
        generate_from_stream(stream_url=args.video_url, output_folder=Path(args.output_folder),
                             sample_size=args.sample_size, interval=args.interval,
                             box=Box(xmin=args.xmin, xmax=args.xmax, ymin=args.ymin, ymax=args.ymax))
    elif args.subcommand == "from_folder":
        generate_from_folder(Path(args.folder_path),
                             Box(xmin=args.xmin, xmax=args.xmax, ymin=args.ymin, ymax=args.ymax))
    else:
        raise ValueError("unknown subcommand")