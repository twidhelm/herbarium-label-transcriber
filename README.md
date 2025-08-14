# Herbarium Label Transcriber

Batch-transcribe herbarium label images (JPEG/PNG) into a Symbiota-ready Excel file.  
Optimized for NEB (Bessey Herbarium) workflows using the `transcribe_all.py` script.

---

## Why?

Turn hundreds of label photos into clean spreadsheet rows you can import into Symbiota — with opinionated parsing rules tailored to herbarium data and NEB conventions.

---

## Key Features

- Extracts **six-digit handwritten NEB catalog numbers** → `otherCatalogNumbers` (e.g., `NEB Catalog #: 322401`)
- Parses **geographic coordinates** (if present) → `verbatimLatitude`, `verbatimLongitude`
- Detects **elevation** → `verbatimElevation`
- Sends **substrate phrases starting with “On …”** → `substrate` (instead of `habitat`)
- Handles **“Collected by X for Y & Z”** → `collector = X`; `occurrenceRemarks = "for Y & Z"`
- Normalizes **country names** to `"United States"` for U.S. specimens
- Improves capture of **`collectorNumber`**
- Outputs all three scientific-name fields:
  - `sciname` – scientific name **without** author
  - `scientificname` – full scientific name **with** authorship
  - `scientificNameAuthorship` – author name only
- Writes directly to a **Symbiota Excel template** (headers in row 1, field descriptions in row 2, data starting row 3)

---

## Installation

### 1️⃣ Clone & Install Python Dependencies
```bash
git clone https://github.com/YOUR-USERNAME/herbarium-label-transcriber.git
cd herbarium-label-transcriber
pip install -r requirements.txt
```

### 2️⃣ Install Tesseract OCR

This script uses [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) via the `pytesseract` wrapper.  
You must install Tesseract separately:

- **macOS (Homebrew)**  
  ```bash
  brew install tesseract
  ```
- **Ubuntu/Debian**  
  ```bash
  sudo apt-get update && sudo apt-get install -y tesseract-ocr
  ```
- **Windows**  
  1. Download and install from [UB Mannheim builds](https://github.com/UB-Mannheim/tesseract/wiki)  
  2. Add the install folder (e.g., `C:\Program Files\Tesseract-OCR`) to your PATH, or pass `--tesseract-path` when running

Optional: install extra language packs if you work with labels in non-English languages.

---

## Quick Start

```bash
python transcribe_all.py \
  --input ./examples/sample_labels \
  --output ./examples/sample_output.xlsx
```

---

## Usage

```bash
python transcribe_all.py --input INPUT_DIR --output OUTPUT_XLSX [options]
```

**Required:**
- `--input` — folder containing label images (`.jpg`, `.jpeg`, `.png`)
- `--output` — Excel file to write (e.g., `results.xlsx`)

**Common Options:**
- `--tesseract-path PATH` — explicit path to Tesseract binary
- `--languages LANGS` — Tesseract language codes (default: `eng`)
- `--dpi N` — override/assume DPI for OCR preprocessing (e.g., `300`)
- `--threads N` — number of parallel workers (e.g., `4` or `auto`)
- `--limit N` — process at most N images (for testing)
- `--verbose` — print debug info for parsing
- `--skip-existing` — skip images already in the output file

---

## Output Schema (Symbiota Columns)

The generated Excel file matches Symbiota’s template:

- **Row 1:** Column headers
- **Row 2:** Field descriptions
- **Row 3+:** Data

**Notable fields:**
- `sciname` — no author
- `scientificname` — full name + authorship
- `scientificNameAuthorship` — author only
- `otherCatalogNumbers` — e.g., `NEB Catalog #: 322401`
- `verbatimLatitude`, `verbatimLongitude` — decimal degrees or verbatim
- `verbatimElevation`
- `substrate` — “On …” phrases
- `occurrenceRemarks` — e.g., “for Y & Z”
- `collector`, `collectorNumber`
- `country` — normalized to `United States` when applicable

---

## Example Repo Structure

```
herbarium-label-transcriber/
├── transcribe_all.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── data/                   # optional reference data
├── examples/
│   ├── sample_labels/      # sample JPEG/PNG labels
│   └── sample_output.xlsx  # example Symbiota-formatted output
└── tests/
    └── test_transcribe.py  # optional tests
```

---

## Testing

- Add images to `examples/sample_labels/`
- Run the Quick Start example above
- (Optional) Create unit tests mapping OCR text → expected parsed fields

---

## Troubleshooting

- **`tesseract: not found`** — install Tesseract and/or pass `--tesseract-path`
- **Poor handwriting OCR** — improve image resolution/lighting or add handwriting-specific models
- **Excel won’t import** — ensure rows 1–2 match Symbiota template (this script sets them automatically)

---

## Contributing

Pull requests welcome! Please:
1. Open an issue describing your change
2. Add/adjust tests for parsing rules
3. Keep the README updated

---

## License

MIT — see [`LICENSE`](LICENSE)

---

## Acknowledgments

Built for the Bessey Herbarium (NEB) data curation workflow and Symbiota import conventions.
