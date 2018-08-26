import pickle
import torch
from torch.utils.data import DataLoader
import block_sys
import time
import model
BATCH_SIZE = 32
EPOCHS = 5


s0 = pickle.load(open("s0.p", "rb"))
force = pickle.load(open("force.p", "rb"))
s1 = pickle.load(open("s1.p", "rb"))

s0_tensor = torch.from_numpy(s0)
force_tensor = torch.from_numpy(force)
s1_tensor = torch.from_numpy(s1)
samples_dataset = torch.utils.data.TensorDataset(s0_tensor,
                                                 force_tensor, s1_tensor)

dataloader = DataLoader(samples_dataset, batch_size=BATCH_SIZE,
                        shuffle=False, num_workers=4)

my_model = model.Model()
for epoch_idx in range(EPOCHS):
    print("epoch: {}".format(epoch_idx))
    for batch_idx, data in enumerate(dataloader):
        s0_batch = data[0]
        force_batch = data[1]
        s1_batch = data[2]
        y1 = my_model.train(s0_batch - 0.5, s1_batch,
                            force_batch / block_sys.FORCE_SCALE)
