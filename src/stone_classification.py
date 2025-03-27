import pickle

import torch
import torch.nn as nn
import torch.nn.functional as F


class StoneClassifactionModel(nn.Module):
    def __init__(self):
        super(StoneClassifactionModel, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(32 * 16 * 16, 128)
        self.fc2 = nn.Linear(128, 3)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 32 * 16 * 16)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


def load_rf(path):
    with open(path, "rb") as file:
        model = pickle.load(file)
    return model


def load_cnn(path) -> StoneClassifactionModel:
    model = StoneClassifactionModel()
    model.load_state_dict(torch.load(path))
    return model
