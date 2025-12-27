from flask import Flask, request, send_file
import cv2
import numpy as np
from filters import anime, ghibli, sketch, portrait
import io
from PIL import Image

app = Flask(__name__)

@app.route("/convert", methods=["POST"])
def convert():
    file = request.files["image"]
    style = request.form["style"]

    image = np.array(Image.open(file).convert("RGB"))
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if style == "anime":
        output = anime(image)
    elif style == "ghibli":
        output = ghibli(image)
    elif style == "sketch":
        output = sketch(image)
    else:
        output = portrait(image)

    result = Image.fromarray(output)
    buf = io.BytesIO()
    result.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)