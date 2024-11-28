import torch.nn as nn
import torch.nn.functional as F


class StoneClassifactionModel(nn.Module):
    def __init__(self):
        super(StoneClassifactionModel, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(32 * 26 * 26, 128)
        self.fc2 = nn.Linear(128, 3)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 32 * 26 * 26)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x
