import io
import stone
import os
from PIL import Image
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from rembg import remove

app = Flask(__name__)
app.secret_key = 'diniyonapwedengmasisikungbatganitoginaganapankolangnanaturalsakainagapankonamautal'

host = os.getenv('FLASK_HOST', '0.0.0.0')
port = int(os.getenv('FLASK_PORT', 3009))
debug = os.getenv('FLASK_DEBUG', 'True') == 'True'

winter_products = [
    {"id": 1, "name": "Winter Coat", "type": "clothes", "color": "#000000", "brand": "North Face"},  # Black
    {"id": 2, "name": "White Turtleneck", "type": "clothes", "color": "#FFFFFF", "brand": "Zara"},  # White
    {"id": 3, "name": "Emerald Green Sweater", "type": "clothes", "color": "#006400", "brand": "H&M"},  # Emerald Green
    {"id": 4, "name": "Royal Blue Jeans", "type": "bottoms", "color": "#4169E1", "brand": "Levi's"},  # Royal Blue
    {"id": 5, "name": "Deep Purple Scarf", "type": "clothes", "color": "#4B0082", "brand": "Burberry"},  # Deep Purple
    {"id": 6, "name": "True Red Dress", "type": "clothes", "color": "#FF0000", "brand": "Dior"},  # True Red
    {"id": 7, "name": "Cool Blue Jacket", "type": "clothes", "color": "#4682B4", "brand": "Adidas"},  # Cool Blue
    {"id": 8, "name": "Hot Pink Pants", "type": "bottoms", "color": "#FF69B4", "brand": "ASOS"},  # Hot Pink
    {"id": 9, "name": "Icy Grey Sweater", "type": "clothes", "color": "#A9A9A9", "brand": "Uniqlo"},  # Icy Grey
    {"id": 10, "name": "Winter Lipstick", "type": "cosmetic", "color": "#FF0000", "brand": "MAC"},  # True Red
    {"id": 11, "name": "Winter Nail Polish", "type": "cosmetic", "color": "#000000", "brand": "OPI"},  # Black
    {"id": 12, "name": "Winter Eye Shadow", "type": "cosmetic", "color": "#4B0082", "brand": "Urban Decay"}  # Deep Purple
]

summer_products = [
    {"id": 10, "name": "Soft Pink Blouse", "type": "clothes", "color": "#FFB6C1", "brand": "Forever 21"},  # Soft Pink
    {"id": 11, "name": "Baby Blue Shorts", "type": "bottoms", "color": "#89CFF0", "brand": "Hollister"},  # Baby Blue
    {"id": 12, "name": "Lavender Maxi Dress", "type": "clothes", "color": "#E6E6FA", "brand": "Lulus"},  # Lavender
    {"id": 13, "name": "Powder Blue Pants", "type": "bottoms", "color": "#B0E0E6", "brand": "Gap"},  # Powder Blue
    {"id": 14, "name": "Dove Grey Cardigan", "type": "clothes", "color": "#696969", "brand": "Mango"},  # Dove Grey
    {"id": 15, "name": "Soft White Capris", "type": "bottoms", "color": "#F5F5F5", "brand": "Old Navy"},  # Soft White
    {"id": 16, "name": "Muted Navy T-shirt", "type": "clothes", "color": "#5F9EA0", "brand": "American Eagle"},  # Muted Navy
    {"id": 17, "name": "Mint Skirt", "type": "bottoms", "color": "#98FF98", "brand": "Express"},  # Mint
    {"id": 18, "name": "Rose Dress", "type": "clothes", "color": "#FF007F", "brand": "Zalando"},  # Rose
    {"id": 19, "name": "Soft Blue-Green Pants", "type": "bottoms", "color": "#4682B4", "brand": "Puma"},  # Soft Blue-Green
    {"id": 20, "name": "Summer Lipstick", "type": "cosmetic", "color": "#FFB6C1", "brand": "Maybelline"},  # Soft Pink
    {"id": 21, "name": "Summer Nail Polish", "type": "cosmetic", "color": "#89CFF0", "brand": "Sally Hansen"},  # Baby Blue
    {"id": 22, "name": "Summer Eye Shadow", "type": "cosmetic", "color": "#E6E6FA", "brand": "Too Faced"}  # Lavender
]

