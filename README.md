# TXT → 自動日誌（Astro + GitHub Actions + Vercel）

只要把 `.txt` 放進 `inbox/`，其餘全自動：
1) GitHub Actions 會把 TXT 轉成帶 Frontmatter 的 Markdown，依「分類/年/月」歸檔到 `src/content/posts/…`。  
2) 推到 main 後，Vercel 會自動重新部署，網站立即更新。

## 一次搞定步驟

1. **把這個專案放上你的 GitHub**
   - 新建一個 repo，把本專案所有檔案推上去。

2. **連接 Vercel**
   - 到 Vercel 新建專案，選取剛剛的 GitHub repo。
   - Framework 選 **Astro**（Vercel 會自動偵測），Build Command 預設即可。
   - 部署完成後會得到一個網址（如 `https://xxx.vercel.app`）。

3. **開始投遞 TXT**
   - 直接在 GitHub 網頁把 `.txt` 上傳到 `inbox/`（或用 `tools/upload_txt.py` 上傳）。
   - 當有 `.txt` 進入 `inbox/` 時，GitHub Actions 會觸發，把它變成 Markdown，轉存到 `src/content/posts/…`，同時把原 TXT 移到 `processed/`。
   - Vercel 會自動重新部署，幾十秒內網站就會顯示新文章。

## 檔名與內容規範（可選，但能提高準確度）

- **檔名推薦格式**：`YYYY-MM-DD__分類__標題.txt`
  - 例如：`2025-08-10__生活__散步的記錄.txt`
- **或在檔案前幾行寫 Metadata**（優先於檔名）：
  ```
  Title: 散步的記錄
  Category: 生活
  Tags: 心情, 日常
  ```
  後面就寫內文。第一行若是 `# 標題` 也會被當作標題。

- 如果沒提供日期，系統會用「台北時區」的今天日期。分類預設為 `uncategorized`。

## 目錄結構

```
inbox/                 # 丟 TXT 的地方（觸發器）
processed/             # 已處理過的 TXT 會被搬到這裡
scripts/ingest_txt.py  # 轉檔與歸檔腳本（GitHub Action 會呼叫）
src/content/posts/     # 生成後的 Markdown 會放在這裡
src/pages/             # Astro 頁面（首頁、文章頁）
.github/workflows/     # GitHub Actions 設定
vercel.json            # Vercel 設定（可用預設）
```

## 進階：本地一鍵上傳（可選）

若你已經 clone repo 並設定好 git，直接執行：
```bash
python3 tools/upload_txt.py /path/to/你的.txt
```
它會把檔案複製到 `inbox/`、建立 commit 並推送，接著就自動轉檔＋部署了。

## 自訂

- 想換佈景/樣式：改 `src/layouts/PostLayout.astro` 與 `src/pages/index.astro`。
- 想改分類路徑或 Frontmatter 欄位：調整 `scripts/ingest_txt.py` 與 `src/content/config.ts`。

## 常見問題
- **會不會重複處理**？不會。TXT 轉檔後會被移到 `processed/`。
- **可以用子資料夾嗎**？可以。`inbox/` 底下任何層級的 `.txt` 都會被處理。
- **支援中文檔名/標題嗎**？可以。檔案實際路徑用簡單的 slug 規則處理，中文也能正常瀏覽。

— Happy logging!