"""
PlantVillage dataset hazırlama — train/val/test split.

Kullanım:
    python prepare_dataset.py \
        --src "C:/Users/durha/Downloads/plantvillage dataset/color" \
        --dst ./data/PlantVillage \
        --train 0.8 --val 0.1 --test 0.1

Çıktı dizin yapısı:
    data/PlantVillage/
        train/ClassName/*.jpg
        val/ClassName/*.jpg
        test/ClassName/*.jpg
"""

import argparse
import os
import random
import shutil
from pathlib import Path


def prepare(src: str, dst: str, train_ratio: float, val_ratio: float, seed: int = 42):
    src_path = Path(src)
    dst_path = Path(dst)
    test_ratio = 1.0 - train_ratio - val_ratio

    if not src_path.exists():
        raise FileNotFoundError(f"Kaynak dizin bulunamadı: {src_path}")

    classes = sorted([d for d in src_path.iterdir() if d.is_dir()])
    if not classes:
        raise ValueError(f"Sınıf klasörü bulunamadı: {src_path}")

    print(f"Bulunan sınıf sayısı: {len(classes)}")
    print(f"Hedef dizin: {dst_path}")
    print(f"Split: train={train_ratio:.0%}  val={val_ratio:.0%}  test={test_ratio:.0%}\n")

    random.seed(seed)
    total_copied = 0

    for cls_dir in classes:
        images = sorted([
            f for f in cls_dir.iterdir()
            if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        ])

        if not images:
            print(f"  ATLA (görüntü yok): {cls_dir.name}")
            continue

        random.shuffle(images)
        n = len(images)
        n_train = int(n * train_ratio)
        n_val   = int(n * val_ratio)

        splits = {
            "train": images[:n_train],
            "val":   images[n_train : n_train + n_val],
            "test":  images[n_train + n_val :],
        }

        for split, files in splits.items():
            out_dir = dst_path / split / cls_dir.name
            out_dir.mkdir(parents=True, exist_ok=True)
            for f in files:
                shutil.copy2(f, out_dir / f.name)
            total_copied += len(files)

        print(f"  {cls_dir.name:<45} → train:{len(splits['train'])}  val:{len(splits['val'])}  test:{len(splits['test'])}")

    print(f"\nTamamlandı. Toplam kopyalanan: {total_copied} görüntü")
    print(f"Eğitim için: python train.py --data-dir {dst_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PlantVillage dataset split")
    parser.add_argument("--src",   default=r"C:/Users/durha/Downloads/plantvillage dataset/color",
                        help="Ham dataset dizini (sınıf klasörleri içeren)")
    parser.add_argument("--dst",   default="./data/PlantVillage",
                        help="Çıktı dizini")
    parser.add_argument("--train", type=float, default=0.8)
    parser.add_argument("--val",   type=float, default=0.1)
    parser.add_argument("--seed",  type=int,   default=42)
    args = parser.parse_args()

    if args.train + args.val >= 1.0:
        raise ValueError("train + val toplamı 1.0'dan küçük olmalı")

    prepare(args.src, args.dst, args.train, args.val, args.seed)
