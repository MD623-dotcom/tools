# 工具箱

自己寫的小工具與報表，用 GitHub Pages 發佈：

**<https://md623-dotcom.github.io/tools/>**

## 結構

```
index.html                      首頁，列出所有工具
clock/index.html                時鐘
scripts/fetch_weather.py        定時抓資料的範例腳本
data/weather-daily.json         腳本產出的資料（由 Actions 自動更新）
.github/workflows/fetch-data.yml  每天執行腳本並 commit 資料
```

## 新增一個工具

1. 開一個新資料夾，例如 `invoice/`，裡面放 `index.html`
2. 打開根目錄的 `index.html`，在最上面的 `TOOLS` 陣列加一筆：

   ```js
   {
     name: "發票整理",
     desc: "一句話說明這個工具在幹嘛。",
     href: "invoice/",
     icon: "🧾",        // emoji 或內嵌 SVG 都可以
     tag: "報表"        // 可省略
   }
   ```
3. `git add -A && git commit -m "新增發票整理" && git push`

約一分鐘後線上就會出現。

## 改版

```bash
cd /Users/mindaou/tools
git add -A
git commit -m "改了什麼"
git push
```

## 動態報表的做法

私密的 API key **絕對不能**寫在前端程式碼裡（這個 repo 是公開的，前端 JS 任何人都看得到）。正確做法是讓 GitHub Actions 在伺服器端抓資料：

```
Actions 定時執行（key 放在 GitHub Secrets）
  → scripts/*.py 抓資料
  → 寫進 data/*.json
  → 自動 commit 回 repo
  → 前端網頁 fetch("../data/xxx.json") 畫圖
```

`scripts/fetch_weather.py` 加上 `.github/workflows/fetch-data.yml` 就是這個模式的完整範例，可以直接照著改。它每天台北時間早上 6:10 跑一次，把臺北的每日高低溫與雨量累積到 `data/weather-daily.json`。

要放金鑰：repo 的 **Settings → Secrets and variables → Actions → New repository secret**，然後在 workflow 的 `env:` 區塊傳進腳本。

要手動跑一次：repo 的 **Actions** 頁籤 → 選 workflow → **Run workflow**。
要停掉：同一頁的 **Disable workflow**。

## 注意

這是公開 repo，所以網站內容和 `data/` 裡的資料**任何人都看得到**。要放私密資料（財務、健康等），改用 Cloudflare Pages + Cloudflare Access，可以鎖成只有你的 Google 帳號登入才看得到。
