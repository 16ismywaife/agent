import torch
import torch.nn as nn
from torchvision import datasets,transforms

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

model = Net()
model.load_state_dict(torch.load('./model.pth',map_location=torch.device('cpu')))
model.eval()

tf=transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])
test_dataset = datasets.MNIST(root='./data',train=False,transform=tf,download=True)

x,y=test_dataset[0]
with torch.no_grad():
    pred=model(x.unsqueeze(0)).argmax(dim=1).item()
print(f"pred: {pred}, label: {y}")