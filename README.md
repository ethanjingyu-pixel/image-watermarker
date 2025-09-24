# Image Watermarker

This script adds a watermark to an image with the date it was taken. It can process a single image file or a directory of images.

## Features

- Extracts the date from the image's EXIF data.
- If no EXIF date is found, it uses the current date.
- Adds the date as a watermark to the image.
- Supports customizing the font size, color, and position of the watermark.
- Can process a single image or a directory of images.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/ethanjingyu-pixel/image-watermarker.git
    ```
2.  Navigate to the project directory:
    ```bash
    cd image-watermarker
    ```
3.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    ```
4.  Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
5.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Single Image

```bash
python3 watermark.py <image_path> [options]
```

### Directory of Images

```bash
python3 watermark.py <directory_path> [options]
```

### Options

- `--font_size`: The font size of the watermark (default: 36).
- `--color`: The color of the watermark (default: white).
- `--position`: The position of the watermark (e.g., `top_left`, `center`, `bottom_right`) (default: `bottom_right`).

## Examples

### Add a watermark to a single image

```bash
python3 watermark.py images.jpeg
```

### Add a watermark with custom options

```bash
python3 watermark.py images.jpeg --font_size 50 --color red --position center
```

### Add watermarks to a directory of images

```bash
python3 watermark.py /path/to/your/images
```