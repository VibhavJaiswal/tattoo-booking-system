import torch
import torchvision.transforms as transforms
from PIL import Image
import torchvision.models as models
import os
import pandas as pd

# Load dataset and model paths
MODEL_PATH = "tattoo_classifier.pth"
DATASET_PATH = "BIVTatt-Dataset"
IMAGES_PATH = os.path.join(DATASET_PATH, "images")
LABELS_FILE = os.path.join(DATASET_PATH, "tattoo_labels.csv")

# Load class labels
labels_df = pd.read_csv(LABELS_FILE)
class_names = labels_df["tattoo_style"].unique().tolist()

# Load the trained model
model = models.efficientnet_b0(weights=None)
num_ftrs = model.classifier[1].in_features
model.classifier = torch.nn.Sequential(
    torch.nn.Linear(num_ftrs, 256),
    torch.nn.ReLU(),
    torch.nn.Linear(256, len(class_names))
)

# Load model weights
model.load_state_dict(torch.load(MODEL_PATH))
model.eval()

# Image preprocessing function
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Function to predict tattoo style
def predict_tattoo(image_path):
    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0)
    
    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)
    
    predicted_style = class_names[predicted.item()]
    print(f"Predicted Tattoo Style: {predicted_style}")
    return predicted_style

# Test with a sample image
TEST_IMAGE = os.path.join(IMAGES_PATH, "67_1.jpg")  # Change to an actual image from your dataset
predict_tattoo(TEST_IMAGE)
