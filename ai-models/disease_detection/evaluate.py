"""
Eğitilmiş modeli test seti üzerinde değerlendirir, confusion matrix üretir.

Kullanım:
    python evaluate.py --data-dir ./data/PlantVillage --weights best_model.pth
"""

import argparse
import json

import torch
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import torch.nn as nn
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def evaluate(args):
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    test_ds = datasets.ImageFolder(f"{args.data_dir}/test", transform)
    loader = DataLoader(test_ds, batch_size=32, shuffle=False, num_workers=4)

    num_classes = len(test_ds.classes)
    model = models.efficientnet_b3(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(nn.Dropout(0.3), nn.Linear(in_features, num_classes))
    model.load_state_dict(torch.load(args.weights, map_location=DEVICE))
    model.to(DEVICE).eval()

    all_preds, all_labels = [], []
    with torch.no_grad():
        for imgs, labels in loader:
            imgs = imgs.to(DEVICE)
            outputs = model(imgs)
            preds = outputs.argmax(1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())

    acc = np.mean(np.array(all_preds) == np.array(all_labels))
    print(f"\nTop-1 Accuracy: {acc:.4f} ({acc*100:.2f}%)")
    print("\nClassification Report:")
    print(classification_report(all_labels, all_preds, target_names=test_ds.classes))

    # CI kontrolü
    target_acc = 0.90
    if acc < target_acc:
        print(f"⚠️  Accuracy {acc:.4f} < hedef {target_acc} — CI başarısız!")
        exit(1)
    else:
        print(f"✓ Accuracy hedef ({target_acc}) aşıldı.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="./data/PlantVillage")
    parser.add_argument("--weights", default="best_model.pth")
    args = parser.parse_args()
    evaluate(args)
