"""
Flask Web Application for 92pkr Big/Small Prediction & Pattern Dashboard.
"""
import os
import json
import re
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify

from analyzer.engine import PredictionEngine
from ocr.parser import ImageHistoryParser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "history.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "zip", "csv", "txt", "json"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB max for ZIP uploads

engine = PredictionEngine()
ocr_parser = ImageHistoryParser()



def get_next_period_string(history):
    """Calculates next incremental period from the last record."""
    if not history:
        return "20240908001"
    last_p = str(history[-1].get("period", "0")).strip()
    match = re.search(r'(\d+)$', last_p)
    if match:
        digits = match.group(1)
        prefix = last_p[:match.start()]
        next_val = int(digits) + 1
        return f"{prefix}{str(next_val).zfill(len(digits))}"
    return str(len(history) + 1)


def load_history():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
            return records
    except Exception:
        return []


def save_history(records):
    # Deduplicate while strictly preserving chronological insertion order
    seen = set()
    deduped = []
    for r in records:
        p = str(r.get("period", "")).strip()
        if p and p not in seen:
            seen.add(p)
            deduped.append(r)
        elif not p:
            deduped.append(r)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=2)
    return deduped


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



import requests
from flask import Response

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/proxy")
def proxy_url():
    url = request.args.get("url")
    if not url:
        return "No URL provided", 400
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=12, verify=False)
        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection", "x-frame-options", "content-security-policy"]
        forward_headers = [(k, v) for k, v in resp.raw.headers.items() if k.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, forward_headers)
    except Exception as e:
        return f"Error proxying URL: {e}", 500


@app.route("/assets/<path:path>")
def proxy_assets(path):
    try:
        url = f"https://www.92pkr1.com/assets/{path}"
        resp = requests.get(url, timeout=12, verify=False)
        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        forward_headers = [(k, v) for k, v in resp.raw.headers.items() if k.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, forward_headers)
    except Exception as e:
        return f"Asset proxy error: {e}", 404


@app.route("/web/<path:path>")
def proxy_web(path):
    try:
        url = f"https://www.92pkr1.com/web/{path}"
        resp = requests.get(url, timeout=12, verify=False)
        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        forward_headers = [(k, v) for k, v in resp.raw.headers.items() if k.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, forward_headers)
    except Exception as e:
        return f"Web proxy error: {e}", 404




from live.client import PKR92LiveClient, GAME_TYPES
live_client = PKR92LiveClient()


@app.route("/api/live_sync", methods=["GET", "POST"])
def live_sync():
    game_key = request.args.get("game", "1m")
    issue_info = live_client.get_game_issue(game_key)
    live_draws = live_client.get_history_draws(game_key, page_size=30)

    history = load_history()
    if live_draws:
        existing_periods = {str(h.get("period", "")).strip() for h in history}
        new_records = [d for d in live_draws if str(d.get("period", "")).strip() not in existing_periods]
        if new_records or not history:
            history.extend(new_records)
            saved = save_history(history)
        else:
            saved = history
    else:
        saved = history

    pred = engine.predict(saved)
    # If live issue is available, override next_period with the exact server active issue
    if issue_info.get("success") and issue_info.get("issueNumber"):
        pred["next_period"] = str(issue_info["issueNumber"])

    return jsonify({
        "status": "success",
        "game_key": game_key,
        "issue_info": issue_info,
        "total_records": len(saved),
        "history": saved,
        "prediction_data": pred
    })


@app.route("/api/data", methods=["GET"])
def get_data():
    history = load_history()
    prediction_data = engine.predict(history)
    return jsonify({
        "status": "success",
        "total_records": len(history),
        "history": history,
        "prediction_data": prediction_data
    })



