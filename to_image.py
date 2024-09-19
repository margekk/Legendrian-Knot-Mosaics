'''
Python program to convert Legendrian mosaic codes into images.

Usage:
python to_image <mosaic code>

This material is based upon work supported by the National Science Foundation under Grant No. MPS-2150299
'''
import sys,os
from PIL import Image, ImageDraw

def main():
    if len(sys.argv) != 2:
        print("Please provide a Legendrian mosaic code.\nUsage: python to_image.py <mosaic code>")
    else:
        mosaic_string = sys.argv[1]
        mosaic = [int(digit) for digit in mosaic_string]
        to_png(mosaic,mosaic_string + ".png") 

def to_png(matrix,output_filename):
    tile_size = 128
    border_size = 4
    border_color = (196, 196, 196, 255)
    size = int(len(matrix)**0.5)

    tile_images = {}
    for num in range(10):
        file_name = f"tiles/{num}.png"
        try:
            tile_images[num] = Image.open(file_name).convert("RGBA")
        except FileNotFoundError:
            print(f"Failed to load image {file_name}")

    mosaic_width = size * tile_size + 2 * border_size
    mosaic = Image.new("RGBA", (mosaic_width, mosaic_width), border_color)
    draw = ImageDraw.Draw(mosaic)

    for i, tile in enumerate(matrix):
            if tile in tile_images:
                img_tile = tile_images[tile]
                for y in range(tile_size):
                    for x in range(tile_size):
                        pixel = img_tile.getpixel((x, y))
                        mosaic.putpixel(( (i % size) * tile_size + x + border_size, (i // size) * tile_size + y + border_size), pixel)

    os.makedirs("images", exist_ok=True)
    rotated_mosaic = mosaic.rotate(45, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
    rotated_mosaic.save(f"images/{output_filename}")
    print(f"Mosaic saved at images/{output_filename}")


main()
