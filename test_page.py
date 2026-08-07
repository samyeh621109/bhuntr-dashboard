from bhuntr_scraper import BHuntrScraper

scraper = BHuntrScraper()
for page in range(1, 6):
    html = scraper.client.get(f"https://bhuntr.com/tw/competitions?sort=newest&location=none&page={page}").text
    state = scraper.extract_embedded_state(html)
    contest_list = state.get("bypass", {}).get("contestResult", {}).get("list", []) if state else []
    print(f"Page {page}: {len(contest_list)} contests")
    for c in contest_list:
        if "美好回憶" in c.get("title", ""):
            print(f"🎯 找到了！在第 {page} 頁：{c.get('title')}")
