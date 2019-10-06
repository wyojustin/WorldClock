from PIL import Image
import colorsys
import math

if __name__ == "__main__":
 
    im = Image.new("RGB", (300,300))
    radius = min(im.size)/2.0
    centre = im.size[0]/2, im.size[1]/2
    pix = im.load()
    
    for x in range(im.width):
        for y in range(im.height):
            rx = x - centre[0]
            ry = y - centre[1]
            r = math.sqrt(rx ** 2 + ry ** 2)
            if r < radius:
                s = ((x - centre[0])**2.0 + (y - centre[1])**2.0)**0.5 / radius
                s = 1
                if s <= 1.0:
                    h = ((math.atan2(ry, rx) / math.pi) + 1.0) / 2.0
                    rgb = colorsys.hsv_to_rgb(h, s, 1.0)
                    pix[x,y] = tuple([int(round(c*255.0)) for c in rgb])
    im.show()
