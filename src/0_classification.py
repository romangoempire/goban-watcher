# %%

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision
from icecream import ic
from torch.utils.data import DataLoader, Dataset
from torchvision.io import read_image, ImageReadMode

# %%

root_path = os.path.dirname(os.getcwd())
img_path = f"{root_path}/images"

# %%

classes = (
    "empty",
    "black",
    "white",
)

# %%


def png_files(parent: str, dir: str) -> list[str]:
    return [
        f"{parent}/{dir}/{f}"
        for f in os.listdir(f"{parent}/{dir}")
        if f.endswith(".png")
    ]


sorted_annotations = pd.DataFrame(
    [
        (file_path, classes.index(label))
        for label in classes
        for file_path in png_files(img_path, label)
    ]
)

# %%
# column_name = sorted_annotations.columns[1]

# # Count the number of samples in each category
# min_count = sorted_annotations[column_name].value_counts().min()

# # Create a list to hold the undersampled DataFrame
# undersampled_df = pd.DataFrame()

# # Loop through each category and sample
# for label in sorted_annotations[column_name].unique():
#     undersampled_df = pd.concat(
#         [
#             undersampled_df,
#             sorted_annotations[sorted_annotations[column_name] == label].sample(
#                 min_count, random_state=42
#             ),
#         ]
# )


# %%
annotations = sorted_annotations.sample(frac=1, random_state=42).reset_index(drop=True)
# annotations = undersampled_df.sample(frac=1, random_state=42).reset_index(drop=True)

percentage_train: float = 0.7
total_annotations = annotations.shape[0]
amount_train_annotations = int(total_annotations * percentage_train)


train_annotations, test_annotations = (
    annotations[:amount_train_annotations],
    annotations[amount_train_annotations:],
)


# %%


class StonesDataset(Dataset):
    def __init__(self, labels: pd.DataFrame, transform=None):
        self.labels = labels
        self.transform = transform

    def __len__(self) -> int:
        return self.labels.shape[0]

    def __getitem__(self, idx):
        img_path, label = self.labels.iloc[idx]
        image = read_image(img_path, mode=ImageReadMode.RGB)
        if self.transform:
            image = self.transform(image)

        # Ensure label is returned as a scalar
        label = int(label)

        return image, label


transform = transforms.Compose(
    [
        transforms.ToPILImage(),
        transforms.Resize((105, 105)),  # Resize to 105x105
        transforms.ToTensor(),  # Convert to tensor
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),  # Normalize
    ]
)
train_dataset = StonesDataset(train_annotations, transform)
test_dataset = StonesDataset(test_annotations, transform)

batch_size = 64

train_loader = DataLoader(
    train_dataset, batch_size=batch_size, shuffle=True, drop_last=True
)
test_loader = DataLoader(
    test_dataset, batch_size=batch_size, shuffle=True, drop_last=True
)


# %%


def imshow(img):
    img = img / 2 + 0.5  # unnormalize
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()


# get some random training images
dataiter = iter(train_loader)
images, labels = next(dataiter)

# show images
imshow(torchvision.utils.make_grid(images))
print(" ".join(f"{classes[labels[j]]:5s}" for j in range(batch_size)))


# %%
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(
            3, 16, kernel_size=3, padding=1
        )  # Output: (16, 105, 105)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)  # Halves the size
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)  # Output: (32, 52, 52)

        # Update the input size for the fully connected layer
        self.fc1 = nn.Linear(32 * 26 * 26, 128)  # Output after pooling: (32, 26, 26)
        self.fc2 = nn.Linear(128, 3)  # Output for 3 classes

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))  # Apply conv1 and max pooling
        x = self.pool(F.relu(self.conv2(x)))  # Apply conv2 and max pooling
        x = x.view(-1, 32 * 26 * 26)  # Flatten the tensor, adjust size here
        x = F.relu(self.fc1(x))  # First fully connected layer
        x = self.fc2(x)  # Output layer
        return x


net = Net()

# %%

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(net.parameters(), lr=0.001)

# %%
for epoch in range(1):
    running_loss = 0.0
    ic(len(train_loader))
    for i, data in enumerate(train_loader, 0):
        inputs, labels = data

        optimizer.zero_grad()

        outputs = net(inputs)

        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        mini_batches = len(train_loader) // 100
        if i % mini_batches == mini_batches - 1:
            print(f"[{epoch + 1}, {i + 1:5d}] loss: {running_loss / mini_batches:.3f}")
            running_loss = 0.0
print("Finished Training")

# %%

PATH = "./net.pth"
torch.save(net.state_dict(), PATH)

# %%

dataiter = iter(test_loader)
images, labels = next(dataiter)

# print images
imshow(torchvision.utils.make_grid(images))
print("GroundTruth: ", " ".join(f"{classes[labels[j]]:5s}" for j in range(batch_size)))

outputs = net(images)

_, predicted = torch.max(outputs, 1)

print("Predicted: ", " ".join(f"{classes[predicted[j]]:5s}" for j in range(batch_size)))


# %%
correct = 0
total = 0
# since we're not training, we don't need to calculate the gradients for our outputs
with torch.no_grad():
    for data in test_loader:
        images, labels = data
        # calculate outputs by running images through the network
        outputs = net(images)
        # the class with the highest energy is what we choose as prediction
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
print(f"Accuracy of the network on the {total} test images: {100 * correct // total} %")

# %%
# prepare to count predictions for each class
correct_pred = {classname: 0 for classname in classes}
total_pred = {classname: 0 for classname in classes}

# again no gradients needed
with torch.no_grad():
    for data in test_loader:
        images, labels = data
        outputs = net(images)
        _, predictions = torch.max(outputs, 1)
        # collect the correct predictions for each class
        for label, prediction in zip(labels, predictions):
            if label == prediction:
                correct_pred[classes[label]] += 1
            else:
                ic(label, prediction)
            total_pred[classes[label]] += 1


# print accuracy for each class
for classname, correct_count in correct_pred.items():
    accuracy = 100 * float(correct_count) / total_pred[classname]
    print(f"Accuracy for class: {classname:5s} is {accuracy:.1f} %")
# %%


# %%
