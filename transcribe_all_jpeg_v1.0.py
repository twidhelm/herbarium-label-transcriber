import os
import base64
import openai
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
import ast
import re

# === Load API Key ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Configuration ===
IMAGE_FOLDER = "images"
TEMPLATE_PATH = "NewUploadTemplateForCollectors.xlsx"
OUTPUT_PATH = "Symbiota_Transcriptions_Output.xlsx"
MODEL = "gpt-4o"
TARGET_COLUMN = "occurrenceRemarks"

# === Load Template (preserve first two rows) ===
template_df = pd.read_excel(TEMPLATE_PATH, header=0)
columns = template_df.columns.tolist()
for extra_col in ["sciname", "scientificname", "scientificNameAuthorship"]:
    if extra_col not in columns:
        columns.append(extra_col)
static_rows = template_df.iloc[:2].copy()
output_df = pd.DataFrame(columns=columns)

# === Helper: DMS to Decimal ===
def dms_to_decimal(dms_str):
    dms_str = dms_str.replace("’", "'").replace("″", '"').replace("”", '"').replace("“", '"')
    dms_pattern = r'(\d{1,3})\u00b0(\d{1,2})\'(\d{1,2}(?:\.\d+)?)"?([NSEW])'
    match = re.match(dms_pattern, dms_str.strip())
    if not match:
        return None
    degrees, minutes, seconds, direction = match.groups()
    decimal = float(degrees) + float(minutes)/60 + float(seconds)/3600
    if direction in ['S', 'W']:
        decimal *= -1
    return round(decimal, 6)

# === Post-processing ===
def clean_and_correct_fields(parsed, content, filename):
    cleaned = parsed.copy()

    neb_match = re.search(r"\b(3|4|5|6|7|8|9)\d{5}\b", content)
    if neb_match:
        cleaned["otherCatalogNumbers"] = f"NEB Catalog #: {neb_match.group(0)}"

    # Extract DMS or decimal coords from anywhere in content
    dms_pair_pattern = r'(\d{1,3}\u00b0\d{1,2}\'\d{1,2}(?:\.\d+)?"?[NS])[^\d]+(\d{1,3}\u00b0\d{1,2}\'\d{1,2}(?:\.\d+)?"?[EW])'
    dms_match = re.search(dms_pair_pattern, content)
    if dms_match:
        lat_dms = dms_match.group(1)
        lon_dms = dms_match.group(2)
        lat = dms_to_decimal(lat_dms)
        lon = dms_to_decimal(lon_dms)
        cleaned["verbatimLatitude"] = lat
        cleaned["verbatimLongitude"] = lon
    else:
        coords = re.findall(r"[-+]?\d{1,3}\.\d{3,}", content)
        if len(coords) >= 2:
            cleaned["verbatimLatitude"] = coords[0]
            cleaned["verbatimLongitude"] = coords[1]

    elev_match = re.search(r"(\d{2,5})\s?m", content.lower())
    if elev_match:
        cleaned["verbatimElevation"] = f"{elev_match.group(1)} m"

    if "habitat" in cleaned and cleaned["habitat"].strip().startswith("On"):
        cleaned["substrate"] = cleaned["habitat"]
        cleaned["habitat"] = ""

    cb_match = re.search(r"Collected by (.+?) for (.+)", content)
    if cb_match:
        cleaned["collector"] = cb_match.group(1).strip()
        cleaned["occurrenceRemarks"] = f"for {cb_match.group(2).strip()}"

    country = cleaned.get("country", "").lower()
    if country in ["usa", "u.s.a", "united states", ""]:
        cleaned["country"] = "United States"

    if not cleaned.get("collectorNumber"):
        cn_match = re.search(r"(No\.?|#)\s?(\d+)", content)
        if cn_match:
            cleaned["collectorNumber"] = cn_match.group(2)

    return cleaned

# === Process Each Image ===
image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".jpg", ".jpeg"))]
print(f"Processing {len(image_files)} images...\n")

for filename in tqdm(image_files, desc="Transcribing"):
    filepath = os.path.join(IMAGE_FOLDER, filename)

    with open(filepath, "rb") as image_file:
        image_bytes = image_file.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    try:
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "This is a herbarium specimen label. Transcribe and parse the information from the label.\n\n"
                                "The most important field is the scientific name that the specimen was identified as. It is usually handwritten or typed in italics near the top of the label. Extract that exactly as written, including author name if present. Example: 'Amblystegium serpens (Hedw.) Schimp.'.\n\n"
                                "Parse the following fields exactly:\n"
                                "- sciname (just the genus and species, no authorship)\n"
                                "- scientificname (full name including authorship)\n"
                                "- scientificNameAuthorship (author portion only)\n\n"
                                "If no scientific name is visible on the label, leave those three fields blank.\n\n"
                                "Coordinates may be embedded anywhere in the label. Extract latitude and longitude in either decimal degrees or degrees/minutes/seconds (DMS).\n"
                                "If DMS is present, put that into verbatimLatitude/verbatimLongitude and convert to decimal degrees for decimalLatitude/decimalLongitude.\n\n"
                                "Also extract the following Symbiota fields:\n"
                                "- catalogNumber\n"
                                "- collector\n"
                                "- collectorNumber\n"
                                "- associatedCollectors\n"
                                "- eventDate\n"
                                "- verbatimEventDate\n"
                                "- country\n"
                                "- stateProvince\n"
                                "- county\n"
                                "- locality\n"
                                "- habitat\n"
                                "- substrate\n"
                                "- occurrenceRemarks\n"
                                "- identifiedBy\n"
                                "- DateIdentified\n\n"
                                "Return results as a Python dictionary. Leave fields blank if not present."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                        }
                    ]
                }
            ],
            max_tokens=1000
        )

        content = response.choices[0].message.content
        print(f"\n--- Raw GPT output for {filename} ---\n{content}\n--- End ---\n")

        try:
            cleaned_text = content.strip().strip("```").replace("python", "").strip()
            match = re.search(r"{.*}", cleaned_text, re.DOTALL)
            if match:
                parsed = ast.literal_eval(match.group(0))
            else:
                raise ValueError("No dictionary found.")
        except Exception as e:
            print(f"❌ Failed to parse {filename}: {e}")
            parsed = {TARGET_COLUMN: content}

        parsed["catalogNumber"] = os.path.splitext(filename)[0]
        parsed["rawGPTOutput"] = content

        cleaned = clean_and_correct_fields(parsed, content, filename)

        row = {col: cleaned.get(col, "") for col in columns}
        output_df = pd.concat([output_df, pd.DataFrame([row])], ignore_index=True)

    except Exception as e:
        print(f"❌ Error with {filename}: {e}")

# === Combine static header + results and save ===
final_df = pd.concat([static_rows, output_df], ignore_index=True)
final_df.to_excel(OUTPUT_PATH, index=False)
print(f"\n✅ Done. Transcriptions saved to {OUTPUT_PATH}")
