import torch
from torchvision import datasets,transforms
from torch.utils.data import DataLoader

trans=transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_ds=datasets.MNIST(root='./data',train=True,download=True,transform=trans)
test_ds=datasets.MNIST(root='./data',train=False,download=True,transform=trans)

print(len(train_ds))
print(len(test_ds))

train_loader = DataLoader(dataset=train_ds,batch_size=32,shuffle=True)
test_loader = DataLoader(dataset=test_ds,batch_size=32,shuffle=False)
#                                                        ↑★ 测试集不需要打乱：
#                                                        评估只看总体准确率，
#                                                        顺序固定才能让结果可复现

x,y=next(iter(train_loader))
print(x.shape)
print(y.shape)
