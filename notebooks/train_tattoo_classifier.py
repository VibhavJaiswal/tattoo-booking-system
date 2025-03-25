import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.models as models
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import pandas as pd
import os

# Load dataset information
DATASET_PATH = "BIVTatt-Dataset"
LABELS_FILE = os.path.join(DATASET_PATH, "tattoo_labels.csv")
IMAGES_PATH = os.path.join(DATASET_PATH, "images")

# Load tattoo labels
labels_df = pd.read_csv(LABELS_FILE)
class_names = labels_df["tattoo_style"].unique().tolist()
complexity_levels = labels_df["complexity_level"].unique().tolist()

# Create mappings
style_to_idx = {style: i for i, style in enumerate(class_names)}
complexity_to_idx = {level: i for i, level in enumerate(complexity_levels)}

# Custom dataset class
class TattooDataset(Dataset):
    def __init__(self, labels_df, transform=None):
        self.labels_df = labels_df
        self.transform = transform
    
    def __len__(self):
        return len(self.labels_df)
    
    def __getitem__(self, idx):
        img_name = os.path.join(IMAGES_PATH, self.labels_df.iloc[idx]["image_name"])
        image = Image.open(img_name).convert("RGB")
        style_label = style_to_idx[self.labels_df.iloc[idx]["tattoo_style"]]
        complexity_label = complexity_to_idx[self.labels_df.iloc[idx]["complexity_level"]]
        
        if self.transform:
            image = self.transform(image)
        
        return image, torch.tensor(style_label), torch.tensor(complexity_label)

# Image transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Create dataset & dataloaders
dataset = TattooDataset(labels_df, transform=transform)
dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

# Load EfficientNet Model
model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
num_ftrs = model.classifier[1].in_features
model.classifier = nn.Sequential(
    nn.Linear(num_ftrs, 256),
    nn.ReLU(),
    nn.Linear(256, len(class_names))
)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Training loop
num_epochs = 15  # Increased number of epochs for better training
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    for images, style_labels, _ in dataloader:
        images, style_labels = images.to(device), style_labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, style_labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += style_labels.size(0)
        correct += (predicted == style_labels).sum().item()
    
    accuracy = 100 * correct / total
    print(f"Epoch {epoch+1}/{num_epochs}, Loss: {running_loss/len(dataloader):.4f}, Accuracy: {accuracy:.2f}%")

# Save trained model
MODEL_SAVE_PATH = "tattoo_classifier.pth"
torch.save(model.state_dict(), MODEL_SAVE_PATH)
print(f"Model saved to {MODEL_SAVE_PATH}")

print(f"Number of classes used during training: {len(class_names)}")
