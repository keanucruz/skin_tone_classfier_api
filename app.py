from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import stone
import io
import rembg  # For background removal (experimental)

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

def recommend_products(season):
    product_recommendations = {
        'Winter': [
            {"name": "Black Coat", "link": "http://example.com/black-coat"},
            {"name": "Emerald Green Sweater", "link": "http://example.com/emerald-sweater"},
            {"name": "Royal Blue Dress", "link": "http://example.com/royal-blue-dress"}
        ],
        'Summer': [
            {"name": "Soft Pink Blouse", "link": "http://example.com/pink-blouse"},
            {"name": "Baby Blue T-shirt", "link": "http://example.com/baby-blue-tshirt"},
            {"name": "Mint Green Skirt", "link": "http://example.com/mint-skirt"}
        ],
        'Autumn': [
            {"name": "Olive Green Jacket", "link": "http://example.com/olive-jacket"},
            {"name": "Burnt Orange Scarf", "link": "http://example.com/orange-scarf"},
            {"name": "Camel Pants", "link": "http://example.com/camel-pants"}
        ],
        'Spring': [
            {"name": "Coral Dress", "link": "http://example.com/coral-dress"},
            {"name": "Peach Cardigan", "link": "http://example.com/peach-cardigan"},
            {"name": "Turquoise Shirt", "link": "http://example.com/turquoise-shirt"}
        ]
    }
    return product_recommendations.get(season, [])

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
       
        image = Image.open(file)

        
        image_np = np.array(image)
        image_no_bg = rembg.remove(image_np)  

        
        image_no_bg_pil = Image.fromarray(image_no_bg)

      
        image_path = "temp_image.png"
        image_no_bg_pil.save(image_path)

        
        result = stone.process(image_path, 'color', return_report_image=True)

      
        if 'faces' in result and len(result['faces']) > 0:
            face_data = result['faces'][0]
            dominant_colors = face_data.get('dominant_colors', [])
            skin_tone = face_data.get('skin_tone', '')  
            accuracy = face_data.get('accuracy', 0)

          
            season_category = categorize_skin_tone(skin_tone)

          
            color_palette = get_color_palette(season_category)

            
            product_recommendations = recommend_products(season_category)

        
            result_json = {
                "dominant_colors": dominant_colors,
                "skin_tone": skin_tone,
                "accuracy": accuracy,
                "season_category": season_category,
                "color_palette": color_palette,
                "product_recommendations": product_recommendations
            }

            return jsonify(result_json)
        else:
            return jsonify({'error': 'No face data found in the processed image'}), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3009, debug=True)
