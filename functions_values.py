import pygame, random, math

#keybinds
up = [pygame.K_UP, pygame.K_w]
down = [pygame.K_DOWN, pygame.K_s]
left = [pygame.K_LEFT, pygame.K_a]
right = [pygame.K_RIGHT,pygame.K_d]


def set_nearest_offscreen_pos(pos,objekt, ekraan):
    ekraan_laius, ekraan_pikkus = ekraan[0], ekraan[1]
    x,y = pos[0], pos[1]
    objekti_laius = objekt.image.get_width()
    objekti_pikkus = objekt.image.get_height()

    a = [x+objekti_laius, y, ekraan_laius - x, ekraan_pikkus - y +objekti_pikkus]
    match a.index(min(a)):
        case 0:
            x = -objekti_laius
            y = y - objekti_pikkus
        case 1:
            y = -objekti_pikkus
        case 2:
            x = ekraan_laius + objekti_laius
            y = y - objekti_pikkus
        case 3:
            y = ekraan_pikkus + objekti_pikkus
    objekt.rect = pygame.math.Vector2(x,y)





def grayscale_with_alpha(input_image_path, output_image_path):
    from PIL import Image
    img = Image.open(input_image_path).convert("RGBA")
    grayscale_img = img.convert("L")
    grayscale_data = grayscale_img.getdata()
    new_data = []
    for i, pixel in enumerate(img.getdata()):
        r, g, b, a = pixel
        alpha = 255 - grayscale_data[i]
        new_data.append((r, g, b, alpha))
    result_img = Image.new("RGBA", img.size)
    result_img.putdata(new_data)
    result_img.save(output_image_path)
    print(f"Image saved at {output_image_path}")

aeg = 0
def fadeout_render(objekt,sekundit):
    global aeg
    frames = sekundit*60
    if aeg < frames:
        aeg += 1
        protsent = 1-aeg/frames
        objekt.sprite = objekt.sprite.set_alpha(255*protsent)
    else:
        aeg = 0

def is_line(positions):
    match len(positions):
        case 0,1: return False
        case 2: return True
        case _:
            first_pos = positions[0]
            last_pos = positions[-1]
            kogu_muut =  last_pos - first_pos
            vektori_pikkus = kogu_muut.length()
            for pos in positions[1:-2]:
                if vektori_pikkus > 100:
                    nimetaja = abs(kogu_muut[1] * pos[0] - kogu_muut[0] * pos[1] + last_pos[0] * first_pos[1] - last_pos[1] *first_pos[0])
                    kaugus_sirgest = nimetaja/vektori_pikkus
                    if kaugus_sirgest > 30:
                        return False
                else:
                    return False

            return True