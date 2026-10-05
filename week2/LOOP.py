import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets,transforms
from torch.utils.data import DataLoader

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

tf=transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])
train_dataset = datasets.MNIST(root='./data',train=True,transform=tf,download=True)
test_dataset = datasets.MNIST(root='./data',train=False,transform=tf,download=True)
train_loader = DataLoader(dataset=train_dataset,batch_size=64,shuffle=True)
test_loader = DataLoader(dataset=test_dataset,batch_size=64,shuffle=False)

class Net(nn.Module):
    def __init__(self):
        super(Net,self).__init__()
        self.net = nn.Sequential(
            nn.Flatten(),
            nn.Linear(28*28,128),
            nn.ReLU(),
            nn.Linear(128,10),
        )
    def forward(self,x):
        x = self.net(x)
        return x

model = Net().to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(),lr=0.001)

def evaluate():
    model.eval()
    correct=total=0
    with torch.no_grad():
        for x,y in test_loader:
            x=x.to(device)
            y=y.to(device)
            pred=model(x).argmax(dim=1)
            correct += (pred==y).sum().item()
            total += y.size(0)
    return correct / total

for epoch in range(3):
    model.train()
    for x,y in train_loader:
        x=x.to(device)
        y=y.to(device)
        optimizer.zero_grad()
        pred=model(x)
        loss=criterion(pred,y)
        loss.backward()
        optimizer.step()
    acc=evaluate()
    print(f"Epoch {epoch+1}: test Accuracy: {acc}")
torch.save(model.state_dict(), "model.pth")
#          ↑★ 只保存【参数】，不保存模型结构
print("模型已保存: model.pth")