import json
import streamlit as st
import os
import math


@st.cache_data
def load_json(run: str, logscale: bool = False) -> list:
    with open(f"data/{run}.json") as f:
        data = json.load(f)
    total_images = len([f for f in os.listdir(f"images/{timestamp}")])
    if not logscale:
        return [d for d in data[:total_images]]
    else:
        return [math.log(d) for d in data[:total_images]]


@st.cache_data
def load_image(run: str, number: int) -> bytes:
    with open(f"images/{run}/{number}.jpg", "rb") as f:
        return f.read()


st.title("Pixel Changes")

recordings = [r.rstrip(".json") for r in os.listdir("data")]

timestamp = st.sidebar.selectbox("Recording", recordings)


st.subheader("Percentage difference in log over time")


log_scale = st.sidebar.checkbox("Logscale")
threshhold = st.sidebar.number_input("Threshold", 0.00, format="%.4f")
results = load_json(timestamp, log_scale)
filtered_results = [
    (i + 1, 0) if threshhold > r else (i + 1, r) for i, r in enumerate(results)
]
images_after_movement = [
    i
    for i, r in enumerate(filtered_results)
    if r[1] == 0 and filtered_results[i - 1][1] > 0
]

st.line_chart([r[1] for r in filtered_results])
count_results = len(results)
count_filtered = len([r for r in filtered_results if r[1] > threshhold])
st.write("Total Images:", count_results)
st.write("Image with high movement:", count_filtered)
st.write("Images after movement:", len(images_after_movement))
selected_image = st.selectbox("Images after movement", images_after_movement)
last_image = load_image(timestamp, selected_image - 1)
image = load_image(timestamp, selected_image)

cols = st.columns(3)
with cols[0]:
    st.image(load_image(timestamp, selected_image - 2))
with cols[1]:
    st.image(load_image(timestamp, selected_image - 1))
with cols[2]:
    st.image(load_image(timestamp, selected_image))
