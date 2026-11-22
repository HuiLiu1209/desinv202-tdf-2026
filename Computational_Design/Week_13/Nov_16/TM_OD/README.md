# TM_OD — Everyday Desk Object Classifier

Teachable Machine **Image Project** that recognizes `cup`, `watch`, `phone`, `headphone`, `mouse`, `bottle`.

- **Shareable model:** https://teachablemachine.withgoogle.com/models/nli0F56XE/
- **Training data:** 897 images: webcam recordings, Open Images V7 crops, and other open-source photos.
  `data_key.json` has the per-class breakdown and sources.

```
TM_OD/
├── data_key.json
├── dataset/
│   ├── tm_samples/<class>/  897 images: exactly what the model was trained on (exported from Teachable Machine)
│   ├── train/<class>/       450 Open Images crops (phone, mouse, bottle), also inside tm_samples/
│   ├── holdout/<class>/     90 Open Images crops: never uploaded; for testing
│   └── manifest.json        Open Images ID and crop box for each crop
├── docs/train-contact-sheet.jpg
├── model/                   Teachable Machine export: model.json, weights.bin, metadata.json
└── scripts/build_dataset.py
```

## How the model was made

1. https://teachablemachine.withgoogle.com/train/image
2. Six classes: `cup`, `watch`, `phone`, `headphone`, `mouse`, `bottle`.
3. Webcam: **Hold to Record** with the object held up to the camera (watch, phone, headphone, bottle).
4. Upload: `dataset/train/<class>/` for phone, mouse, bottle, plus extra open-source photos for cup, watch, headphone, phone.
5. **Train Model** (default settings).
6. **Export Model → Tensorflow.js**:
   - **Upload (shareable link) → Upload my model**: gives the link above.
   - **Download → Download my model**: unzipped into `model/` (and copied to `../TM_App/models/od/`).
7. Each class's **⋮ → Download Samples**: unzipped into `dataset/tm_samples/<class>/`.

## Test it

Open `../TM_App` (see its README), **Object classifier** tab → **Test on holdout set**.
The holdout set only covers phone, mouse and bottle.

## Rebuild the Open Images part

```bash
python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt
# put train-bbox-subset.csv, validation-bbox.csv, test-bbox.csv in ann/ (see data_key.json)
.venv/bin/python scripts/build_dataset.py ann dataset
```
