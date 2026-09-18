"""
OCR and Computer Vision parser for 92pkr / Win Go game history screenshots.
Extracts Period / Issue numbers, winning digits (0-9), Big/Small labels, and colors.
"""
import os
import re
import cv2
import numpy as np
import pytesseract
from PIL import Image
from typing import List, Dict, Any

# Configure tesseract path
TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_EXE):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE


class ImageHistoryParser:
    def __init__(self):
        pass

    def infer_properties_from_number(self, num: int) -> Dict[str, str]:
        """
        In 92pkr / Win Go:
        0: Violet & Red, Small
        1: Green, Small
        2: Red, Small
        3: Green, Small
        4: Red, Small
        5: Violet & Green, Big
        6: Red, Big
        7: Green, Big
        8: Red, Big
        9: Green, Big
        """
        size = "Big" if num >= 5 else "Small"
        if num == 0:
            color = "Violet"  # Also Red
        elif num == 5:
            color = "Violet"  # Also Green
        elif num in [1, 3, 7, 9]:
            color = "Green"
        else:
            color = "Red"
        return {"size": size, "color": color}

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Loads image and produces optimized thresholded image for OCR.
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image at {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Upscale if image is relatively small
        h, w = gray.shape[:2]
        if w < 1000:
            scale = 1000.0 / w
            gray = cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)

        # Denoise and adaptive threshold
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 4
        )

        return thresh

    def parse_text_lines(self, text: str) -> List[Dict[str, Any]]:
        """
        Parses raw text extracted by OCR into records.
        Win Go tables typically feature columns:
        [Period Number] [Number (0-9)] [Big/Small] [Color]
        """
        records = []
        lines = text.splitlines()

        # Regular expressions for period (at least 3-14 digits)
        period_pattern = re.compile(r'\b(202\d{7,13}|\d{3,14})\b')
        num_pattern = re.compile(r'\b([0-9])\b')
        size_pattern = re.compile(r'\b(Big|Small|BIG|SMALL)\b', re.IGNORECASE)
        color_pattern = re.compile(r'\b(Red|Green|Violet|Purple)\b', re.IGNORECASE)

        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            # Look for period match
            period_matches = period_pattern.findall(line_clean)
            if not period_matches:
                continue

            period = period_matches[0]
            # Discard periods that look like pure short indices unless part of valid table
            if len(period) < 3 and len(period_matches) == 1:
                continue

            # Remove period from line to look for remaining tokens
            line_without_period = line_clean.replace(period, "", 1)

            # Look for number (0-9)
            num_matches = num_pattern.findall(line_without_period)
            size_matches = size_pattern.findall(line_without_period)
            color_matches = color_pattern.findall(line_without_period)

            if num_matches:
                num = int(num_matches[0])
                inferred = self.infer_properties_from_number(num)

                size = size_matches[0].capitalize() if size_matches else inferred["size"]
                color = color_matches[0].capitalize() if color_matches else inferred["color"]
                if color == "Purple":
                    color = "Violet"

                records.append({
                    "period": period,
                    "number": num,
                    "size": size,
                    "color": color
                })

        # Deduplicate records by period
        unique_records = {}
        for r in records:
            p = r["period"]
            if p not in unique_records:
                unique_records[p] = r

        # Sort chronologically by period (older -> newer)
        sorted_records = sorted(
            unique_records.values(),
            key=lambda x: int(re.sub(r'\D', '', x["period"])) if re.sub(r'\D', '', x["period"]) else 0
        )

        return sorted_records

    def extract_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        Executes OCR on an image file and extracts table records.
        """
        try:
            # 1. OCR directly on PIL Image
            pil_img = Image.open(image_path)
            custom_config = r'--oem 3 --psm 6'
            raw_text = pytesseract.image_to_string(pil_img, config=custom_config)

            records = self.parse_text_lines(raw_text)

            # 2. If records are few, try with preprocessed OpenCV image
            if len(records) < 3:
                cv_img = self.preprocess_image(image_path)
                raw_text_cv = pytesseract.image_to_string(cv_img, config=r'--oem 3 --psm 4')
                records_cv = self.parse_text_lines(raw_text_cv)
                if len(records_cv) > len(records):
                    records = records_cv
                    raw_text = raw_text_cv

            return {
                "success": True,
                "count": len(records),
                "records": records,
                "raw_sample": raw_text[:300] if raw_text else ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "count": 0,
                "records": []
            }

    def parse_csv_or_text(self, text_content: str) -> List[Dict[str, Any]]:
        """
        Parses CSV, TSV, or raw text records.
        Expected headers or values: period, number, size, color
        """
        records = []
        lines = text_content.strip().splitlines()
        for line in lines:
            parts = [p.strip() for p in re.split(r'[,;\t|]', line) if p.strip()]
            if not parts:
                continue
            # Skip header line if found
            if any(k in parts[0].lower() for k in ["period", "issue", "round"]):
                continue

            # Look for number in parts
            num = None
            period = parts[0]
            size = None
            color = None

            for p in parts:
                if p.isdigit() and 0 <= int(p) <= 9 and num is None:
                    num = int(p)
                elif p.lower() in ["big", "small"]:
                    size = p.capitalize()
                elif p.lower() in ["green", "red", "violet"]:
                    color = p.capitalize()

            if num is not None:
                inferred = self.infer_properties_from_number(num)
                records.append({
                    "period": period,
                    "number": num,
                    "size": size or inferred["size"],
                    "color": color or inferred["color"]
                })
        return records

    def extract_from_zip(self, zip_path: str) -> Dict[str, Any]:
        """
        Extracts all images, CSVs, and JSONs from a ZIP archive and parses them.
        """
        import zipfile
        import tempfile

        all_records = []
        parsed_files = []
        errors = []

        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(tmp_dir)

                for root, _, files in os.walk(tmp_dir):
                    # Sort files alphabetically/numerically
                    for file in sorted(files):
                        file_lower = file.lower()
                        full_p = os.path.join(root, file)

                        if file_lower.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                            try:
                                res = self.extract_from_image(full_p)
                                if res["success"] and res["records"]:
                                    all_records.extend(res["records"])
                                    parsed_files.append(f"{file} (Image OCR: {res['count']} rows)")
                            except Exception as e:
                                errors.append(f"{file}: {e}")

                        elif file_lower.endswith(('.csv', '.tsv', '.txt')):
                            try:
                                with open(full_p, 'r', encoding='utf-8', errors='ignore') as f:
                                    txt = f.read()
                                recs = self.parse_csv_or_text(txt)
                                if not recs:
                                    recs = self.parse_text_lines(txt)
                                if recs:
                                    all_records.extend(recs)
                                    parsed_files.append(f"{file} (Text: {len(recs)} rows)")
                            except Exception as e:
                                errors.append(f"{file}: {e}")

                        elif file_lower.endswith('.json'):
                            try:
                                with open(full_p, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                if isinstance(data, list):
                                    for item in data:
                                        if isinstance(item, dict) and "number" in item:
                                            num = int(item["number"])
                                            inferred = self.infer_properties_from_number(num)
                                            all_records.append({
                                                "period": str(item.get("period", len(all_records) + 1)),
                                                "number": num,
                                                "size": item.get("size") or inferred["size"],
                                                "color": item.get("color") or inferred["color"]
                                            })
                                    parsed_files.append(f"{file} (JSON: {len(data)} rows)")
                            except Exception as e:
                                errors.append(f"{file}: {e}")

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to open ZIP: {e}",
                    "count": 0,
                    "records": []
                }

        # Deduplicate records by period
        unique = {}
        for r in all_records:
            p = str(r.get("period", "")).strip()
            if p:
                unique[p] = r

        return {
            "success": True,
            "count": len(unique),
            "records": list(unique.values()),
            "parsed_files": parsed_files,
            "errors": errors
        }

