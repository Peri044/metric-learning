import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision

class SimpleNet(nn.Module):
    def __init__(self, feature_size=64, im_size=128):
        super(SimpleNet, self).__init__()
        self.feature_size=feature_size
        self.im_size = im_size
        self.h1_len = (self.im_size-4)/2
        self.h2_len = (self.h1_len-4)/2
        self.fc1_len = self.h2_len*self.h2_len*20
        # all the layers
        self.bn0   = nn.BatchNorm2d(3)
        self.conv1 = nn.Conv2d(3, 10, kernel_size=5)
        self.bn1   = nn.BatchNorm2d(10)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.bn2   = nn.BatchNorm2d(20)
        self.conv2_drop = nn.Dropout2d(p=0.3)
        self.fc1 = nn.Linear(self.fc1_len, 512)
        self.bn3 = nn.BatchNorm1d(512)
        self.fc2 = nn.Linear(512, feature_size)

    def forward(self, x):
        x = self.bn0(x)
        x = F.relu(F.max_pool2d(self.bn1(self.conv1(x)), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.bn2(self.conv2(x))), 2))
        x = x.view(-1, self.fc1_len)
        x = F.relu(self.bn3(self.fc1(x)))
        x = F.dropout(x, training=self.training)
        return self.fc2(x)

class ShallowNet(nn.Module):
    def __init__(self, feature_size=64, im_size=96):
        super(ShallowNet, self).__init__()
        self.feature_size=feature_size
        self.im_size = im_size
        self.h1_len = (self.im_size-6)/2
        self.h2_len = (self.h1_len-5)/2
        self.fc1_len = self.h2_len*self.h2_len*32
        # all the layers
        self.bn0   = nn.BatchNorm2d(3)
        self.conv1 = nn.Conv2d(3, 32, kernel_size=7)
        self.conv1_drop = nn.Dropout2d(p=0.3)
        self.bn1   = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 32, kernel_size=5)
        self.bn2   = nn.BatchNorm2d(32)
        self.conv2_drop = nn.Dropout2d(p=0.3)
        self.fc1 = nn.Linear(self.fc1_len, 512)
        self.bn3 = nn.BatchNorm1d(512)
        self.fc2 = nn.Linear(512, feature_size)

    def forward(self, x):
        x = self.bn0(x)
        x = F.relu(F.max_pool2d(self.conv1_drop(self.bn1(self.conv1(x))), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.bn2(self.conv2(x))), 2))
        x = x.view(-1, self.fc1_len)
        x = F.relu(self.bn3(self.fc1(x)))
        x = F.dropout(x, training=self.training)
        return self.fc2(x)

class InceptionBased(nn.Module):
    def __init__(self, feature_size=64, im_size=299):
        super(InceptionBased, self).__init__()
        self.im_size = 299
        self.feature_size=feature_size
        self.inception = torchvision.models.inception_v3(pretrained=True)
        self.inception.fc = nn.Linear(2048, feature_size)

    def forward(self, x):
        return self.inception(x)[0]

class SqueezeNetBased(nn.Module):
    def __init__(self, feature_size=64, im_size=224):
        super(SqueezeNetBased, self).__init__()
        self.im_size = 224
        self.feature_size = feature_size
        self.features = torchvision.models.squeezenet1_1(pretrained=True).features
        final_conv = nn.Conv2d(512, feature_size, kernel_size=1)
        classifier = nn.Sequential(
            nn.Dropout(p=0.5),
            final_conv,
            nn.ReLU(inplace=True),
            nn.AvgPool2d(13)
        )
        self.classifier = classifier

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x.view(-1, self.feature_size)