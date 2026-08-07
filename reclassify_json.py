import json
from qual_classifier import QualificationClassifier
from generate_web import generate_html_app

def sanitize_database(input_file: str):
    print(f"🔄 正在對數據庫 {input_file} 進行分類校正與品質清洗...")
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    classifier = QualificationClassifier()
    updated_data = []

    for item in data:
        # 重建純文字 text 用於傳入 classifier
        title = item.get("title", "")
        # 從現有欄位逆推全文字
        raw_guideline = item.get("guideline", "")
        clean_text = f"{title} {raw_guideline}"
        
        identify_limit = {}
        # 依據原有解析回推判別，若有 elementary_eligible, 帶入
        if item.get("qualifications", {}).get("elementary_eligible"):
            identify_limit["elementarySchool"] = True
        if item.get("qualifications", {}).get("student_eligible"):
            identify_limit["university"] = True
        if item.get("qualifications", {}).get("social_eligible"):
            identify_limit["nonStudent"] = True

        # 重新分類校正：100% 採用官方原生 categories 欄位
        categories_raw = item.get("categories", [])
        item["categories"] = classifier._resolve_categories(categories_raw)
        updated_data.append(item)

    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 成功清洗 {len(updated_data)} 筆賽事數據！")

if __name__ == "__main__":
    for file_path in ["full_contests.json", "full_elementary.json"]:
        try:
            sanitize_database(file_path)
        except Exception as e:
            print(f"清洗 {file_path} 失敗: {e}")
            
    # 重新生成 HTML
    with open("full_contests.json", "r", encoding="utf-8") as f:
        full_data = json.load(f)
    generate_html_app(full_data, "index.html")
