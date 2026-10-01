"""Small CNN used only for single handwritten mark digits (0–9)."""

import cv2
import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as functional
except ImportError:  # The app still works with Tesseract when torch is absent.
    torch = None


if torch:
    class DigitCNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(1, 16, 3, padding=1)
            self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
            self.pool = nn.MaxPool2d(2, 2)
            self.fc1 = nn.Linear(32 * 7 * 7, 64)
            self.fc2 = nn.Linear(64, 10)

        def forward(self, value):
            value = self.pool(functional.relu(self.conv1(value)))
            value = self.pool(functional.relu(self.conv2(value)))
            value = value.reshape(value.size(0), -1)
            return self.fc2(functional.relu(self.fc1(value)))


def load_digit_model(weights_path):
    if torch is None:
        return None
    model = DigitCNN()
    model.load_state_dict(torch.load(weights_path, map_location="cpu", weights_only=True))
    model.eval()
    return model


def _preprocess_digit_crop(gray: np.ndarray) -> np.ndarray:
    """Center digit inside 28x28 bounding box with MNIST-standard aspect ratio and padding."""
    if gray.mean() > 127:
        gray = 255 - gray
    # Binarize to locate digit bounding box
    _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
    coords = cv2.findNonZero(thresh)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        digit_crop = gray[y : y + h, x : x + w]
    else:
        digit_crop = gray

    # Make square with aspect ratio preservation
    h, w = digit_crop.shape[:2]
    max_side = max(h, w)
    square = np.zeros((max_side, max_side), dtype=np.uint8)
    dx = (max_side - w) // 2
    dy = (max_side - h) // 2
    square[dy : dy + h, dx : dx + w] = digit_crop

    # Resize to 20x20 inside 28x28 canvas (4-pixel border padding)
    resized_20 = cv2.resize(square, (20, 20), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((28, 28), dtype=np.uint8)
    canvas[4:24, 4:24] = resized_20
    return canvas


def predict_digit(model, cell_image: np.ndarray) -> dict:
    if model is None or cell_image is None or cell_image.size == 0:
        return {"digit": "", "confidence": 0.0}
    gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY) if cell_image.ndim == 3 else cell_image
    preprocessed = _preprocess_digit_crop(gray)
    tensor = torch.tensor(preprocessed, dtype=torch.float32).div(255).unsqueeze(0).unsqueeze(0)
    with torch.no_grad():
        probabilities = functional.softmax(model(tensor), dim=1)
        confidence, digit = torch.max(probabilities, dim=1)
    return {"digit": str(int(digit.item())), "confidence": round(float(confidence.item()) * 100, 1)}
