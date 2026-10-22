# 極簡手機閱讀器

極簡的純前端閱讀 App — **PWA 版本，可安裝、可離線使用**。

> 原始碼由 [Gemini](https://gemini.google.com/) 生成，原始分享對話：
> <https://share.gemini.google/S8bCZvaCmcnc>

## 功能

- **TTS 朗讀** — 使用瀏覽器內建 Web Speech API 朗讀全文
- **分頁閱讀** — 自動分頁、頁碼顯示、跳頁
- **自動捲動** — 朗讀時自動捲動，可暫停
- **深淺色主題** — 跟隨系統或手動切換
- **閱讀歷史** — localStorage 記錄
- **離線可用** — 所有依賴已本地化，無外部請求

## PWA

| 項目 | 說明 |
|------|------|
| Manifest | `manifest.webmanifest`（standalone、zinc 主題、3 種 icon 含 maskable） |
| Service Worker | `sw.js` — app shell cache-first、導航 network-first、靜態資源 stale-while-revalidate |
| 離線 | ✅ Tailwind 已本地化至 `vendor/tailwind.js`，線上殘留 CDN 引用 0 |
| 安裝 | iOS：Safari 分享 → 加入主畫面；Android Chrome：選單 → 安裝應用程式 |

## 開發

```bash
python3 -m http.server 8899   # 需經 HTTP 才能註冊 Service Worker
# → http://127.0.0.1:8899
```

## 技術棧

Tailwind CSS（CDN 版，已本地化）· 原生 JS · Web Speech API · localStorage

## License

MIT
