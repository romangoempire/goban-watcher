import cv2
import numpy as np
import matplotlib.pyplot as plt

# %%
IMAGE_PATH = "images"


def image(filename: str):
    return f"{IMAGE_PATH}/{filename}"


# %%

img = cv2.imread(image("2024-08-21 12-47-10.jpeg"))
rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
image_gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
inverted_image = cv2.bitwise_not(image_gray)

_, white_mask = cv2.threshold(image_gray, 150, 255, cv2.THRESH_BINARY)
_, black_mask = cv2.threshold(inverted_image, 210, 255, cv2.THRESH_BINARY)


white_stones = cv2.bitwise_and(image_gray, image_gray, mask=white_mask)
black_stones = cv2.bitwise_and(inverted_image, inverted_image, mask=black_mask)


# %%
plt.figure(figsize=(20, 20))


plt.subplot(2, 2, 1)
plt.imshow(image_gray, cmap="gray")
plt.axis("off")  # Hide the axis


plt.subplot(2, 2, 3)
plt.imshow(white_stones, cmap="gray")
plt.axis("off")  # Hide the axis

plt.subplot(2, 2, 4)
plt.imshow(black_stones, cmap="gray")
plt.axis("off")  # Hide the axis

plt.axis("off")  # Hide the axis
plt.tight_layout()
plt.show()
# %%

edges = cv2.Canny(image_gray, 50, 200)
kernel = np.ones((3, 3), np.uint8)
dilated_edges = cv2.dilate(edges, kernel, iterations=1)

# Step 6: Convert BGR to RGB for Matplotlib

# Display the result using Matplotlib
plt.figure(figsize=(10, 10))
plt.imshow(dilated_edges, cmap="gray")
plt.axis("off")  # Hide axes
plt.title("Detected Lines using Canny Edge Detection")
plt.show()

# %%

red_image = np.zeros((white_stones.shape[0], white_stones.shape[1], 3), dtype=np.uint8)
red_image[:, :, 0] = white_stones  # Set the red channel

blue_image = np.zeros((black_stones.shape[0], black_stones.shape[1], 3), dtype=np.uint8)
blue_image[:, :, 2] = black_stones  # Set the red channel


mask = image_gray > 0

# Initialize combined image
combined_image = np.zeros_like(red_image)

# Combine red and blue where the mask is True
combined_image[mask] = red_image[mask] + blue_image[mask]


plt.figure(figsize=(15, 15))
plt.imshow(combined_image)
plt.title("Combined Red and Blue Image")
plt.axis("off")
plt.show()
