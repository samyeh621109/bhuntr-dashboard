from typing import Dict, Any, List, Tuple
from bs4 import BeautifulSoup
import json
import re

# BHuntr 分類 ID 對照表 (常見編號)
CATEGORY_MAP = {
    "101": "視覺設計",
    "102": "攝影影音",
    "103": "音樂創作",
    "104": "文學寫作",
    "105": "軟體程式",
    "106": "企劃行銷",
    "107": "工業設計",
    "108": "建築空間",
    "109": "時尚造型",
    "110": "遊戲動畫",
    "111": "藝術創作",
    "112": "綜合創新"
}

STUDENT_KEYS = {
    "preschool", "elementarySchool", "juniorHighSchool", "seniorHighSchool", 
    "vocationalHighSchool", "university", "fiveYearJuniorCollege", 
    "twoYearJuniorCollege", "twoYearInstituteOfTechnology", 
    "fourYearInstituteOfTechnology", "graduateSchoolMastersProgram", 
    "graduateSchoolMastersProgramPartTime", "graduateSchoolDoctoralProgram", 
    "graduateSchoolDoctoralProgramPartTime"
}

class QualificationClassifier:
    """
    比賽分類與參賽資格分析器。
    結合結構化 API 欄位 (identifyLimit) 與 HTML 內文語意關鍵字解析。
    """
    
    STUDENT_KEYWORDS = [
        "在校生", "學生", "大專院校", "高中生", "國小", "國中", "高中", "高職", 
        "研究生", "碩士", "博士", "學童", "應屆畢業生", "在學證件", "學生證"
    ]
    
    SOCIAL_KEYWORDS = [
        "社會人士", "社會組", "不限年齡", "不限身份", "不限資格", "全民", 
        "一般民眾", "一般社會大眾", "愛好者", "各界人士", "個人或團體", "凡喜愛"
    ]

    STRICT_STUDENT_ONLY_KEYWORDS = [
        "僅限學生", "限在校生", "限大專", "限高中", "限國小", "限國中", "限在學", "限學生"
    ]

    STRICT_SOCIAL_ONLY_KEYWORDS = [
        "限社會人士", "非學生", "限社會組"
    ]

    @classmethod
    def clean_html(cls, raw_html: str) -> str:
        """移除 HTML 標籤取得純文字"""
        if not raw_html:
            return ""
        soup = BeautifulSoup(raw_html, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def classify(self, contest: Dict[str, Any]) -> Dict[str, Any]:
        """
        傳入單筆比賽 Dict，輸出具備完整資格與分類標籤的結構。
        """
        title = contest.get("title", "")
        raw_guideline = contest.get("guideline", "")
        clean_text = f"{title} {self.clean_html(raw_guideline)}"
        identify_limit = contest.get("identifyLimit", {}) or {}
        categories_raw = contest.get("categories", []) or []

        # 1. 解析比賽領域分類
        categories = self._resolve_categories(categories_raw, clean_text)

        # 2. 判斷學生與社會人士資格
        student_eligible, social_eligible, elementary_eligible, reasons = self._analyze_qualification(identify_limit, clean_text)

        # 綜合資格型態標籤
        if elementary_eligible:
            elementary_label = "國小生可參加"
        else:
            elementary_label = "非國小生限定"

        if student_eligible and social_eligible:
            qual_label = "學生與社會人士皆可"
        elif student_eligible and not social_eligible:
            qual_label = "僅限學生資格"
        elif not student_eligible and social_eligible:
            qual_label = "僅限社會人士資格"
        else:
            qual_label = "不限 / 需檢視細則"

        return {
            "id": contest.get("id"),
            "alias": contest.get("alias"),
            "title": title,
            "url": f"https://bhuntr.com/tw/competitions/{contest.get('alias')}" if contest.get("alias") else "",
            "prize_total": contest.get("prizeTotal", 0),
            "submit_end_time": contest.get("submitEndTime"),
            "categories": categories,
            "qualifications": {
                "label": qual_label,
                "student_eligible": student_eligible,
                "social_eligible": social_eligible,
                "elementary_eligible": elementary_eligible,
                "elementary_label": elementary_label,
                "reasons": reasons
            }
        }

    def _resolve_categories(self, category_ids: List[str], text: str = "") -> List[str]:
        """
        100% 遵照 BHuntr 官方原生的 categories 欄位進行映射。
        如果官方填錯或未填，完全尊重官方原生資料。
        """
        resolved = []
        for cid in category_ids:
            cid_str = str(cid)
            if cid_str in CATEGORY_MAP:
                resolved.append(CATEGORY_MAP[cid_str])
            elif cid:
                resolved.append(f"類別-{cid_str}")

        return resolved if resolved else ["未分類/綜合類別"]

    def _analyze_qualification(self, identify_limit: Dict[str, bool], text: str) -> Tuple[bool, bool, bool, List[str]]:
        student_eligible = False
        social_eligible = False
        elementary_eligible = False
        reasons = []

        is_none_limit = identify_limit.get("none", False)
        is_non_student_limit = identify_limit.get("nonStudent", False)
        is_elem_limit = identify_limit.get("elementarySchool", False) or identify_limit.get("preschool", False)

        # 檢查是否有任何學生選項設為 True
        student_limit_hits = [k for k in STUDENT_KEYS if identify_limit.get(k, False)]

        # 依據 API 欄位進行基本判定
        if is_none_limit:
            student_eligible = True
            social_eligible = True
            elementary_eligible = True
            reasons.append("API 設定為不限身份 (none=True)，國小生可報名")
        else:
            if student_limit_hits:
                student_eligible = True
                reasons.append(f"API 設定符合特定學生限制 ({', '.join(student_limit_hits)})")
            if is_elem_limit:
                elementary_eligible = True
                reasons.append("API 設定開放國小生/幼兒 (elementarySchool=True)")
            if is_non_student_limit:
                social_eligible = True
                reasons.append("API 設定允許非學生身分 (nonStudent=True)")

        # 內文文字強修正與補助檢查 (Semantic / Text matching)
        strict_student = any(w in text for w in self.STRICT_STUDENT_ONLY_KEYWORDS)
        strict_social = any(w in text for w in self.STRICT_SOCIAL_ONLY_KEYWORDS)
        has_student_kw = any(w in text for w in self.STUDENT_KEYWORDS)
        has_social_kw = any(w in text for w in self.SOCIAL_KEYWORDS)
        has_elem_kw = any(w in text for w in ["國小", "小學生", "兒童", "童", "幼兒", "低年級", "中年級", "高年級", "國小組", "小學"])

        if has_elem_kw:
            elementary_eligible = True
            reasons.append("內文包含『國小/兒童/低中高年級』相關對象關鍵字")

        if strict_student:
            student_eligible = True
            social_eligible = False
            reasons.append("文字簡介包含『僅限學生/限在校生』關鍵字")
        elif strict_social:
            student_eligible = False
            social_eligible = True
            elementary_eligible = False
            reasons.append("文字簡介包含『僅限社會人士』關鍵字")
        else:
            if has_student_kw and not student_eligible:
                student_eligible = True
                reasons.append("內文提及學生相關參賽關鍵字")
            if has_social_kw and not social_eligible:
                social_eligible = True
                reasons.append("內文提及社會人士/不限對象關鍵字")

        # 預設保護：若兩者皆無法判別，通常獎金獵人比賽多為全體皆可報名
        if not student_eligible and not social_eligible:
            student_eligible = True
            social_eligible = True
            elementary_eligible = True
            reasons.append("未偵測到排他性限制，預設開放大眾、學生與國小生報名")

        return student_eligible, social_eligible, elementary_eligible, reasons

if __name__ == "__main__":
    classifier = QualificationClassifier()
    sample_contest = {
        "id": 123,
        "alias": "test-contest",
        "title": "2026 全國大專院校程式設計大賽",
        "guideline": "<p>本競賽僅限大專院校在校學生參加，需檢附學生證影本。</p>",
        "identifyLimit": {"none": False, "university": True, "nonStudent": False},
        "categories": ["105"]
    }
    result = classifier.classify(sample_contest)
    print("測試範例結果:", json.dumps(result, ensure_ascii=False, indent=2))
