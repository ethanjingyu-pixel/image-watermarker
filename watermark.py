import os
import argparse
from PIL import Image, ImageDraw, ImageFont
import exifread

def get_exif_date(image_path):
    date = None
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)
        if 'EXIF DateTimeOriginal' in tags:
            date_str = str(tags['EXIF DateTimeOriginal'])
            date = date_str.split(' ')[0].replace(':', '-')
    if not date:
        import datetime
        date = datetime.date.today().strftime("%Y-%m-%d")
    return date

def add_watermark(image_path, text, output_path, font_size, color, position):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
    width, height = image.size

    if position == "top_left":
        x, y = 10, 10
    elif position == "center":
        x, y = (width - text_width) / 2, (height - text_height) / 2
    else:  # bottom_right
        x, y = width - text_width - 10, height - text_height - 10

    draw.text((x, y), text, fill=color, font=font)
    
    if os.path.dirname(output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path)

def main():
    parser = argparse.ArgumentParser(description="Add a watermark to an image with the date it was taken.")
    parser.add_argument("image_path", type=str, help="The path to the image file or directory.")
    parser.add_argument("--font_size", type=int, default=36, help="The font size of the watermark.")
    parser.add_argument("--color", type=str, default="white", help="The color of the watermark.")
    parser.add_argument("--position", type=str, default="bottom_right", help="The position of the watermark (e.g., top_left, center, bottom_right).")
    args = parser.parse_args()

    if os.path.isdir(args.image_path):
        for filename in os.listdir(args.image_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(args.image_path, filename)
                date = get_exif_date(image_path)
                if date:
                    output_dir = os.path.join(args.image_path, os.path.basename(args.image_path) + "_watermark")
                    output_path = os.path.join(output_dir, filename)
                    add_watermark(image_path, date, output_path, args.font_size, args.color, args.position)
                    print(f"Added watermark to {filename}")
    else:
        date = get_exif_date(args.image_path)
        print(f"Extracted date: {date}")
        if date:
            filename, file_extension = os.path.splitext(args.image_path)
            output_path = f"{filename}_watermark{file_extension}"
            add_watermark(args.image_path, date, output_path, args.font_size, args.color, args.position)
            print(f"Added watermark to {args.image_path}")

if __name__ == "__main__":
    main()