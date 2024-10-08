from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import stone
import rembg  # For background removal (experimental)
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
import os
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
products = []

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

# Hex to RGB conversion
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

# Convert RGB to Lab
def rgb_to_lab(rgb_color):
    r, g, b = rgb_color
    srgb_color = sRGBColor(r / 255, g / 255, b / 255)
    return convert_color(srgb_color, LabColor)

# Calculate Delta E (color difference)
def calculate_color_difference(color1, color2):
    lab1 = rgb_to_lab(color1)
    lab2 = rgb_to_lab(color2)
    delta_e = delta_e_cie2000(lab1, lab2)
    return delta_e

# Check if the selected color is within the shade of a palette color
def is_color_within_shade(selected_color, palette_color, threshold=10):
    selected_rgb = hex_to_rgb(selected_color)
    palette_rgb = hex_to_rgb(palette_color)
    delta_e = calculate_color_difference(selected_rgb, palette_rgb)
    return delta_e < threshold

# Check if any palette color is within the shade of the selected color
def does_color_match(selected_color, palette, threshold=10):
    for palette_color in palette.values():
        if is_color_within_shade(selected_color, palette_color, threshold):
            return True
    return False

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        image = Image.open(file)

        # Remove background
        image_np = np.array(image)
        image_no_bg = rembg.remove(image_np)

        image_no_bg_pil = Image.fromarray(image_no_bg)
        image_path = "temp_image.png"
        image_no_bg_pil.save(image_path)

        # Process the image with the stone library
        result = stone.process(image_path, 'color', return_report_image=True)

        if 'faces' in result and len(result['faces']) > 0:
            face_data = result['faces'][0]
            dominant_colors = face_data.get('dominant_colors', [])
            skin_tone = face_data.get('skin_ttone', '')
            accuracy = face_data.get('accuracy', 0)

            # Categorize the skin tone
            season_category = categorize_skin_tone(skin_tone)

            # Get the color palette based on the season
            color_palette = get_color_palette(season_category)

            result_json = {
                "dominant_colors": dominant_colors,
                "skin_tone": skin_tone,
                "accuracy": accuracy,
                "season_category": season_category,
                "color_palette": color_palette
            }

            return jsonify(result_json)
        else:
            return jsonify({'error': 'No face data found in the processed image'}), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/submit_product', methods=['POST'])
def submit_product():
    try:
        # Get form data
        product_name = request.form.get('Name')
        manufacturer = request.form.get('Manufacturer')
        release_date = request.form.get('Day')  # New field: Date of product release
        product_color = request.form.get('selectedColor')
        description = request.form.get('Description')  # New field: Product description
        shop_name = request.form.get('ShopName')  # New field: Shop name
        cost = request.form.get('Cost')  # New field: Product cost
        product_type = request.form.get('Product')  # New field: Type of product

        # Save the image
        image_file = request.files.get('image')
        image_path = None
        if image_file:
            image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
            image_file.save(image_path)

        # Store product details
        products.append({
            "name": product_name,
            "manufacturer": manufacturer,
            "release_date": release_date,
            "color": product_color,
            "description": description,
            "shop_name": shop_name,
            "cost": cost,
            "product_type": product_type,
            "image_path": image_path
        })

        response = {
            "success": True, 
            "message": f"Product '{product_name}' uploaded successfully.",
        }

        return jsonify(response)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_products', methods=['GET'])
def get_products():
    return jsonify(products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3009, debug=True)
