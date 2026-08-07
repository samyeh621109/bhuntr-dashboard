import json
import os
from typing import List, Dict, Any

def generate_html_app(data: List[Dict[str, Any]], output_file: str = "index.html", max_embed_items: int = 1500):
    """
    將比賽數據渲染為現代化、具震撼力且支援高階動態搜尋、獎金排序與身份過濾的獨立 Web 應用。
    為了網頁開啟與檢索效能，優先載入頂級高獎金與最新熱門賽事 (預設 1500 筆)，完整 48,000+ 筆資料保存於 JSON。
    """
    embed_data = data[:max_embed_items]
    json_data_str = json.dumps(embed_data, ensure_ascii=False)
    
    html_template = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>獎金獵人 BHuntr - 智慧比賽儀表板與資格分類器</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.1);
            --accent-gold: #f59e0b;
            --accent-blue: #38bdf8;
            --accent-purple: #a855f7;
            --accent-pink: #ec4899;
            --accent-green: #10b981;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Noto Sans TC', 'Outfit', sans-serif;
            background: var(--bg-gradient);
            background-attachment: fixed;
            color: var(--text-main);
            min-height: 100vh;
            padding-bottom: 60px;
        }}

        header {{
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--card-border);
            position: sticky;
            top: 0;
            z-index: 100;
            padding: 1.25rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }}

        .logo-area {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .logo-badge {{
            background: linear-gradient(135deg, var(--accent-gold), var(--accent-pink));
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            box-shadow: 0 0 15px rgba(245, 158, 11, 0.4);
        }}

        .logo-title {{
            font-size: 1.5rem;
            font-weight: 900;
            background: linear-gradient(to right, #ffffff, #93c5fd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .stats-banner {{
            display: flex;
            gap: 20px;
            background: rgba(255,255,255,0.05);
            padding: 8px 16px;
            border-radius: 30px;
            border: 1px solid var(--card-border);
            font-size: 0.9rem;
        }}

        .stat-item span {{
            font-weight: 700;
            color: var(--accent-blue);
        }}

        .container {{
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 1.5rem;
        }}

        /* 控制面板與搜尋區 */
        .controls-panel {{
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: var(--glass-shadow);
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
        }}

        .search-row {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}

        .search-input-wrap {{
            flex: 1;
            min-width: 280px;
            position: relative;
        }}

        .search-input-wrap input {{
            width: 100%;
            padding: 0.9rem 1.2rem;
            border-radius: 12px;
            border: 1px solid var(--card-border);
            background: rgba(15, 23, 42, 0.6);
            color: var(--text-main);
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
        }}

        .search-input-wrap input:focus {{
            border-color: var(--accent-blue);
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
        }}

        .select-wrap select {{
            padding: 0.9rem 1.2rem;
            border-radius: 12px;
            border: 1px solid var(--card-border);
            background: rgba(15, 23, 42, 0.8);
            color: var(--text-main);
            font-size: 1rem;
            cursor: pointer;
            outline: none;
            transition: all 0.3s ease;
        }}

        .select-wrap select:focus {{
            border-color: var(--accent-purple);
        }}

        .filter-tags {{
            display: flex;
            gap: 0.6rem;
            flex-wrap: wrap;
            align-items: center;
        }}

        .tag-label {{
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 600;
        }}

        .chip {{
            padding: 6px 14px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--card-border);
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.25s ease;
            user-select: none;
        }}

        .chip:hover {{
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
        }}

        .chip.active {{
            background: linear-gradient(135deg, var(--accent-blue), #2563eb);
            color: white;
            border-color: transparent;
            box-shadow: 0 0 12px rgba(37, 99, 235, 0.4);
        }}

        .chip.active.gold {{
            background: linear-gradient(135deg, var(--accent-gold), #d97706);
            box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
        }}

        /* 卡片網格 */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1.5rem;
        }}

        .card {{
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            box-shadow: var(--glass-shadow);
        }}

        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
            opacity: 0.7;
            transition: opacity 0.3s;
        }}

        .card:hover {{
            transform: translateY(-6px) scale(1.01);
            border-color: rgba(255, 255, 255, 0.25);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
        }}

        .card:hover::before {{
            opacity: 1;
            background: linear-gradient(90deg, var(--accent-gold), var(--accent-pink));
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 0.8rem;
        }}

        .prize-badge {{
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: #fff;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 800;
            font-size: 0.95rem;
            box-shadow: 0 2px 10px rgba(245, 158, 11, 0.3);
            white-space: nowrap;
        }}

        .card-title {{
            font-size: 1.15rem;
            font-weight: 700;
            line-height: 1.4;
            color: #ffffff;
            margin-bottom: 1rem;
        }}

        .qual-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 1rem;
        }}

        .badge {{
            font-size: 0.75rem;
            padding: 3px 10px;
            border-radius: 6px;
            font-weight: 600;
        }}

        .badge-elem {{
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }}

        .badge-student {{
            background: rgba(56, 189, 248, 0.2);
            color: #7dd3fc;
            border: 1px solid rgba(56, 189, 248, 0.4);
        }}

        .badge-social {{
            background: rgba(168, 85, 247, 0.2);
            color: #c084fc;
            border: 1px solid rgba(168, 85, 247, 0.4);
        }}

        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            margin-top: auto;
        }}

        .cat-list {{
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .btn-link {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 8px 16px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.85rem;
            transition: all 0.2s ease;
        }}

        .btn-link:hover {{
            background: var(--accent-blue);
            color: #0f172a;
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
        }}

        .empty-state {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 4rem 1rem;
            color: var(--text-muted);
            font-size: 1.2rem;
        }}
    </style>
