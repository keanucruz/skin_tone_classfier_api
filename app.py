from flask import Flask, request, jsonify
from PIL import Image
import stone
import io

app = Flask(__name__)

@app.route('/')
def welcome():
    return "Welcome"

def categorize_skin_tone(hex_color):
    hex_to_season = {
        '#373028': 'Winter',
        '#422811': 'Autumn',
        '#513B2E': 'Winter',
        '#6F503C': 'Autumn',
        '#81654F': 'Autumn',
        '#9D7A54': 'Autumn',
        '#BEA07E': 'Autumn',
        '#E5C8A6': 'Autumn',
        '#E7C1B8': 'Spring',
        '#F3DAD6': 'Summer',
        '#FBF2F3': 'Spring'
    }
    return hex_to_season.get(hex_color, "Unknown")

def get_color_palette(season):
    palettes = {
        'Winter': {
            "Black": "#000000",
            "White": "#FFFFFF",
            "Emerald Green": "#006400",
            "Royal Blue": "#4169E1",
            "Deep Purple": "#4B0082",
            "True Red": "#FF0000",
            "Cool Blue": "#4682B4",
            "Hot Pink": "#FF69B4",
            "Icy Grey": "#A9A9A9"
        },
        'Summer': {
            "Soft Pink": "#FFB6C1",
            "Baby Blue": "#89CFF0",
            "Lavender": "#E6E6FA",
            "Powder Blue": "#B0E0E6",
            "Dove Grey": "#696969",
            "Soft White": "#F5F5F5",
            "Muted Navy": "#5F9EA0",
            "Mint": "#98FF98",
            "Rose": "#FF007F",
            "Soft Blue-Green": "#4682B4"
        },
        'Autumn': {
            "Olive Green": "#808000",
            "Burnt Orange": "#CC5500",
            "Mustard Yellow": "#FFDB58",
            "Camel": "#C19A6B",
            "Beige": "#F5F5DC",
            "Rich Brown": "#8B4513",
            "Deep Teal": "#014421",
            "Brick Red": "#CB4154",
            "Forest Green": "#228B22",
            "Gold": "#FFD700",
            "Bronze": "#CD7F32"
        },
        'Spring': {
            "Coral": "#FF7F50",
            "Peach": "#FFE5B4",
            "Clear Red": "#FF4500",
            "Bright Green": "#00FF00",
            "Turquoise": "#40E0D0",
            "Light Warm Blue": "#ADD8E6",
            "Peachy Pink": "#FFDAB9",
            "Apricot": "#FBCEB1",
            "Light Camel": "#C19A6B",
            "Ivory": "#FFFFF0",
            "Warm Beige": "#F5F5DC",
            "Butter Yellow": "#FFFACD",
            "Light Periwinkle": "#C3CDE6",
            "Bright Warm Green": "#7FFF00"
        }
    }
    return palettes.get(season, {})

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

    # Determine the season category
    season_category = categorize_skin_tone(skin_tone)

    # Get the color palette for the determined season category
    color_palette = get_color_palette(season_category)

    result_json = {
        "dominant_colors": dominant_colors,
        "skin_tone": skin_tone,
        "accuracy": accuracy,
        "season_category": season_category,
        "color_palette": color_palette
    }

    return jsonify(result_json)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3009, debug=True)