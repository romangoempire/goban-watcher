import os

import cv2
import numpy as np
from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from icecream import ic
from surrealdb import Surreal

IMAGE_DIR = "images/raw"
CANNY_DIR = "images/canny"
SOBEL_DIR = "images/sobel"
LAPLASIAN_DIR = "images/laplacian"
LABEL_FILE = "data/labels.json"

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(CANNY_DIR, exist_ok=True)
os.makedirs(SOBEL_DIR, exist_ok=True)
os.makedirs(LAPLASIAN_DIR, exist_ok=True)


async def init_db() -> Surreal:
    db = Surreal("ws://localhost:8000/rpc")
    await db.connect()
    await db.use("goban_watcher", "labels")
    return db


app = FastAPI()


@app.get("/image_path")
async def image_path(db: Surreal = Depends(init_db)):
    images = os.listdir(IMAGE_DIR)

    # first image that needs to be labelled
    for img_path in images:
        found_image = await db.query(f"SELECT path FROM label WHERE path=={img_path}")
        if not found_image[0].get("results"):
            return img_path
    return


@app.get("/image")
def image(filename: str):
    return FileResponse(os.path.join(os.getcwd(), IMAGE_DIR, filename))


@app.get("/image_canny")
async def image_canny(filename: str):
    img = cv2.imread(f"{IMAGE_DIR}/{filename}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    canny = cv2.Canny(blur, 0, 100)
    canny_path = f"{CANNY_DIR}/{filename}"
    cv2.imwrite(canny_path, canny)

    return FileResponse(canny_path)


@app.get("/image_sobel")
async def image_sobel(filename: str):
    img = cv2.imread(f"{IMAGE_DIR}/{filename}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    sobel_x = cv2.Sobel(blur, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(blur, cv2.CV_64F, 0, 1, ksize=3)
    sobel = cv2.magnitude(sobel_x, sobel_y)
    sobel_path = f"{SOBEL_DIR}/{filename}"
    cv2.imwrite(sobel_path, sobel)
    return FileResponse(sobel_path)


@app.get("/image_laplacian")
async def image_lablacian(filename: str):
    img = cv2.imread(f"{IMAGE_DIR}/{filename}")
    laplacian = cv2.Laplacian(img, cv2.CV_64F)
    laplacian_abs = np.absolute(laplacian)
    laplacian_normalized = np.zeros((laplacian_abs.shape[0], laplacian_abs.shape[1], 1))
    laplacian_normalized = cv2.normalize(
        laplacian_abs, laplacian_normalized, 0.5, 255, cv2.NORM_MINMAX
    )

    laplacian_uint8 = np.uint8(laplacian_normalized)
    _, laplacian = cv2.threshold(laplacian_uint8, 40, 255, cv2.THRESH_BINARY)
    laplacian = cv2.cvtColor(laplacian, cv2.COLOR_BGR2GRAY)
    laplacian_path = f"{LAPLASIAN_DIR}/{filename}"
    cv2.imwrite(laplacian_path, laplacian)
    return FileResponse(laplacian_path)