@app.route("/api/record", methods=["POST"])
def add_record():
    data = request.json or {}
    number_raw = data.get("number")
    period = str(data.get("period", "")).strip()

    if number_raw is None:
        return jsonify({"status": "error", "message": "Number is required"}), 400

    try:
        number = int(number_raw)
        if not (0 <= number <= 9):
            return jsonify({"status": "error", "message": "Number must be between 0 and 9"}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Number must be an integer (0-9)"}), 400

    history = load_history()
    if not period or period.lower() == "auto":
        period = get_next_period_string(history)

    inferred = ocr_parser.infer_properties_from_number(number)
    size = data.get("size") or inferred["size"]
    color = data.get("color") or inferred["color"]

    new_record = {
        "period": period,
        "number": number,
        "size": size.capitalize(),
        "color": color.capitalize()
    }
    history.append(new_record)
    saved = save_history(history)
    prediction_data = engine.predict(saved)

    return jsonify({
        "status": "success",
        "message": f"Period {period}: {number} ({size}) recorded!",
        "new_period": period,
        "total_records": len(saved),
        "prediction_data": prediction_data
    })


@app.route("/api/add_calibration", methods=["POST"])
def add_calibration():
    data = request.json or {}
    conf = float(data.get("confidence", 50.0))
    outcome = data.get("outcome", "Win")
    note = data.get("note", "")
    engine.calibrator.add_entry(conf, outcome, note)
    return jsonify({
        "status": "success",
        "message": f"Added calibration: {conf}% -> {outcome}",
        "tier_stats": engine.calibrator.get_tier_stats()
    })



@app.route("/api/upload", methods=["POST"])
def upload_screenshot():
    # Support single or multiple files
    uploaded_files = []
    if "image" in request.files:
        uploaded_files.extend(request.files.getlist("image"))
    if "files" in request.files:
        uploaded_files.extend(request.files.getlist("files"))
    if "file" in request.files:
        uploaded_files.extend(request.files.getlist("file"))

    if not uploaded_files or uploaded_files[0].filename == "":
        return jsonify({"status": "error", "message": "No files provided for upload"}), 400

    total_extracted = []
    processed_info = []

    for file in uploaded_files:
        if not allowed_file(file.filename):
            continue
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Check if ZIP archive
        if filename.lower().endswith(".zip"):
            zip_res = ocr_parser.extract_from_zip(filepath)
            if zip_res["success"] and zip_res["records"]:
                total_extracted.extend(zip_res["records"])
                processed_info.append(f"ZIP {filename}: extracted {zip_res['count']} draws across {len(zip_res.get('parsed_files', []))} files.")
        elif filename.lower().endswith((".csv", ".tsv", ".txt")):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            csv_recs = ocr_parser.parse_csv_or_text(content)
            if not csv_recs:
                csv_recs = ocr_parser.parse_text_lines(content)
            total_extracted.extend(csv_recs)
            processed_info.append(f"File {filename}: parsed {len(csv_recs)} records.")
        else:
            # Single image OCR
            ocr_res = ocr_parser.extract_from_image(filepath)
            if ocr_res["success"] and ocr_res["records"]:
                total_extracted.extend(ocr_res["records"])
                processed_info.append(f"Image {filename}: extracted {ocr_res['count']} rows.")

    if not total_extracted:
        return jsonify({
            "status": "warning",
            "message": "Files processed, but could not detect valid history rows. Please ensure images contain the 92PKR history table or upload clearer data.",
            "processed_info": processed_info
        })

    # Merge newly detected records into history
    existing_history = load_history()
    existing_history.extend(total_extracted)
    saved_history = save_history(existing_history)

    prediction_data = engine.predict(saved_history)

    return jsonify({
        "status": "success",
        "message": f"Successfully parsed and learned from {len(total_extracted)} historical records!",
        "extracted_count": len(total_extracted),
        "total_records": len(saved_history),
        "processed_info": processed_info,
        "prediction_data": prediction_data
    })



@app.route("/api/delete", methods=["POST"])
def delete_record():
    data = request.json or {}
    period = str(data.get("period", "")).strip()

    history = load_history()
    filtered = [h for h in history if str(h.get("period", "")).strip() != period]
    saved = save_history(filtered)
    prediction_data = engine.predict(saved)

    return jsonify({
        "status": "success",
        "message": f"Record {period} deleted",
        "total_records": len(saved),
        "prediction_data": prediction_data
    })


@app.route("/api/clear", methods=["POST"])
def clear_history():
    data = request.json or {}
    mode = data.get("mode", "empty")

    if mode == "sample":
        sample = [
            {"period": "20240908001", "number": 7, "size": "Big", "color": "Green"},
            {"period": "20240908002", "number": 3, "size": "Small", "color": "Green"},
            {"period": "20240908003", "number": 8, "size": "Big", "color": "Red"},
            {"period": "20240908004", "number": 6, "size": "Big", "color": "Red"},
            {"period": "20240908005", "number": 1, "size": "Small", "color": "Green"},
            {"period": "20240908006", "number": 4, "size": "Small", "color": "Red"},
            {"period": "20240908007", "number": 9, "size": "Big", "color": "Green"},
            {"period": "20240908008", "number": 5, "size": "Big", "color": "Violet"},
            {"period": "20240908009", "number": 2, "size": "Small", "color": "Red"},
            {"period": "20240908010", "number": 0, "size": "Small", "color": "Violet"},
            {"period": "20240908011", "number": 7, "size": "Big", "color": "Green"},
            {"period": "20240908012", "number": 8, "size": "Big", "color": "Red"},
            {"period": "20240908013", "number": 9, "size": "Big", "color": "Green"},
            {"period": "20240908014", "number": 6, "size": "Big", "color": "Red"},
            {"period": "20240908015", "number": 3, "size": "Small", "color": "Green"},
            {"period": "20240908016", "number": 2, "size": "Small", "color": "Red"},
            {"period": "20240908017", "number": 8, "size": "Big", "color": "Red"},
            {"period": "20240908018", "number": 1, "size": "Small", "color": "Green"},
            {"period": "20240908019", "number": 7, "size": "Big", "color": "Green"},
            {"period": "20240908020", "number": 4, "size": "Small", "color": "Red"}
        ]
        saved = save_history(sample)
    else:
        saved = save_history([])

    prediction_data = engine.predict(saved)
    return jsonify({
        "status": "success",
        "message": "History updated",
        "total_records": len(saved),
        "prediction_data": prediction_data
    })


if __name__ == "__main__":
    PORT = 5092
    print(f"\n========================================================")
    print(f" 92PKR Big/Small AI Predictor running at:")
    print(f" Local PC:       http://127.0.0.1:{PORT}")
    print(f" Phone / Mobile: http://192.168.1.78:{PORT}")
    print(f"========================================================\n")
    app.run(host="0.0.0.0", port=PORT, debug=False)