</head>
<body>

    <header>
        <div class="logo-area">
            <div class="logo-badge">🏆</div>
            <div class="logo-title">BHuntr 比賽賽事分析儀表板</div>
        </div>
        <div class="stats-banner">
            <div class="stat-item">總賽事：<span id="total-count">0</span></div>
            <div class="stat-item">國小生可報：<span id="elem-count">0</span></div>
        </div>
    </header>

    <div class="container">
        <!-- 搜尋與過濾區 -->
        <div class="controls-panel">
            <div class="search-row">
                <div class="search-input-wrap">
                    <input type="text" id="search-box" placeholder="🔍 搜尋比賽關鍵字、主辦單位、獎項..." oninput="filterData()">
                </div>
                <div class="select-wrap">
                    <select id="sort-select" onchange="filterData()">
                        <option value="prize-desc">💰 總獎金最高優先</option>
                        <option value="prize-asc">🪙 總獎金最低優先</option>
                        <option value="default">🕒 最新發布優先</option>
                    </select>
                </div>
            </div>

            <!-- 身分標籤過濾 -->
            <div class="filter-tags">
                <span class="tag-label">參賽身分：</span>
                <div class="chip active gold" onclick="setQualFilter('all', this)">全部對象</div>
                <div class="chip" onclick="setQualFilter('elementary', this)">👧👦 國小生可參加</div>
                <div class="chip" onclick="setQualFilter('student', this)">🎓 學生資格</div>
                <div class="chip" onclick="setQualFilter('social', this)">💼 社會人士資格</div>
                <div class="chip" onclick="setQualFilter('student_only', this)">🔒 僅限學生</div>
            </div>

            <!-- 領域分類過濾 -->
            <div class="filter-tags" id="category-chips">
                <span class="tag-label">領域類別：</span>
                <div class="chip active" onclick="setCatFilter('all', this)">全部分類</div>
                <!-- 動態注入分類 -->
            </div>
        </div>

        <!-- 比賽卡片列表 -->
        <div class="cards-grid" id="cards-container"></div>
    </div>

    <script>
        const rawData = {json_data_str};
        let currentQualFilter = 'all';
        let currentCatFilter = 'all';

        // 初始化領域分類按鈕
        function initCategoryChips() {{
            const catSet = new Set();
            rawData.forEach(item => {{
                if (item.categories) {{
                    item.categories.forEach(c => catSet.add(c));
                }}
            }});

            const container = document.getElementById('category-chips');
            catSet.forEach(cat => {{
                const chip = document.createElement('div');
                chip.className = 'chip';
                chip.innerText = cat;
                chip.onclick = function() {{ setCatFilter(cat, this); }};
                container.appendChild(chip);
            }});
        }}

        function setQualFilter(val, el) {{
            document.querySelectorAll('.filter-tags:nth-of-type(1) .chip').forEach(c => c.classList.remove('active', 'gold'));
            el.classList.add('active', 'gold');
            currentQualFilter = val;
            filterData();
        }}

        function setCatFilter(val, el) {{
            document.querySelectorAll('#category-chips .chip').forEach(c => c.classList.remove('active'));
            el.classList.add('active');
            currentCatFilter = val;
            filterData();
        }}

        function filterData() {{
            const keyword = document.getElementById('search-box').value.toLowerCase();
            const sortMode = document.getElementById('sort-select').value;

            let filtered = rawData.filter(item => {{
                // 關鍵字比對
                const matchKw = !keyword || 
                    item.title.toLowerCase().includes(keyword) || 
                    (item.categories && item.categories.some(c => c.toLowerCase().includes(keyword))) ||
                    (item.qualifications.reasons && item.qualifications.reasons.some(r => r.toLowerCase().includes(keyword)));

                // 身份比對
                let matchQual = true;
                const q = item.qualifications;
                if (currentQualFilter === 'elementary') matchQual = q.elementary_eligible;
                else if (currentQualFilter === 'student') matchQual = q.student_eligible;
                else if (currentQualFilter === 'social') matchQual = q.social_eligible;
                else if (currentQualFilter === 'student_only') matchQual = (q.label === '僅限學生資格');

                // 類別比對
                let matchCat = true;
                if (currentCatFilter !== 'all') {{
                    matchCat = item.categories && item.categories.includes(currentCatFilter);
                }}

                return matchKw && matchQual && matchCat;
            }});

            // 排序處理
            if (sortMode === 'prize-desc') {{
                filtered.sort((a, b) => (b.prize_total || 0) - (a.prize_total || 0));
            }} else if (sortMode === 'prize-asc') {{
                filtered.sort((a, b) => (a.prize_total || 0) - (b.prize_total || 0));
            }}

            renderCards(filtered);
            updateStats(filtered.length);
        }}

        function updateStats(filteredCount) {{
            document.getElementById('total-count').innerText = filteredCount;
            const elemCount = rawData.filter(i => i.qualifications.elementary_eligible).length;
            document.getElementById('elem-count').innerText = elemCount;
        }}

        function renderCards(items) {{
            const container = document.getElementById('cards-container');
            if (items.length === 0) {{
                container.innerHTML = '<div class="empty-state">🤔 沒有找到符合條件的比賽</div>';
                return;
            }}

            container.innerHTML = items.map(item => {{
                const prize = item.prize_total ? `$${{item.prize_total.toLocaleString()}}` : '未額外標明';
                const q = item.qualifications;

                let badgesHtml = '';
                if (q.elementary_eligible) badgesHtml += '<span class="badge badge-elem">👧👦 國小生可報名</span>';
                if (q.student_eligible) badgesHtml += '<span class="badge badge-student">🎓 學生資格</span>';
                if (q.social_eligible) badgesHtml += '<span class="badge badge-social">💼 社會人士</span>';

                const cats = item.categories ? item.categories.join(' · ') : '綜合類別';

                return `
                    <div class="card">
                        <div class="card-header">
                            <div class="prize-badge">${{prize}}</div>
                        </div>
                        <div class="card-title">${{escapeHtml(item.title)}}</div>
                        <div class="qual-badges">${{badgesHtml}}</div>
                        <div class="card-footer">
                            <div class="cat-list">📂 ${{escapeHtml(cats)}}</div>
                            <a href="${{item.url}}" target="_blank" class="btn-link">檢視比賽 ➔</a>
                        </div>
                    </div>
                `;
            }}).join('');
        }}

        function escapeHtml(str) {{
            return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
        }}

        // 初始化發動
        initCategoryChips();
        filterData();
    </script>
</body>
</html>
"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"✨ 成功產出高品質互動式前端 Web 頁面: {output_file}")

if __name__ == "__main__":
    if os.path.exists("full_elementary.json"):
        with open("full_elementary.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        generate_html_app(data, "index.html")
    else:
        print("請先產出 JSON 資料檔 (full_elementary.json)")
