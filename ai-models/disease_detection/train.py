"""
EfficientNet-B3 — PlantVillage bitki hastalığı tespiti eğitimi.

Kullanım:
    python train.py --data-dir ./data/PlantVillage --epochs 30 --batch-size 32

Dataset indirme:
    https://www.kaggle.com/datasets/emmarex/plantdisease
    (ya da: kaggle datasets download -d emmarex/plantdisease)

Dizin yapısı beklentisi:
    data/PlantVillage/
        train/
            Tomato_Late_blight/   ← sınıf adı klasör adından gelir
                img1.jpg
                ...
            Tomato_healthy/
                ...
        val/
            ...
"""

import argparse
import os

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

try:
    from tqdm import tqdm
except ImportError:
    # tqdm yoksa basit bir sarmalayıcı kullan
    def tqdm(iterable, **kwargs):
        desc = kwargs.get("desc", "")
        total = kwargs.get("total", "?")
        for i, item in enumerate(iterable, 1):
            if i % 50 == 0 or i == total:
                print(f"\r  {desc} [{i}/{total}]", end="", flush=True)
            yield item
        print()

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_transforms(train: bool):
    if train:
        return transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3),
            transforms.RandomRotation(30),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])


def build_model(num_classes: int) -> nn.Module:
    model = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.IMAGENET1K_V1)
    # Son katmanı değiştir
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, num_classes),
    )
    return model


def train(args):
    train_ds = datasets.ImageFolder(os.path.join(args.data_dir, "train"), get_transforms(True))
    val_ds = datasets.ImageFolder(os.path.join(args.data_dir, "val"), get_transforms(False))

    num_classes = len(train_ds.classes)
    print(f"Sınıf sayısı: {num_classes}")
    print(f"Eğitim: {len(train_ds)} | Validasyon: {len(val_ds)}")

    # Sınıf etiketlerini kaydet
    import json
    with open("class_labels.json", "w", encoding="utf-8") as f:
        json.dump(train_ds.classes, f, ensure_ascii=False, indent=2)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=4, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=4)

    model = build_model(num_classes).to(DEVICE)

    # Faz 1: Sadece classifier eğit (5 epoch)
    for param in model.features.parameters():
        param.requires_grad = False

    optimizer = AdamW(model.classifier.parameters(), lr=1e-3, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    best_acc = 0.0
    for epoch in range(min(5, args.epochs)):
        _train_epoch(model, train_loader, optimizer, criterion, epoch, "Feature extract")

    # Faz 2: Tüm ağı fine-tune et
    for param in model.parameters():
        param.requires_grad = True

    optimizer = AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs - 5)

    for epoch in range(5, args.epochs):
        _train_epoch(model, train_loader, optimizer, criterion, epoch, "Fine-tune")
        acc = _validate(model, val_loader, criterion, epoch)
        scheduler.step()

        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), "best_model.pth")
            print(f"  ✓ Best model kaydedildi: {acc:.4f}")

    print(f"\nEğitim tamamlandı. En iyi accuracy: {best_acc:.4f}")
    print("Sonraki adım: export_onnx.py ile ONNX'e çevirin.")


def _train_epoch(model, loader, optimizer, criterion, epoch, phase):
    model.train()
    total_loss, correct, total = 0, 0, 0
    bar = tqdm(loader, desc=f"[{phase}] Epoch {epoch+1}", total=len(loader), leave=True)
    for imgs, labels in bar:
        imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * imgs.size(0)
        correct += (outputs.argmax(1) == labels).sum().item()
        total += imgs.size(0)
        bar.set_postfix(loss=f"{total_loss/total:.4f}", acc=f"{correct/total:.4f}")
    print(f"[{phase}] Epoch {epoch+1} | Loss: {total_loss/total:.4f} | Acc: {correct/total:.4f}")


def _validate(model, loader, criterion, epoch):
    model.eval()
    total_loss, correct, total = 0, 0, 0
    with torch.no_grad():
        for imgs, labels in loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * imgs.size(0)
            correct += (outputs.argmax(1) == labels).sum().item()
            total += imgs.size(0)
    acc = correct / total
    print(f"  [Val] Epoch {epoch+1} | Loss: {total_loss/total:.4f} | Acc: {acc:.4f}")
    return acc


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="./data/PlantVillage")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    train(args)
