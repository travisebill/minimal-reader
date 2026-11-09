from playwright.sync_api import sync_playwright
import time

SITE = 'https://travisebill.github.io/minimal-reader/'
errors = []
FENCE = chr(96) * 3

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox'])
    ctx = b.new_context(
        viewport={'width': 412, 'height': 915},
        user_agent='Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
        is_mobile=True, has_touch=True, device_scale_factor=2.625, locale='zh-TW')
    pg = ctx.new_page()
    pg.on('console', lambda m: errors.append('console:' + m.text[:120]) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errors.append('PAGEERROR: ' + str(e)[:160]))

    print('=== 1. online load ===')
    pg.goto(SITE, wait_until='networkidle', timeout=60000)
    time.sleep(6)

    def probe():
        return pg.evaluate('''() => {
          const t = document.body.innerText;
          const b = document.body.firstElementChild;
          return {
            len: t.length,
            firstTag: b ? b.tagName : null,
            firstText: b ? (b.textContent||'').trim().slice(0,50) : null,
            hasTitle: t.includes('極簡') || t.includes('閱讀'),
            hasTailwind: !!window.tailwind,
            scriptCount: document.querySelectorAll('script').length,
            swCtl: !!navigator.serviceWorker.controller,
          };
        }''')

    on = probe()
    print('  ', on)

    print()
    print('=== 2. 渲染三驗（教訓）===')
    print('  首元素是預期元素 :', on['firstTag'], '(', on['firstText'], ')')
    print('  非預期文字        :', '❌ 有' if on['firstText'] and on['firstText'].startswith(chr(96)) else '✅ 無')
    src = pg.evaluate("() => document.documentElement.outerHTML")
    print('  殘留 fence        :', src.count(FENCE))
    print('  script 標籤平衡   :', on['scriptCount'], '/', src.count('</script>'))
    print('  殘留 CDN 引用     :', src.count('https://cdn.'))

    print()
    print('=== 3. SW cache ===')
    sw = pg.evaluate('''async () => {
      const c = await caches.open('minimal-reader-v1');
      const keys = await c.keys();
      const hit = await c.match('./index.html');
      const txt = hit ? await hit.text() : '';
      return { cacheKeys: keys.length, cachedHasFence: txt.indexOf(String.fromCharCode(96).repeat(3)) >= 0 };
    }''')
    print('  ', sw)

    print()
    print('=== 4. 功能實測：輸入文字 + 主題切換 ===')
    try:
        pg.fill('#textInput', '這是一段測試文字，用來驗證輸入與朗讀功能是否正常運作。')
        time.sleep(1)
        v = pg.evaluate("() => (document.getElementById('textInput')||{}).value || ''")
        print('  輸入框內容:', repr(v[:40]))
    except Exception as e:
        print('  fill err:', str(e)[:100])

    before = pg.evaluate("() => document.documentElement.className")
    pg.evaluate("() => { const b=document.getElementById('modeToggleBtn'); if(b) b.click(); }")
    time.sleep(1)
    after = pg.evaluate("() => document.documentElement.className")
    print('  主題切換:', before, '->', after)

    print()
    print('=== 5. 離線對照（線上 vs 離線同一組指標 — 教訓）===')
    ctx.set_offline(True)
    pg.reload(wait_until='domcontentloaded', timeout=30000)
    time.sleep(6)
    off = probe()
    print('  offline:', off)
    same = (off['len'] == on['len'] and off['hasTailwind'] == on['hasTailwind'])
    print('  離線可用:', '✅ 與線上一致' if same and off['len'] > 100 else '⚠️ 有差異')
    ctx.set_offline(False)

    print()
    print('=== 6. 頁面錯誤 ===', len(errors))
    for e in errors[:5]: print('   -', e)

    pg.screenshot(path='/Users/nigo/.openclaw/workspace/agents/ryo/media/reader_online.png')
    b.close()
