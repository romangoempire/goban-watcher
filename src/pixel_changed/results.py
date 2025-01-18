import json
import os

import cv2
import streamlit as st
from cv2.typing import MatLike
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src import DATA_PATH, IMG_PATH

img_path = IMG_PATH.joinpath("games")
data_path = DATA_PATH.joinpath("games")


@st.cache_data
def load_json(run: str) -> list:
    with open(f"{data_path}/{run}.json") as f:
        data = json.load(f)
    return data


@st.cache_data
def load_image(run: str, number: int) -> MatLike:
    img = cv2.imread(f"{img_path}/{run}/{number}.jpg")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


st.title("Pixel Changes")

recordings = [r.rstrip(".json") for r in os.listdir(data_path)]

run = st.sidebar.selectbox("Recording", recordings)
results = load_json(run)

selected_range = st.slider("Select", 0, len(results), [0, len(results)])
selected_results = results[selected_range[0] : selected_range[1]]
threshold = st.number_input("Threshold", 0.001, format="%.4f")


ma_results = [
    sum(selected_results[i - 30 : i]) / 30 for i, _ in enumerate(selected_results)
]
results_after_movement = [
    i
    for i, r in enumerate(ma_results)
    if r < threshold and ma_results[i - 1] > threshold
]

st.write("Percentage difference over time")
st.line_chart(selected_results, x_label="frame", y_label="percentage changed")
st.line_chart(ma_results, x_label="frame", y_label="percentage changed")


st.write("Total Images:", len(selected_results))
st.write("Image with high movement:", len(results_after_movement))


@st.fragment()
def display_images():
    image_after_movement = st.select_slider(
        "Images after Movement", results_after_movement
    )
    index = results_after_movement.index(image_after_movement)

    last_image = load_image(run, results_after_movement[max(0, index - 1)])
    current_image = load_image(run, image_after_movement)

    cols = st.columns(3)
    with cols[0]:
        st.subheader("Last Recoring")
        st.image(last_image)

    with cols[1]:
        st.subheader("Current")
        st.image(current_image)

    with cols[2]:
        st.subheader("Difference")
        diff_image = cv2.absdiff(last_image, current_image)
        gray_diff_image = cv2.cvtColor(diff_image, cv2.COLOR_BGR2GRAY)
        _, gray_diff_image = cv2.threshold(gray_diff_image, 20, 255, cv2.THRESH_BINARY)
        st.image(gray_diff_image)


display_images()
