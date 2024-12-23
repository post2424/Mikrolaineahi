import pygame, random, math

#keybinds
up = [pygame.K_UP, pygame.K_w]
down = [pygame.K_DOWN, pygame.K_s]
left = [pygame.K_LEFT, pygame.K_a]
right = [pygame.K_RIGHT,pygame.K_d]

def get_vector(point1,point2):
    return [i - j for i, j in zip(point1, point2)]
def get_vectors_sum(vektor1, vektor2):
    return [i + j for i, j in zip(vektor1, vektor2)]
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
            kogu_muut = get_vector(last_pos,first_pos)
            for pos in positions[1:-2]:
                vektori_pikkus = get_vector_length(kogu_muut)
                if vektori_pikkus > 100 and vektori_pikkus != 0:
                    nimetaja = abs(kogu_muut[1] * pos[0] - kogu_muut[0] * pos[1] + last_pos[0] * first_pos[1] - last_pos[1] *first_pos[0])
                    kaugus_sirgest = nimetaja/vektori_pikkus
                    if kaugus_sirgest > 30:
                        return False
                else:
                    return False
            return True

