"""Build a Teachable Machine image dataset of everyday desk objects
(phone, mouse, bottle) from Google's Open Images V7.

Open Images gives bounding boxes. For each photo we take the largest box of
the class, expand it to a padded square, crop and resize to 224x224, so the
object fills the frame the way it does when you hold it up to a webcam.
Training crops come from the Open Images *train* split and holdout crops from
*validation/test*, so no photo is used twice.

Usage:
    python build_dataset.py <annotations dir> <output dataset dir>

<annotations dir> must contain:
    train-bbox-subset.csv   rows of oidv6-train-annotations-bbox.csv for the 3 classes
    validation-bbox.csv     https://storage.googleapis.com/openimages/v5/validation-annotations-bbox.csv
    test-bbox.csv           https://storage.googleapis.com/openimages/v5/test-annotations-bbox.csv
"""

import csv
import io
import json
import random
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

CLASSES = {"/m/050k8": "phone", "/m/020lf": "mouse", "/m/04dr76w": "bottle"}
TRAIN_PER_CLASS = 150
HOLDOUT_PER_CLASS = 30
MIN_AREA = 0.04   # box must cover >= 4% of the photo (skip tiny background objects)
PAD = 0.15
OUT_SIZE = 224
SEED = 42
IMAGE_URL = "https://open-images-dataset.s3.amazonaws.com/{split}/{image_id}.jpg"


def candidates(csv_paths, split_of):
    """Largest usable box per (class, image)."""
    best = {}
    for path in csv_paths:
        for r in csv.DictReader(open(path)):
            name = CLASSES.get(r["LabelName"])
            if not name or r["IsGroupOf"] == "1" or r["IsDepiction"] == "1":
                continue
            box = tuple(float(r[k]) for k in ("XMin", "YMin", "XMax", "YMax"))
            area = (box[2] - box[0]) * (box[3] - box[1])
            if area < MIN_AREA:
                continue
            key = (name, r["ImageID"])
            if key not in best or area > best[key][1]:
                best[key] = (split_of(path), area, box)
    per_class = {name: [] for name in CLASSES.values()}
    for (name, image_id), (split, _, box) in sorted(best.items()):
        per_class[name].append((image_id, split, box))
    return per_class


def fetch_crop(item):
    image_id, split, (x1, y1, x2, y2) = item
    try:
        url = IMAGE_URL.format(split=split, image_id=image_id)
        with urllib.request.urlopen(url, timeout=30) as resp:
            im = Image.open(io.BytesIO(resp.read())).convert("RGB")
    except Exception:
        return None
    w, h = im.size
    x1, x2, y1, y2 = x1 * w, x2 * w, y1 * h, y2 * h
    side = min(max(x2 - x1, y2 - y1) * (1 + 2 * PAD), w, h)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    left = min(max(cx - side / 2, 0), w - side)
    top = min(max(cy - side / 2, 0), h - side)
    box = (int(left), int(top), int(left + side), int(top + side))
    return im.crop(box).resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS), box


def export(per_class, out_dir, split_name, count, rng, manifest):
    for name, items in per_class.items():
        rng.shuffle(items)
        folder = out_dir / split_name / name
        folder.mkdir(parents=True, exist_ok=True)
        saved = 0
        pool = items[: int(count * 1.3) + 10]  # spare candidates in case a download fails
        with ThreadPoolExecutor(max_workers=16) as ex:
            for item, result in zip(pool, ex.map(fetch_crop, pool)):
                if result is None or saved >= count:
                    continue
                crop, box = result
                out_name = f"{name}_{saved:03d}.jpg"
                crop.save(folder / out_name, quality=92)
                manifest.append({"file": f"{split_name}/{name}/{out_name}", "label": name,
                                 "open_images_id": item[0], "open_images_split": item[1],
                                 "crop_xyxy_px": list(box)})
                saved += 1
        print(f"{split_name:8s} {name:7s} {saved:4d}  (candidates {len(items)})")


def main():
    ann, out = Path(sys.argv[1]), Path(sys.argv[2])
    rng = random.Random(SEED)
    manifest = []
    train = candidates([ann / "train-bbox-subset.csv"], lambda p: "train")
    holdout = candidates([ann / "validation-bbox.csv", ann / "test-bbox.csv"],
                         lambda p: "validation" if "validation" in p.name else "test")
    export(train, out, "train", TRAIN_PER_CLASS, rng, manifest)
    export(holdout, out, "holdout", HOLDOUT_PER_CLASS, rng, manifest)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))


if __name__ == "__main__":
    main()
