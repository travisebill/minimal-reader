from PIL import Image
import os

# 教訓：原圖是圓角方形 + 四角外側近白 → 轉 alpha 再以 app 主色補底
def key_light(im, thr=232):
    im = im.convert('RGBA')
    px = im.load()
    n = 0
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a > 0 and r > thr and g > thr and b > thr:
                px[x, y] = (r, g, b, 0)
                n += 1
    return im, n

def make(src, out, size, scale, bg):
    art, n = key_light(Image.open(src))
    # 取 artwork 內緣平均色當底色
    w, h = art.size
    row = int(h * 0.955)
    samples = [art.load()[int(w * f), row] for f in (0.25, 0.4, 0.6, 0.75)]
    real_bg = tuple(sum(c[i] for c in samples) // len(samples) for i in range(3)) if all(c[3] for c in samples) else bg
    canvas = Image.new('RGBA', (size, size), real_bg + (255,))
    aw = int(size * scale)
    ar = art.resize((aw, aw), Image.LANCZOS)
    canvas.paste(ar, ((size - aw) // 2, (size - aw) // 2), ar)
    canvas.convert('RGB').save(out, 'PNG')
    return n, real_bg

for src in ['icons/icon_001.jpg', 'icons/icon_002.jpg']:
    base = src.split('/')[-1].replace('.jpg', '')
    for suffix, size, scale in [('', 512, 0.90), ('-192', 192, 0.90), ('-maskable-512', 512, 0.62)]:
        out = 'icons/icon%s.png' % (('-512' if suffix == '' else suffix) if suffix != '-192' else '-192')
        n, bg = make(src, out, size, scale, (24, 24, 27))
        print('  %-34s keyed=%-6d bg=%s' % (out, n, bg))

# apple-touch / favicon 用 icon-001
import shutil
shutil.copy('icons/icon-512.png', 'icons/icon-192.png')
Image.open('icons/icon-512.png').convert('RGB').resize((180, 180), Image.LANCZOS).save('icons/apple-touch-icon.png')
Image.open('icons/icon-512.png').convert('RGB').resize((32, 32), Image.LANCZOS).save('icons/favicon-32.png')
os.remove('icons/_placeholder.png')
print()
print('=== 角落白邊檢查（應全為綠）===')
for f in ['icons/icon-512.png', 'icons/icon-maskable-512.png', 'icons/icon-192.png', 'icons/apple-touch-icon.png']:
    im = Image.open(f).convert('RGB')
    w, h = im.size
    pts = [(2,2),(w-3,2),(2,h-3),(w-3,h-3),(w//2,2),(2,h//2),(w//2,h-3),(w-3,h//2)]
    px = [im.getpixel(p) for p in pts]
    whites = [p for p in px if p[0]>225 and p[1]>225 and p[2]>225]
    print('  %-32s 白邊=%d  角落=%s' % (f, len(whites), px[0]))
