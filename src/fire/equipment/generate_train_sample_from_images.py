import cv2
import numpy as np
import random
from fire.misc import Box
from pathlib import Path


def main(img_folder: Path, box: Box):

    equipment_img_folder = img_folder / "equipment"
    background_img_folder = img_folder / "background"

    equipment_img_folder.mkdir(exist_ok=True)
    background_img_folder.mkdir(exist_ok=True)

    for img_path in img_folder.glob("*.jpg"):

        equipment_img_path = equipment_img_folder / img_path.name
        background_img_path = background_img_folder / img_path.name

        img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)

        height, width, _ = img.shape

        equipment_img = img[int(box.ymin*height):int(box.ymax*height), int(box.xmin*width):int(box.xmax*width)]

        # create a frame without equipment
        stacked_frame = np.concatenate((img, img), axis=1)
        fake_img = img.copy()
        fake_img[int(box.ymin*height):int(box.ymax*height), int(box.xmin*width):int(box.xmax*width)] = \
            stacked_frame[int(box.ymin*height):int(box.ymax*height),
            int(box.xmax*width):(int(box.xmax*width)*2 - int(box.xmin*width))]

        # create a background image from the fake image
        height, width, _ = fake_img.shape
        box_width = int(box.xmax*width) - int(box.xmin*width)
        box_height = int(box.ymax*height) - int(box.ymin*height)

        x = random.choice(range(width - box_width))
        y = random.choice(range(height - box_height))
        background_img = fake_img[y:(y + box_height), x:(x + box_width)]

        cv2.imwrite(str(equipment_img_path), equipment_img)
        cv2.imwrite(str(background_img_path), background_img)
        print("writing to {}".format(str(equipment_img_path)))


if __name__ == "__main__":
    main(Path(r"C:\Users\h232559\Desktop\test_imgs"), Box(xmin=0.23385, xmax=0.57604, ymin=0.10556, ymax=0.40556))