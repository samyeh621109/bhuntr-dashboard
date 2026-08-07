import base64
import json
import re
from typing import Dict, List, Any, Optional
import httpx
from bs4 import BeautifulSoup

class BHuntrScraper:
    """
    獎金獵人 (BHuntr) 專用爬蟲，支援多頁分頁抓取與資料解析。
    """
    BASE_URL = "https://bhuntr.com/tw/competitions"
    
    def __init__(self, timeout: float = 15.0):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        self.client = httpx.Client(headers=self.headers, timeout=timeout, follow_redirects=True)

    def fetch_competitions_raw_page(self, sort: str = "newest", location: str = "none", page: int = 1) -> str:
        """抓取指定頁數的找比賽頁面 HTML 內容"""
        url = f"{self.BASE_URL}?sort={sort}&location={location}&page={page}"
        resp = self.client.get(url)
        resp.raise_for_status()
        return resp.text

    def extract_embedded_state(self, html_content: str) -> Optional[Dict[str, Any]]:
        """從 HTML 中抽取加密的 window._[timestamp] Base64 資料並解碼為 dict"""
        pattern = r"window\._\d+\s*=\s*'([A-Za-z0-9+/=]+)'"
        match = re.search(pattern, html_content)
        if not match:
            return None
        
        b64_str = match.group(1)
        try:
            decoded_bytes = base64.b64decode(b64_str)
            decoded_json = json.loads(decoded_bytes.decode("utf-8"))
            return decoded_json
        except Exception as e:
            print(f"Base64 解碼失敗: {e}")
            return None

    def fetch_competitions(self, sort: str = "newest", location: str = "none", max_pages: Optional[int] = 5) -> List[Dict[str, Any]]:
        """
        獲取比賽清單資料。
        若 max_pages 為 None 或 <= 0，則全自動翻頁直到無新資料為止（爬取全站比賽）。
        """
        all_contests = []
        seen_ids = set()
        page = 1

        while True:
            if max_pages and max_pages > 0 and page > max_pages:
                break
                
            try:
                html = self.fetch_competitions_raw_page(sort=sort, location=location, page=page)
                state = self.extract_embedded_state(html)
                if not state:
                    break
                
                contest_list = state.get("bypass", {}).get("contestResult", {}).get("list", [])
                if not contest_list:
                    # 已到達最後一頁
                    break

                new_items_count = 0
                for c in contest_list:
                    cid = c.get("id")
                    if cid and cid not in seen_ids:
                        seen_ids.add(cid)
                        all_contests.append(c)
                        new_items_count += 1

                # 若整頁完全沒有新新增的資料，說明已被重定向或已重複無新筆數，中止爬取
                if new_items_count == 0:
                    break

                page += 1
            except Exception as e:
                print(f"抓取第 {page} 頁時發生錯誤: {e}")
                break

        return all_contests

    def fetch_single_contest_detail(self, alias: str) -> Optional[Dict[str, Any]]:
        """
        特定單一比賽的內頁抓取與完整 State 解析
        """
        url = f"{self.BASE_URL}/{alias}"
        try:
            resp = self.client.get(url)
            resp.raise_for_status()
            state = self.extract_embedded_state(resp.text)
            if state:
                return state.get("bypass", {}).get("contestItem")
        except Exception as e:
            print(f"抓取單一比賽 {alias} 詳細頁面失敗: {e}")
        return None

    def close(self):
        self.client.close()

if __name__ == "__main__":
    scraper = BHuntrScraper()
    try:
        contests = scraper.fetch_competitions(max_pages=3)
        print(f"多頁抓取測試：共抓取 {len(contests)} 筆比賽！")
    finally:
        scraper.close()
