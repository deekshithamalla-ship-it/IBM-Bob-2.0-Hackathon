from flask import Flask, render_template, request, jsonify
import os
from ai_analyzer import analyze_waste_image

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({"error": "No image selected"}), 400

    if not allowed_file(image.filename):
        return jsonify({"error": "Unsupported file type. Please upload a JPG, PNG, or WEBP image."}), 400

    image_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        image.filename
    )

    image.save(image_path)

    try:
        result = analyze_waste_image(image_path)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503

    return jsonify({"success": True, **result})


if __name__ == "__main__":
    app.run(debug=True, threaded=True, use_reloader=False)