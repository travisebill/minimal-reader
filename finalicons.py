from PIL import Image
import os

# 用候選 1（icon_001.jpg）
SRC = 'icons/icon_001.jpg'
THR = 232

def key_light(im):
    im = im.convert('RGBA')
    px = im.load()
    n = 0
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a > 0 and r > THR and g > THR and b > THR:
                px[x, y] = (r, g, b, 0)
                n += 1
    return im, n

art, keyed = key_light(Image.open(SRC))
w, h = art.size
row = int(h * 0.955)
samples = [art.load()[int(w * f), row] for f in (0.25, 0.4, 0.6, 0.75)]
bg = tuple(sum(c[i] for c in samples) // len(samples) for i in range(3))
print('  keyed px:', keyed, '| bg:', bg)

def make(out, size, scale):
    canvas = Image.new('RGBA', (size, size), bg + (255,))
    aw = int(size * scale)
    ar = art.resize((aw, aw), Image.LANCZOS)
    canvas.paste(ar, ((size - aw) // 2, (size - aw) // 2), ar)
    canvas.convert('RGB').save(out, 'PNG')

make('icons/icon-512.png', 512, 0.90)
make('icons/icon-192.png', 192, 0.90)
make('icons/icon-maskable-512.png', 512, 0.62)
Image.open('icons/icon-512.png').convert('RGB').resize((180, 180), Image.LANCZOS).save('icons/apple-touch-icon.png')
Image.open('icons/icon-512.png').convert('RGB').resize((32, 32), Image.LANCZOS).save('icons/favicon-32.png')
for f in ['icons/icon_001.jpg', 'icons/icon_002.jpg']:
    if os.path.exists(f): os.remove(f)

print()
print('=== 白邊檢查 ===')
for f in ['icons/icon-512.png','icons/icon-maskable-512.png','icons/icon-192.png','icons/apple-touch-icon.png','icons/favicon-32.png']:
    im = Image.open(f).convert('RGB')
    ww, hh = im.size
    pts = [(2,2),(ww-3,2),(2,hh-3),(ww-3,hh-3),(ww//2,2),(2,hh//2),(ww//2,hh-3),(ww-3,hh//2)]
    px = [im.getpixel(p) for p in pts]
    whites = [p for p in px if p[0]>225 and p[1]>225 and p[2]>225]
    print('  %-32s 白邊=%d 角落=%s' % (f, len(whites), px[0]))
