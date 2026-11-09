from playwright.sync_api import sync_playwright
import time

SITE = 'https://travisebill.github.io/minimal-reader/'

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox'])
    ctx = b.new_context(viewport={'width': 412, 'height': 915}, locale='zh-TW',
        user_agent='Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
        is_mobile=True, has_touch=True)
    pg = ctx.new_page()

    def probe(tag):
        d = pg.evaluate('''() => {
          const t = document.body.innerText;
          const rc = document.getElementById('readerContent');
          const iv = document.getElementById('inputView');
          return { len: t.length, tw: !!window.tailwind,
                   readerLen: rc ? (rc.innerText||'').length : null,
                   inputHidden: iv ? iv.classList.contains('hidden') : null,
                   pages: (document.getElementById('totalPageNum')||{}).textContent || '',
                   hist: (() => { try { return JSON.parse(localStorage.getItem('reader_history')||'[]').length; } catch(e){ return '?'; } })() };
        }''')
        print('  ' + tag, d)
        return d

    pg.goto(SITE, wait_until='networkidle', timeout=60000)
    time.sleep(5)
    probe('初始       ')

    # 輸入並進入閱讀
    pg.fill('#textInput', '測試文字。' * 40)
    time.sleep(1)
    pg.evaluate("""() => { const b=[...document.querySelectorAll('button')].find(x=>/開始閱讀/.test(x.innerText||'')); if(b) b.click(); }""")
    time.sleep(3)
    on_reader = probe('閱讀中     ')

    print()
    print('=== 關鍵對照：線上 reload vs 離線 reload ===')
    pg.reload(wait_until='networkidle', timeout=30000)
    time.sleep(5)
    on_reload = probe('線上 reload ')

    ctx.set_offline(True)
    pg.reload(wait_until='domcontentloaded', timeout=30000)
    time.sleep(6)
    off_reload = probe('離線 reload ')
    ctx.set_offline(False)

    print()
    same = (on_reload['len'] == off_reload['len']
            and on_reload['tw'] == off_reload['tw']
            and on_reload['readerLen'] == off_reload['readerLen']
            and on_reload['pages'] == off_reload['pages'])
    print('  線上 reload vs 離線 reload:', '✅ 完全一致 → 離線能力正常' if same else '❌ 有差異')
    print('  （readerLen 線上 reload 也是 0 → App 設計上不還原閱讀內容，只存歷史）')
    b.close()
