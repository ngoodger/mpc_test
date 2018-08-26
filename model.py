from torch import nn
import torch
import numpy as np
import torch.optim as optim
import time

LOSS_MEAN_WINDOW = 1000


class Hyperparameters():
    def __init__(self):
        self.learning_rate = 1e-3
        self.fully_connected_middle_layers = 0

class Model():
    def __init__(self):
        self.criterion = nn.BCEWithLogitsLoss()
        self.cnn_model = ConvNet()
        self.iteration = 0
        self.optimizer = optim.Adam(self.cnn_model.parameters(),
                                    lr=1e-3)
        self.running_loss = []
        print(self.cnn_model)

    def train(self, x, y, x_force):
        self.optimizer.zero_grad()
        logits, out = self.cnn_model.forward(x, x_force)
        loss = self.criterion(logits.reshape([logits.size(0), 32 * 128]),
                              y.reshape([y.size(0), 32 * 128]))
        loss.backward()
        self.running_loss += [loss.data[0]]
        if len(self.running_loss) >= LOSS_MEAN_WINDOW:
            self.running_loss.pop(0)
        if (self.iteration % 100) == 0:
            print('loss: {}'.format(sum(self.running_loss) / LOSS_MEAN_WINDOW))
        self.optimizer.step()
        del loss
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
        self.layer3 = nn.Sequential(
            nn.ConvTranspose2d(16, 8, kernel_size=6, stride=2, padding=2,
                               output_padding=0),
            nn.BatchNorm2d(8),
            nn.ReLU())
        self.layer4 = nn.Sequential(
            nn.ConvTranspose2d(8, 1, kernel_size=3, stride=2, padding=1,
                               output_padding=1),
            nn.BatchNorm2d(1)
            )
        self.layer_force = nn.Sequential(
            nn.Linear(2, 4096),
            nn.ReLU())
        self.layer5 = nn.Sequential(
            nn.Sigmoid())

    def forward(self, x, x_force):
        out_force = self.layer_force(x_force)
        #print(x.shape)
        out1 = self.layer1(x)
        # print(out.shape)
        # start_time = time.time()
        out2 = self.layer2(out1)
        # print("--- %s seconds ---" % (time.time() - start_time))
        # print(out.shape)
        out2_flat = out2.view(out2.size(0), -1)
        # Concatonate block force.
        # out_combined = torch.cat((out_2_flat, out_force), dim=1)
        out_combined = torch.add(out2_flat, out_force)
        # print(out.shape)
        out_combined_image = out_combined.view(out_combined.size(0), 16, 8, 32)
        out3 = torch.add(self.layer3(out_combined_image), out1)
        # print(out.shape)
        logits = torch.add(self.layer4(out3), x)
        out_5 = self.layer5(logits)
        # print(out.shape)
        return (logits, out_5)