autumn_products = [
    {"id": 20, "name": "Olive Green Jacket", "type": "clothes", "color": "#808000", "brand": "Columbia"},  # Olive Green
    {"id": 21, "name": "Burnt Orange Sweater", "type": "clothes", "color": "#CC5500", "brand": "H&M"},  # Burnt Orange
    {"id": 22, "name": "Mustard Yellow Scarf", "type": "clothes", "color": "#FFDB58", "brand": "Banana Republic"},  # Mustard Yellow
    {"id": 23, "name": "Camel Coat", "type": "clothes", "color": "#C19A6B", "brand": "Zara"},  # Camel
    {"id": 24, "name": "Beige Pants", "type": "bottoms", "color": "#F5F5DC", "brand": "Dockers"},  # Beige
    {"id": 25, "name": "Rich Brown Skirt", "type": "bottoms", "color": "#8B4513", "brand": "Topshop"},  # Rich Brown
    {"id": 26, "name": "Deep Teal T-shirt", "type": "clothes", "color": "#014421", "brand": "Uniqlo"},  # Deep Teal
    {"id": 27, "name": "Brick Red Dress", "type": "clothes", "color": "#CB4154", "brand": "ASOS"},  # Brick Red
    {"id": 28, "name": "Forest Green Pants", "type": "bottoms", "color": "#228B22", "brand": "Levi's"},  # Forest Green
    {"id": 29, "name": "Gold Top", "type": "clothes", "color": "#FFD700", "brand": "Chanel"},  # Gold
    {"id": 30, "name": "Bronze Skirt", "type": "bottoms", "color": "#CD7F32", "brand": "Michael Kors"},  # Bronze
    {"id": 31, "name": "Autumn Lipstick", "type": "cosmetic", "color": "#CC5500", "brand": "Revlon"},  # Burnt Orange
    {"id": 32, "name": "Autumn Nail Polish", "type": "cosmetic", "color": "#808000", "brand": "Essie"},  # Olive Green
    {"id": 33, "name": "Autumn Eye Shadow", "type": "cosmetic", "color": "#CB4154", "brand": "NYX"}  # Brick Red
]

spring_products = [
    {"id": 31, "name": "Coral Dress", "type": "clothes", "color": "#FF7F50", "brand": "Lulus"},  # Coral
    {"id": 32, "name": "Peach Blouse", "type": "clothes", "color": "#FFE5B4", "brand": "Forever 21"},  # Peach
    {"id": 33, "name": "Clear Red Skirt", "type": "bottoms", "color": "#FF4500", "brand": "H&M"},  # Clear Red
    {"id": 34, "name": "Bright Green T-shirt", "type": "clothes", "color": "#00FF00", "brand": "American Eagle"},  # Bright Green
    {"id": 35, "name": "Turquoise Pants", "type": "bottoms", "color": "#40E0D0", "brand": "Zalando"},  # Turquoise
    {"id": 36, "name": "Light Warm Blue Dress", "type": "clothes", "color": "#ADD8E6", "brand": "Zara"},  # Light Warm Blue
    {"id": 37, "name": "Peachy Pink Top", "type": "clothes", "color": "#FFDAB9", "brand": "Mango"},  # Peachy Pink
    {"id": 38, "name": "Lilac Skirt", "type": "bottoms", "color": "#C8A2C8", "brand": "Topshop"},  # Lilac
    {"id": 39, "name": "Spring Lipstick", "type": "cosmetic", "color": "#FF7F50", "brand": "NARS"},  # Coral
    {"id": 40, "name": "Spring Nail Polish", "type": "cosmetic", "color": "#FFE5B4", "brand": "Sally Hansen"},  # Peach
    {"id": 41, "name": "Spring Eye Shadow", "type": "cosmetic", "color": "#40E0D0", "brand": "Benefit Cosmetics"}  # Turquoise
]


@app.route('/')
def home():
    return render_template('index.html')

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
    output_image = remove(image)


    image_folder = os.path.join(app.root_path, 'images')


    os.makedirs(image_folder, exist_ok=True)


    processed_image_path = os.path.join(image_folder, "temp_image.png")
    output_image.save(processed_image_path)

    result = stone.process(processed_image_path, image_type, return_report_image=True)

    dominant_colors = result['faces'][0]['dominant_colors']
    skin_tone = result['faces'][0]['skin_tone']
    accuracy = result['faces'][0]['accuracy']

    season_category = categorize_skin_tone(skin_tone)

    color_palette = get_color_palette(season_category)

    result_json = {
        "dominant_colors": dominant_colors,
        "skin_tone": skin_tone,
        "accuracy": accuracy,
        "season_category": season_category,
        "color_palette": color_palette
    }

    return jsonify(result_json)

@app.route('/api/products/<season>', methods=['GET'])
def get_products(season):
    products = {
        "winter": winter_products,
        "summer": summer_products,
        "autumn": autumn_products,
        "spring": spring_products
    }

    if season in products:
        return jsonify({season: products[season]})
    else:
        return jsonify({"error": "Season not found"}), 404

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    type_ = request.form['type']
    color = request.form['color']
    brand = request.form['brand']


    season = None
    for s in ['Winter', 'Summer', 'Autumn', 'Spring']:
        colors = get_color_palette(s)
        if color in colors.values():
            season = s
            break

    if season is None:
        flash("Color not found in any season", "danger")
        return redirect(url_for('home'))

    new_product = {
        "id": len(globals()[f"{season.lower()}_products"]) + 1,
        "name": name,
        "type": type_,
        "color": color,
        "brand": brand
    }

    globals()[f"{season.lower()}_products"].append(new_product)

    flash("Product added successfully!", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host=host, port=port, debug=debug)
