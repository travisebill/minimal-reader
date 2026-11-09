from playwright.sync_api import sync_playwright
import time

SITE = 'https://travisebill.github.io/minimal-reader/'

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox'])
    ctx = b.new_context(viewport={'width': 412, 'height': 915}, locale='zh-TW',
        user_agent='Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
        is_mobile=True, has_touch=True)
    pg = ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:150]))

    print('=== 1. 輸入文字 → 進入閱讀模式 ===')
    pg.goto(SITE, wait_until='networkidle', timeout=60000)
    time.sleep(5)
    pg.fill('#textInput', '這是一段測試文字，用來驗證輸入與朗讀功能是否正常運作。' * 6)
    time.sleep(1)
    # 找切換到閱讀模式的按鈕
    clicked = pg.evaluate('''() => {
      const bs = [...document.querySelectorAll('button')];
      const b = bs.find(x => /開始|閱讀|朗讀|轉換|進入/.test(x.innerText||''));
      if (b) { b.click(); return b.innerText.trim().slice(0,20); }
      return null;
    }''')
    print('  點擊:', clicked)
    time.sleep(3)
    st = pg.evaluate('''() => {
      const rv = document.getElementById('readerView');
      const rc = document.getElementById('readerContent');
      const iv = document.getElementById('inputView');
      return {
        readerViewVisible: rv ? !rv.classList.contains('hidden') : null,
        readerContentLen: rc ? (rc.innerText||'').length : null,
        inputViewHidden: iv ? iv.classList.contains('hidden') : null,
        totalPages: (document.getElementById('totalPageNum')||{}).textContent,
        bodyLen: document.body.innerText.length,
      };
    }''')
    print('  ', st)
    pg.screenshot(path='/Users/nigo/.openclaw/workspace/agents/ryo/media/reader_mode.png')

    print()
    print('=== 2. 離線對照（純對照，不加絕對門檻 — 教訓）===')
    def probe():
        return pg.evaluate('''() => {
          const t = document.body.innerText;
          return { len: t.length, tw: !!window.tailwind,
                   readerLen: (document.getElementById('readerContent')||{innerText:''}).innerText.length,
                   pages: (document.getElementById('totalPageNum')||{}).textContent || '' };
        }''')
    on = probe()
    ctx.set_offline(True)
    pg.reload(wait_until='domcontentloaded', timeout=30000)
    time.sleep(6)
    off = probe()
    ctx.set_offline(False)
    print('  online :', on)
    print('  offline:', off)
    match = (on['len'] == off['len'] and on['tw'] == off['tw'] and on['readerLen'] == off['readerLen'])
    print('  結果   :', '✅ 線上與離線完全一致（離線可用）' if match else '❌ 有差異')

    print()
    print('=== 3. localStorage 持久化（閱讀歷史）===')
    ls = pg.evaluate("() => Object.keys(localStorage).map(k => k + '=' + String(localStorage.getItem(k)).length)")
    print('  ', ls)

    print()
    print('=== 4. 錯誤 ===', len(errs))
    for e in errs[:5]: print('   -', e)
    b.close()
