from flask import Flask, request, jsonify
from PIL import Image
import stone
import io

app = Flask(__name__)

@app.route('/')
def welcome():
    return "Welcome"

@app.route('/process_image', methods=['POST'])
def process_image():
    file = request.files['image']
    image_type = 'color'
    other_args = []

    image = Image.open(io.BytesIO(file.read()))
    image_path = "temp_image.png"
    image.save(image_path)

    result = stone.process(image_path, image_type, return_report_image=True)

    dominant_colors = result['faces'][0]['dominant_colors']
    skin_tone = result['faces'][0]['skin_tone']
    accuracy = result['faces'][0]['accuracy']

    result_json = {
        "dominant_colors": dominant_colors,
        "skin_tone": skin_tone,
        "accuracy": accuracy
    }

    return jsonify(result_json)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3009, debug=True)
