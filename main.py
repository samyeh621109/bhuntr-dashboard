import argparse
import json
from typing import List, Dict, Any
from tabulate import tabulate

from bhuntr_scraper import BHuntrScraper
from qual_classifier import QualificationClassifier
from generate_web import generate_html_app

def filter_competitions(
    results: List[Dict[str, Any]], 
    target: str = "all", 
    category_filter: str = None
) -> List[Dict[str, Any]]:
    filtered = []
    for item in results:
        qual = item["qualifications"]
        categories = item["categories"]
        
        # 資格篩選
        if target == "student" and not qual["student_eligible"]:
            continue
        if target == "social" and not qual["social_eligible"]:
            continue
        if target == "elementary" and not qual["elementary_eligible"]:
            continue
        if target == "student_only" and qual["label"] != "僅限學生資格":
            continue
        if target == "social_only" and qual["label"] != "僅限社會人士資格":
            continue
            
        # 分類篩選
        if category_filter and not any(category_filter.lower() in c.lower() for c in categories):
            continue

        filtered.append(item)
    return filtered

def display_table(items: List[Dict[str, Any]]):
    table_data = []
    for idx, item in enumerate(items, 1):
        quals = item["qualifications"]["label"]
        elem_qual = item["qualifications"]["elementary_label"]
        cats = ", ".join(item["categories"])
        prize = f"${item['prize_total']:,}" if item['prize_total'] else "未提供"
        title = item["title"]
        if len(title) > 30:
            title = title[:28] + "..."
            
        table_data.append([
            idx,
            title,
            cats,
            quals,
            elem_qual,
            prize,
            item["url"]
        ])
    
    headers = ["序號", "比賽標題", "領域分類", "資格標籤", "國小生資格", "總獎金", "比賽連結"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def main():
    parser = argparse.ArgumentParser(description="獎金獵人 (BHuntr) 比賽爬蟲與資格/類別自動分類工具")
    parser.add_argument("--target", choices=["all", "student", "social", "elementary", "student_only", "social_only"], default="all",
                        help="篩選資格: all, student, social, elementary (國小生可報), student_only, social_only")
    parser.add_argument("--category", type=str, default=None, help="篩選特定類別名稱 (例如: 視覺設計, 攝影影音, 軟體程式...)")
    parser.add_argument("--pages", type=str, default="5", help="爬取頁數深度 (填數字，或填 'all' 自動全爬無上限)")
    parser.add_argument("--sort", choices=["prize", "newest"], default="prize", help="排序規則: prize (總獎金高到低), newest (最新發布)")
    parser.add_argument("--export", type=str, default=None, help="指定輸出 JSON 檔案路徑 (例如: output.json)")
    parser.add_argument("--web", action="store_true", default=True, help="自動生成前端互動式 HTML 網頁 (預設開啟生成 index.html)")
    
    args = parser.parse_args()

    if args.pages.lower() == "all" or args.pages == "0":
        max_pages = None
        pages_str = "全站無上限（爬取所有頁面）"
    else:
        try:
            max_pages = int(args.pages)
            pages_str = f"{max_pages} 頁"
        except ValueError:
            max_pages = 5
            pages_str = "5 頁 (預設)"

    print(f"🔍 正在從 獎金獵人 (BHuntr) 抓取最新比賽資料 (深度: {pages_str})...")
    scraper = BHuntrScraper()
    classifier = QualificationClassifier()

    try:
        raw_contests = scraper.fetch_competitions(max_pages=max_pages)
        print(f"成功擷取到 {len(raw_contests)} 筆比賽數據，開始進行智慧資格與分類標籤化...")

        results = [classifier.classify(c) for c in raw_contests]
        filtered_results = filter_competitions(results, target=args.target, category_filter=args.category)

        # 排序
        if args.sort == "prize":
            filtered_results.sort(key=lambda x: x["prize_total"] or 0, reverse=True)
            print("💰 已依照總獎金金額（從高到低）排序完成！")

        print(f"\n✅ 分析完成！符合條件比賽共 {len(filtered_results)} 筆：\n")
        display_table(filtered_results[:30]) # 前 30 筆預覽

        if args.export:
            with open(args.export, "w", encoding="utf-8") as f:
                json.dump(filtered_results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 已將完整數據匯出至 JSON: {args.export}")

        if args.web:
            generate_html_app(filtered_results, "index.html")

    finally:
        scraper.close()

if __name__ == "__main__":
    main()
