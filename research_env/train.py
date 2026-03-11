import torch
import torch.nn.functional as F
import torch.optim as optim

# Define the model
class MyModel(torch.nn.Module):
    def __init__(self):
        super(MyModel, self).__init__()
        self.linear1 = torch.nn.Linear(20, 10)
        self.linear2 = torch.nn.Linear(10, 1)

    def forward(self, x):
        x = self.linear1(x)
        x = self.linear2(x)
        return x

# Define the optimizer
optimizer = optim.Adam(MyModel.parameters(), lr=0.04)

# Define the loss function
loss_fn = torch.nn.CrossEntropyLoss()

# Define the training loop
for step in range(100):
    print(f"Step: {step}")
    # Move to the next training step
    # Make sure the gradient is not zero
    if step > 0:
        print("Move to the next training step...")
    
    # Create a batch of data
    batch = torch.randn(1, 20, 10, 1)
    # Calculate the loss
    loss = loss_fn(batch)

    # Calculate the gradients
    loss.backward()

    # Update the model
    optimizer.step()

    # Print the loss
    print(f"Loss: {loss.item():.4f}")

    # Print the gradients
    print("Gradients:")
    for param in MyModel.parameters():
        print(f"Parameter: {param.data}")

    # Check for gradient vanishing
    if torch.cuda.is_available():
        print("CUDA available")

    print("Finished training")