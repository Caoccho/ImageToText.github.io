import os
import cv2
import base64
import numpy as np
import pytesseract
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "❌ Không tìm thấy file!"

        file = request.files["file"]

        if file.filename == "":
            return "❌ Chưa chọn file!"

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Xử lý OCR
        text = process_image(filepath)

        return render_template("result.html", text=text, image=filepath)

    return render_template("upload.html")


@app.route("/paste", methods=["POST"])
def paste_image():
    if "clipboardImage" not in request.form:
        return "❌ Không tìm thấy ảnh từ clipboard!"

    image_data = request.form["clipboardImage"]
    image_bytes = base64.b64decode(image_data)  # Giải mã base64 thành ảnh
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], "clipboard.png")
    cv2.imwrite(filepath, image)  # Lưu ảnh từ clipboard

    # Xử lý OCR
    text = process_image(filepath)

    return render_template("result.html", text=text, image=filepath)


def process_image(filepath):
    """Chuyển ảnh sang grayscale và xử lý OCR"""
    image = cv2.imread(filepath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Chuyển ảnh sang grayscale
    text = pytesseract.image_to_string(gray, config="--psm 3")  # Nhận diện chữ
    return text


if __name__ == "__main__":
    app.run(debug=True)
