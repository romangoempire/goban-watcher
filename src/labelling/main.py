import asyncio
import os
import enum
import pathlib as pl

import cv2
from dotenv import load_dotenv
from icecream import ic
import numpy as np
from surrealdb import Surreal

ROOT_DIR = "goban-watcher"
IMAGE_PATH = (
    f"{pl.Path.cwd()}/images"
    if pl.Path.cwd().name == ROOT_DIR
    else f"{pl.Path.cwd().parent}/images"
)
RAW_IMAGES_PATH = f"{IMAGE_PATH}/raw"


class Color(enum.Enum):
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)


async def files_to_label() -> list:
    load_dotenv()

    db = Surreal(str(os.getenv("SURREAL_URL")))
    await db.connect()
    await db.signin(
        {"user": str(os.getenv("SURREAL_USER")), "pass": str(os.getenv("SURREAL_PASS"))}
    )
    await db.use(str(os.getenv("SURREAL_NS")), str(os.getenv("SURREAL_DB")))

    files = [file for file in pl.Path(RAW_IMAGES_PATH).glob("*") if file.is_file()]

    response = await db.query("SELECT path FROM label")
    labelled_files = response[0]["result"]
    await db.close()

    return [file for file in files if file.as_posix() not in labelled_files]


files = asyncio.run(files_to_label())
selected_point = None


def get_mouse_position(event, x, y, flags, param):
    global selected_point
    if event == cv2.EVENT_MOUSEMOVE:
        if selected_point is not None:
            points[selected_point] = [x, y]
    if event == cv2.EVENT_LBUTTONDOWN:
        if selected_point is not None:
            selected_point = None
            return
        for i, point in enumerate(points):
            if (
                max(point[0], x) - min(point[0], x) < 10
                and max(point[1], y) - min(point[1], y) < 10
            ):
                selected_point = i


for index, file in enumerate(files):
    selected_point = 0
    original_img = cv2.imread(file.as_posix())
    left = int(original_img.shape[1] / 3)
    right = int(original_img.shape[1] - original_img.shape[1] / 3)
    top = int(original_img.shape[0] / 4)
    bottom = int(original_img.shape[0] - original_img.shape[0] / 4)

    points = [
        [left, top],
        [right, top],
        [left, bottom],
        [right, bottom],
    ]

    cv2.namedWindow(file.name)
    cv2.setMouseCallback(file.name, get_mouse_position)
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("1"):
            selected_point = 0
        if key == ord("2"):
            selected_point = 1
        if key == ord("3"):
            selected_point = 2
        if key == ord("4"):
            selected_point = 3

        if cv2.waitKey(1) & 0xFF == ord("q"):
            ic(points)
            cv2.destroyWindow(file.name)
            break

        img = cv2.putText(
            original_img.copy(),
            f"{index+1}/{len(files)}",
            (10, 30),
            cv2.FONT_HERSHEY_COMPLEX,
            0.5,
            (255, 255, 255),
        )

        for index, point in enumerate(points):
            if selected_point == index:
                img = cv2.circle(img, point, 3, Color.GREEN.value, -1)
            else:
                img = cv2.circle(img, point, 3, Color.RED.value, -1)

        pts1 = np.float32(points)
        pts2 = np.float32(
            [
                [0, 0],
                [500, 0],
                [0, 500],
                [500, 500],
            ]
        )

        M = cv2.getPerspectiveTransform(pts1, pts2)

        transformed = cv2.warpPerspective(img, M, (500, 500))
        cv2.imshow(file.name, img)
        cv2.imshow("Transformed", transformed)

cv2.destroyAllWindows()
