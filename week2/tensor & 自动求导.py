import torch

torch.manual_seed(1)
x=torch.linspace(-1,1,50).unsqueeze(1)
y=2*x+1

w=torch.tensor([0.0],requires_grad=True)
b=torch.tensor([0.0],requires_grad=True)
lr=0.1

for i in range(200):
    y_hat=x*w+b
    loss=((y_hat-y)**2).mean()
    loss.backward()
    with torch.no_grad():
        w-=lr*w.grad
        b-=lr*b.grad
    w.grad.zero_()
    b.grad.zero_()

print(w.item(),b.item())