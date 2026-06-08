import streamlit as st
import pandas as pd
from weasyprint import HTML
import io

st.set_page_config(page_title="おれの出目表 自動作成", layout="wide")
st.title("📊 おれの出目表 PDF自動作成システム")
st.write("ミニロトの最新CSVファイルをアップロードすると、A4横1枚に綺麗に収まる出目表PDFを作成します。")

uploaded_file = st.file_uploader("ミニロトのCSVファイルをアップロードしてください", type=['csv'])

if uploaded_file is not None:
    try:
        # CSV読み込み
        df_csv = pd.read_csv(uploaded_file)
        
        # 列名変更（存在チェック付き）
        rename_dict = {
            '開催回': '回号', '第1数字': '本数字1', '第2数字': '本数字2',
            '第3数字': '本数字3', '第4数字': '本数字4', '第5数字': '本数字5',
            'ボーナス数字': 'ボーナス'
        }
        df_csv = df_csv.rename(columns=rename_dict)
        
        # 直近24回分
        df_analysis = df_csv.sort_values('回号').tail(24).reset_index(drop=True)
        
        # ガイドライン計算
        latest_row = df_analysis.iloc[-1]
        prev_row = df_analysis.iloc[-2]
        
        latest_nums = [int(latest_row[f'本数字{i}']) for i in range(1, 6)]
        prev_nums = [int(prev_row[f'本数字{i}']) for i in range(1, 6)]
        
        hot_zone = set()
        for n in latest_nums:
            for offset in [-1, 0, 1]:
                val = n + offset
                if 1 <= val <= 31: hot_zone.add(val)
                
        dull_zone = set()
        for n in prev_nums:
            for offset in range(-3, 4):
                val = n + offset
                if 1 <= val <= 31: dull_zone.add(val)
                
        left_loop = [29, 30, 31]
        main_area = list(range(1, 32))
        right_loop = [1, 2, 3]
        
        # HTML/CSS 組み立て
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            @page { size: A4 landscape; margin: 4mm 4mm; background-color: #ffffff; }
            *, *::before, *::after { box-sizing: border-box; }
            body { margin: 0; padding: 0; font-family: 'Helvetica Neue', 'Meiryo', sans-serif; color: #333; }
            .title { font-size: 11pt; font-weight: bold; margin-bottom: 3px; color: #1a237e; }
            table { table-layout: fixed; width: 100%; border-collapse: collapse; background-color: #ffffff; }
            th, td { border: 0.5px solid #cccccc; text-align: center; padding: 0; height: 14.5px; font-size: 7.5pt; }
            .num-cell { width: 20px !important; }
            th { background-color: #f1f3f5; font-weight: bold; color: #495057; height: 16px; font-size: 7.5pt; }
            .loop-col { background-color: #f8f9fa; color: #868e96; }
            .main-col { background-color: #ffffff; }
            .border-thick-right { border-right: 1.5pt solid #000000 !important; }
            .hit-main { background-color: #e3f2fd !important; color: #0d47a1 !important; font-weight: bold !important; }
            .hit-bonus { background-color: #fff3e0 !important; color: #e65100 !important; font-weight: bold !important; }
            .label-row { font-weight: bold; background-color: #e9ecef; color: #495057; }
            .predict-row td { height: 15px; background-color: #ffffff; }
            .g-dull { background-color: #dcdcdc !important; }
            .g-hot { border: 1.5pt solid #0091ea !important; color: #0d47a1 !important; font-weight: bold !important; }
            .g-both { background-color: #dcdcdc !important; border: 1.5pt solid #0091ea !important; color: #0d47a1 !important; font-weight: bold !important; }
            .legend-text { font-size: 6.5pt; text-align: center; vertical-align: middle; line-height: 1.1; font-weight: bold; color: #333; }
            .list-num-col { font-size: 7.5pt; font-family: monospace; font-weight: bold; color: #2b2b2b; }
        </style>
        </head>
        <body>
        <div class="title">新・予想ガイド分析出目表（hajime_no_mini_v2）</div>
        <table>
            <colgroup>
                <col style="width: 45px;">
                <col class="num-cell" span="37">
                <col style="width: 110px;">
            </colgroup>
            <thead>
                <tr>
                    <th>回号</th>
                    <th class="loop-col num-cell">29</th><th class="loop-col num-cell">30</th><th class="loop-col num-cell" style="border-right: 1px solid #ced4da;">31</th>
                    <th class="main-col num-cell">1</th><th class="main-col num-cell">2</th><th class="main-col num-cell">3</th><th class="main-col num-cell border-thick-right">4</th>
                    <th class="main-col num-cell">5</th><th class="main-col num-cell">6</th><th class="main-col num-cell">7</th><th class="main-col num-cell">8</th><th class="main-col num-cell">9</th><th class="main-col num-cell">10</th><th class="main-col num-cell">11</th><th class="main-col num-cell">12</th><th class="main-col num-cell border-thick-right">13</th>
                    <th class="main-col num-cell">14</th><th class="main-col num-cell">15</th><th class="main-col num-cell">16</th><th class="main-col num-cell">17</th><th class="main-col num-cell">18</th><th class="main-col num-cell">19</th><th class="main-col num-cell">20</th><th class="main-col num-cell">21</th><th class="main-col num-cell">22</th><th class="main-col num-cell border-thick-right">23</th>
                    <th class="main-col num-cell">24</th><th class="main-col num-cell">25</th><th class="main-col num-cell">26</th><th class="main-col num-cell">27</th><th class="main-col num-cell">28</th><th class="main-col num-cell">29</th><th class="main-col num-cell">30</th><th class="main-col num-cell border-thick-right">31</th>
                    <th class="loop-col num-cell">1</th><th class="loop-col num-cell">2</th><th class="loop-col num-cell" style="border-right: 1px solid #ced4da;">3</th>
                    <th>当選番号</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for _, row in df_analysis.iterrows():
            h_nums = [int(row[f'本数字{i}']) for i in range(1, 6)]
            b_num = int(row['ボーナス'])
            
            html_content += f"<tr><td class='label-row'>{int(row['回号'])}回</td>"
            
            for num in left_loop:
                c = "loop-col num-cell"
                if num in h_nums: c += " hit-main"
                elif num == b_num: c += " hit-bonus"
                html_content += f"<td class='{c}'>{num}</td>"
                
            for num in main_area:
                c = "main-col num-cell"
                if num in h_nums: c += " hit-main"
                elif num == b_num: c += " hit-bonus"
                if num in [4, 13, 23, 31]: c += " border-thick-right"
                html_content += f"<td class='{c}'>{num}</td>"
                
            for num in right_loop:
                c = "loop-col num-cell"
                if num in h_nums: c += " hit-main"
                elif num == b_num: c += " hit-bonus"
                html_content += f"<td class='{c}'>{num}</td>"
                
            formatted_all = " ".join([f"{int(row[f'本数字{i}']):02d}" for i in range(1, 6)]) + f" ({b_num:02d})"
            html_content += f"<td class='list-num-col'>{formatted_all}</td></tr>"
            
        for i in range(1, 4):
            html_content += f"<tr class='predict-row'><td class='label-row'>予想{i}</td>"
            for num in left_loop: html_content += "<td class='loop-col num-cell'></td>"
            for num in main_area:
                c = "main-col num-cell"
                if num in [4, 13, 23, 31]: c += " border-thick-right"
                html_content += f"<td class='{c}'></td>"
            for num in right_loop: html_content += "<td class='loop-col num-cell'></td>"
            html_content += "<td></td></tr>"
            
        html_content += "<tr><td class='label-row' style='height:18px;'>予想ガイド</td>"
        
        for num in left_loop:
            is_hot = num in hot_zone
            is_dull = num in dull_zone
            c = "loop-col num-cell"
            if is_hot and is_dull: c += " g-both"
            elif is_hot: c += " g-hot"
            elif is_dull: c += " g-dull"
            html_content += f"<td class='{c}'>{num}</td>"
            
        for num in main_area:
            is_hot = num in hot_zone
            is_dull = num in dull_zone
            c = "main-col num-cell"
            if is_hot and is_dull: c += " g-both"
            elif is_hot: c += " g-hot"
            elif is_dull: c += " g-dull"
            if num in [4, 13, 23, 31]: c += " border-thick-right"
            html_content += f"<td class='{c}'>{num}</td>"
            
        for num in right_loop:
            is_hot = num in hot_zone
            is_dull = num in dull_zone
            c = "loop-col num-cell"
            if is_hot and is_dull: c += " g-both"
            elif is_hot: c += " g-hot"
            elif is_dull: c += " g-dull"
            html_content += f"<td class='{c}'>{num}</td>"
            
        html_content += """<td class="legend-text">■青枠:最新±1<br>■灰色:前々回±3</td></tr></tbody></table></body></html>"""
        
        # PDF生成
        pdf_data = HTML(string=html_content).write_pdf()
        
        st.success("🎉 PDFが正常に作成されました！下のボタンからダウンロードしてください。")
        st.download_button(
            label="📄 出目表PDFをダウンロード",
            data=pdf_data,
            file_name="おれの出目表_最新版.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"エラーが発生しました。CSVの形式を確認してください。: {e}")
