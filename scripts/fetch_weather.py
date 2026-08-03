#!/usr/bin/env python3
"""定時抓資料的範例腳本。

這支腳本示範「動態報表」的標準做法：由 GitHub Actions 定時執行，
把抓回來的資料存成 data/ 底下的 JSON，前端網頁只負責讀 JSON 畫圖。

這樣做的好處：
  1. 不需要伺服器，GitHub Pages 只吐靜態檔案
  2. 私密的 API key 放在 GitHub Secrets，永遠不會出現在前端程式碼裡
  3. 每天跑一次就自然累積出歷史資料，趨勢圖才有東西可畫

要改成抓你自己的資料，把 fetch_weather() 換掉就行，其他都可以留著。
只用 Python 標準函式庫，所以不需要 pip install 任何東西。
"""

import json
import os
import ssl
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ------------------------------------------------------------------
# 設定
# ------------------------------------------------------------------

LOCATION = {"name": "臺北", "latitude": 25.0478, "longitude": 121.5319}

# 保留多少天的歷史資料
KEEP_DAYS = 365

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "weather-daily.json"

# 如果你的 API 需要金鑰，就這樣讀（值設定在 GitHub repo 的
# Settings → Secrets and variables → Actions → New repository secret，
# 然後在 workflow 的 env: 區塊把它傳進來）。
# 絕對不要把金鑰直接寫在程式碼裡。
API_KEY = os.environ.get("MY_API_KEY")  # 這個範例用不到，僅示範位置


# ------------------------------------------------------------------
# 抓資料
# ------------------------------------------------------------------

def fetch_weather():
    """回傳 [{date, tmax, tmin, rain}, ...]，含最近幾天已完成的觀測。"""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude={latitude}&longitude={longitude}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=auto&past_days=3&forecast_days=1"
    ).format(**LOCATION)

    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "tools-report/1.0"})
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        data = json.load(resp)

    daily = data["daily"]
    rows = []
    for i, date in enumerate(daily["time"]):
        rows.append({
            "date": date,
            "tmax": daily["temperature_2m_max"][i],
            "tmin": daily["temperature_2m_min"][i],
            "rain": daily["precipitation_sum"][i],
        })
    return rows


# ------------------------------------------------------------------
# 合併並寫檔
# ------------------------------------------------------------------

def load_existing():
    if not OUT_PATH.exists():
        return {}
    try:
        with OUT_PATH.open(encoding="utf-8") as f:
            old = json.load(f)
        return {row["date"]: row for row in old.get("days", [])}
    except (ValueError, KeyError, TypeError) as exc:
        print("舊資料讀不出來，這次重新建立：%s" % exc, file=sys.stderr)
        return {}


def main():
    by_date = load_existing()
    before = len(by_date)

    for row in fetch_weather():
        # 同一天的資料以新抓到的為準（當天的數值會隨時間修正）
        if row["tmax"] is not None:
            by_date[row["date"]] = row

    days = [by_date[d] for d in sorted(by_date)][-KEEP_DAYS:]

    payload = {
        "location": LOCATION["name"],
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "unit": {"tmax": "°C", "tmin": "°C", "rain": "mm"},
        "days": days,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print("寫入 %s：%d 天（新增 %d 天）" % (OUT_PATH.name, len(days), len(days) - before))


if __name__ == "__main__":
    main()
