from torch import nn
import torch
import numpy as np
import torch.optim as optim


class Model():
    def __init__(self):
        self.criterion = nn.BCEWithLogitsLoss()
        self.cnn_model = ConvNet()
        self.iteration = 0
        self.optimizer = optim.Adam(self.cnn_model.parameters(),
                                    lr=1e-3)
        self.running_loss = []
        print(self.cnn_model)

    def train(self, s0, s1, force):
        x = torch.from_numpy(s0)
        y = torch.from_numpy(s1)
        x_force = torch.from_numpy(force)
        self.optimizer.zero_grad()
        logits, out = self.cnn_model.forward(x, x_force)
        loss = self.criterion(logits.reshape([1, 32 * 128]),
                              y.reshape([1, 32 * 128]))
        loss.backward()
        self.running_loss += [loss.data[0]]
        if len(self.running_loss) >= 1000:
            self.running_loss.pop(0)
        if (self.iteration % 100) == 0:
            print('loss: {}'.format(np.mean(self.running_loss)))
        self.optimizer.step()
        y1 = out.data.numpy()
        self.iteration += 1
        return y1


class ConvNet(nn.Module):
    def __init__(self):
        super(ConvNet, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(1, 8, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(8),
            nn.ReLU())
        self.layer2 = nn.Sequential(
            nn.Conv2d(8, 16, kernel_size=6, stride=2, padding=2),
            nn.BatchNorm2d(16),
            nn.ReLU())
        self.layer3 = nn.Sequential(nn.Linear(16*16*16, 64),
            nn.ReLU())
        self.layer4 = nn.Sequential(nn.Linear(128, 16*16*16),
            nn.ReLU())
        self.layer5 = nn.Sequential(
            nn.ConvTranspose2d(16, 8, kernel_size=6, stride=2, padding=2,
                               output_padding=0),
            nn.BatchNorm2d(8),
            nn.ReLU())
        self.layer6 = nn.Sequential(
            nn.ConvTranspose2d(8, 1, kernel_size=3, stride=2, padding=1,
                               output_padding=1),
            nn.BatchNorm2d(1)
            )
        self.layer7 = nn.Sequential(
            nn.Sigmoid())

    def forward(self, x, x_force):
        # print(x.shape)
        out = self.layer1(x)
        # print(out.shape)
        out = self.layer2(out)
        # print(out.shape)
        out = out.reshape(out.size(0), -1)
        out = self.layer3(out)
        # Concatonate block force.
        out_force = torch.cat((out, x_force), dim=1)
        # print(out.shape)
        out = self.layer4(out_force)
        out = out.reshape(1, 16, 8, 32)
        out = self.layer5(out)
        # print(out.shape)
        logits = self.layer6(out)
        out = self.layer7(logits)
        # print(out.shape)
        return (logits, out)
