# Herbarium Label Transcriber

Batch-transcribe herbarium label **JPEG** images into a **Symbiota-ready Excel** file using the OpenAI API.  
Optimized for NEB (Bessey Herbarium) workflows with a Symbiota template that keeps **row 1 = headers** and **row 2 = field descriptions**.

---

## What this does

- Reads **all `.jpg`/`.jpeg` images** from a folder (default: `images/`)
- Uses **OpenAI GPT** to extract structured fields from the label text
- Adds some **rule-based cleanups** (e.g., NEB catalog numbers, coordinates conversion)
- Preserves the **first two rows** from your Symbiota template (headers + descriptions)
- Writes results to an Excel file (default: `Symbiota_Transcriptions_Output.xlsx`)

> The script currently expects GPT to return a Python-dict-like block; it parses that and fills Symbiota columns, plus a few convenience columns such as `rawGPTOutput` and the three scientific name variants (`sciname`, `scientificname`, `scientificNameAuthorship`).

---

## Requirements

- Python 3.10+
- Packages (see `requirements.txt`):
  - `openai`, `pandas`, `tqdm`, `python-dotenv`

---

## Installation

```bash
git clone https://github.com/YOUR-USERNAME/herbarium-label-transcriber.git
cd herbarium-label-transcriber
pip install -r requirements.txt
```

---

## Quick Start (with included examples)

After installing requirements, you can test the script using the provided example files.

1. **Add your OpenAI API key**  
   Create a `.env` file in the project root containing:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

2. **Run with examples**  
   The script defaults to looking for images in `images/` and a template in the project root.  
   For the examples, either:

   **Option A — Copy example files into expected locations**:
   ```bash
   cp examples/sample_labels/test_label.jpg images/
   cp examples/NewUploadTemplateForCollectors.xlsx .
   python transcribe_all_jpeg_v1.0.py
   ```

   **Option B — Point script directly to examples**  
   Edit the constants at the top of `transcribe_all_jpeg_v1.0.py`:
   ```python
   IMAGE_FOLDER = "examples/sample_labels"
   TEMPLATE_PATH = "examples/NewUploadTemplateForCollectors.xlsx"
   ```
   Then run:
   ```bash
   python transcribe_all_jpeg_v1.0.py
   ```

3. **Check the output**  
   When finished, the script will create:
   ```
   Symbiota_Transcriptions_Output.xlsx
   ```
   in the project root, containing the parsed label data from the example image.

---

### Cloning the Repository (SSH)
If you have your SSH key set up with GitHub, you can clone this repository with:

```bash
git clone git@github.com:twidhelm/herbarium-label-transcriber.git

---

## Set up your OpenAI API key

Create a file named `.env` in the project root:

```
OPENAI_API_KEY=your_api_key_here
```

The script uses `python-dotenv` to load this automatically.

---

## Prepare your inputs

- Put your label images in: `images/` (you can change this; see **Configuration** below)
- Put your Symbiota Excel template in the repo root and name it:
  - `NewUploadTemplateForCollectors.xlsx` (default expected by the script)

**Template assumptions**
- Row 1: column headers
- Row 2: field descriptions  
The script preserves these two rows when writing output.

---

## Run it

Use your file’s actual name. If you rename your script to `transcribe_all.py`, use that instead.

```bash
python transcribe_all_jpeg_v1.0.py
```

When it’s done, you’ll see:

```
✅ Done. Transcriptions saved to Symbiota_Transcriptions_Output.xlsx
```

---

## Configuration (edit at the top of the script)

Open the script and adjust these constants to your preference:

```python
IMAGE_FOLDER = "images"                       # Where your .jpg/.jpeg files are
TEMPLATE_PATH = "NewUploadTemplateForCollectors.xlsx"  # Your Symbiota template
OUTPUT_PATH = "Symbiota_Transcriptions_Output.xlsx"    # Where to write results
MODEL = "gpt-4o"                              # OpenAI model name
```

> The script currently processes only `.jpg`/`.jpeg`. Add `".png"` to the filter if needed.

---

## What gets parsed & cleaned

- **NEB catalog numbers**: finds a 6-digit number (starting 3–9) and writes to  
  `otherCatalogNumbers` as `NEB Catalog #: 3xxxxx`
- **Coordinates**: detects DMS (e.g., `41°...N 96°...W`) and converts to decimal degrees; also handles decimal forms when present, filling `verbatimLatitude` and `verbatimLongitude`
- **Catalog number from filename**: adds the filename (without extension) to `catalogNumber`
- **Raw GPT output**: stored in `rawGPTOutput` for auditing
- **Scientific names**: ensures `sciname`, `scientificname`, `scientificNameAuthorship` columns exist in the output

> If GPT output can’t be parsed as a dict, the script falls back to dumping the model’s text into `occurrenceRemarks` so you don’t lose information.

---

## Output

- An Excel file (default: `Symbiota_Transcriptions_Output.xlsx`)
- First two rows are copied from your template; data begin at row 3

---

## Example workflow

1. Place 10 label photos in `images/`
2. Put `NewUploadTemplateForCollectors.xlsx` in the repo root
3. Create `.env` with your `OPENAI_API_KEY`
4. Run `python transcribe_all_jpeg_v1.0.py`
5. Open `Symbiota_Transcriptions_Output.xlsx` and verify fields

---

## Troubleshooting

- **OpenAI authentication error**  
  Ensure `.env` exists and contains `OPENAI_API_KEY=...`
- **No images found**  
  Confirm your files end with `.jpg` or `.jpeg` and `IMAGE_FOLDER` is correct
- **Template read error**  
  Check `TEMPLATE_PATH` and verify the file is a valid `.xlsx`
- **Parsed fields missing**  
  See `rawGPTOutput` column to inspect the model’s raw response; adjust prompt or post-processing rules as needed

---

## Contributing

- Open an issue describing your change
- Keep README in sync with script behavior
- (Optional) add tests for parsing rules

---

## License

MIT — see `LICENSE`.
