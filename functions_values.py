import pygame, random, math

#keybinds
up = [pygame.K_UP, pygame.K_w]
down = [pygame.K_DOWN, pygame.K_s]
left = [pygame.K_LEFT, pygame.K_a]
right = [pygame.K_RIGHT,pygame.K_d]


def get_vector_length(vektor):
    return math.sqrt(vektor[0]**2 + vektor[1]**2)
def big_render(renders):
    renders = sorted(renders, key=lambda obj: obj.pos[1]+obj.sprite.get_height())
    for rend in renders:
        rend.render()
def set_nearest_offscreen_pos(pos,objekt, ekraan):
    ekraan_laius, ekraan_pikkus = ekraan[0], ekraan[1]
    x,y = pos[0], pos[1]
    a = [x, y, ekraan_laius - x, ekraan_pikkus - y]
    match a.index(min(a)):
        case 0:
            objekt.pos = (-objekt.sprite.get_width(), y - objekt.sprite.get_height())
        case 1:
            objekt.pos = (x, -objekt.sprite.get_height())
        case 2:
            objekt.pos = (ekraan_laius + objekt.sprite.get_width(), y - objekt.sprite.get_height())
        case 3:
            objekt.pos = (x, ekraan_pikkus + objekt.sprite.get_height())

from PIL import Image

from PIL import Image


def grayscale_with_alpha(input_image_path, output_image_path):
    # Open the image and ensure it's in RGBA mode
    img = Image.open(input_image_path).convert("RGBA")

    # Convert to grayscale
    grayscale_img = img.convert("L")

    # Get the grayscale pixel data
    grayscale_data = grayscale_img.getdata()

    # Modify the alpha channel based on the grayscale intensity
    new_data = []
    for i, pixel in enumerate(img.getdata()):
        r, g, b, a = pixel  # Original RGBA values
        alpha = 255 - grayscale_data[i]  # Higher grayscale value = lower alpha
        new_data.append((r, g, b, alpha))

    # Create a new image with updated alpha
    result_img = Image.new("RGBA", img.size)
    result_img.putdata(new_data)

    # Save the result
    result_img.save(output_image_path)
    print(f"Image saved at {output_image_path}")

