import httpx
import json

url = "https://api.bhuntr.com/v1.0/contest/list"
params = {
    "tz": "Asia/Taipei",
    "lang": "tw",
    "sort": "newest",
    "location": "none",
    "limit": 50,
    "skip": 0
}

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

resp = httpx.get(url, params=params, headers=headers)
print("Status code:", resp.status_code)
data = resp.json()
print("Keys in payload:", data.keys() if isinstance(data, dict) else type(data))
if isinstance(data, dict):
    payload = data.get("payload", {})
    contest_list = payload.get("list", [])
    print("Contest list length:", len(contest_list))
    if contest_list:
        print("First title:", contest_list[0].get("title"))
        # 尋找是否包含《我的美好回憶》
        match = [c for c in contest_list if "美好回憶" in c.get("title", "")]
        print("Found 塔木德:", len(match))
