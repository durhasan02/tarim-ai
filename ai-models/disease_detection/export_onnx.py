"""
Eğitilmiş PyTorch modelini ONNX formatına çevirir.

Kullanım:
    python export_onnx.py --weights best_model.pth --labels class_labels.json
"""

import argparse
import json

import torch
import torch.nn as nn
from torchvision import models


def build_model(num_classes: int) -> nn.Module:
    model = models.efficientnet_b3(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, num_classes),
    )
    return model


def export(args):
    with open(args.labels, "r", encoding="utf-8") as f:
        labels = json.load(f)

    num_classes = len(labels)
    model = build_model(num_classes)
    model.load_state_dict(torch.load(args.weights, map_location="cpu"))
    model.eval()

    import os
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    dummy = torch.randn(1, 3, 224, 224)

    torch.onnx.export(
        model,
        (dummy,),
        args.output,
        input_names=["image"],
        output_names=["logits"],
        opset_version=18,
    )

    print(f"ONNX modeli kaydedildi: {args.output}")
    print(f"Sınıf sayısı: {num_classes}")

    # Metadata dosyası
    meta = {"num_classes": num_classes, "labels": labels, "input_size": 224}
    with open(args.output.replace(".onnx", "_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print("Metadata kaydedildi.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", default="best_model.pth")
    parser.add_argument("--labels", default="class_labels.json")
    parser.add_argument("--output", default="../../ai-service/models/disease_model.onnx")
    args = parser.parse_args()
    export(args)
