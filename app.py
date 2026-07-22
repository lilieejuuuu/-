from datetime import date, timedelta
import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="每日稼動率與料金歷史比對系統", page_icon="📊", layout="wide")

st.title("📊 每日稼動率與料金歷史比對系統")
st.caption("支援批次貼上整月稼動率，自動比對「今日更新」與「昨日更新」之料金差異。")

st.write("---")

# --- 1. 計算淡旺季與料金的函式 ---
def calculate_price(target_date, util):
    month = target_date.month
    day = target_date.day
    
    # 淡季判斷
    is_low_season = False
    if month in [1, 2, 6, 9]:
        is_low_season = True
    elif month == 7 and 1 <= day <= 10:
        is_low_season = True
    elif month == 8 and 20 <= day <= 31:
        is_low_season = True
    elif month == 12 and 1 <= day <= 15:
        is_low_season = True
        
    # 計算料金
    if is_low_season:
        if util <= 30: return 11000
        elif util <= 50: return 12000
        elif util <= 60: return 12500
        elif util <= 70: return 14110
        else: return 16000
    else:
        if util <= 30: return 12500
        elif util <= 50: return 13500
        elif util <= 60: return 14000
        elif util <= 75: return 14250
        elif util <= 85: return 14525
        else: return 17500

# --- 2. 輸入設定區 ---
st.subheader("📝 1. 輸入今日更新設定")

col1, col2, col3 = st.columns(3)

with col1:
    update_date_str = st.text_input("今日更新日 (例如: 7/21)", value=f"{date.today().month}/{date.today().day}")

with col2:
    start_date = st.date_input("本批資料的第 1 天日期 (例如: 2026/7/1)", value=date(2026, 7, 1))

with col3:
    st.write(" ") # 留空對齊

# 文字貼上區
pasted_text = st.text_area(
    "請複製並貼上 Staysee 該列數據 (1號~31號的數字串)：",
    placeholder="例如: 21.6 43.1 44.3 52.7 71.3 82 33.5 23.4 50.9 91.6 ...",
    height=120
)

# 上傳 yesterday 紀錄檔 (選填，比對用)
st.write("---")
st.subheader("📂 2. 上傳昨日的歷史紀錄 (比對用)")
uploaded_history = st.file_uploader("若要比對與昨天的差異，請上傳昨天匯出的 CSV 紀錄檔：", type=["csv"])

# 處理昨日資料數據庫
yesterday_dict = {} # key: 'YYYY-MM-DD', value: price
if uploaded_history is not None:
    try:
        y_df = pd.read_csv(uploaded_history)
        # 建立歷史價格對照表 (取最近一次記錄)
        for idx, row in y_df.iterrows():
            d_str = str(row['日期']).strip()
            p_val = int(row['區間金額'])
            yesterday_dict[d_str] = p_val
        st.success(f"✅ 成功載入昨日歷史資料，共 {len(yesterday_dict)} 筆！")
    except Exception as e:
        st.error(f"昨日紀錄讀取失敗: {e}")

# --- 3. 處理與計算今日數據 ---
if pasted_text.strip():
    # 正規化解析出所有浮點數
    raw_numbers = re.findall(r"\d+\.?\d*", pasted_text)
    
    if raw_numbers:
        table_data = []
        
        for i, num_str in enumerate(raw_numbers):
            try:
                util_val = float(num_str)
                # 自動累加日期
                current_date = start_date + timedelta(days=i)
                date_str = current_date.strftime("%Y/%n/%d").replace("/0", "/") # 格式化如 2026/7/1
                date_iso = current_date.strftime("%Y-%m-%d")
                
                # 計算今日金額
                today_price = calculate_price(current_date, util_val)
                
                # 比對昨日金額
                diff_note = ""
                yesterday_price = yesterday_dict.get(date_str) or yesterday_dict.get(date_iso)
                
                if yesterday_price is not None:
                    if today_price != yesterday_price:
                        diff_note = f"🔥 變動！原為 {yesterday_price}"
                
                table_data.append({
                    "更新日": update_date_str,
                    "日期": date_str,
                    "稼動率": util_val,
                    "區間金額": today_price,
                    "變動提醒": diff_note
                })
            except ValueError:
                continue
        
        # 轉換成 Pandas DataFrame 呈現
        res_df = pd.DataFrame(table_data)
        
        st.write("---")
        st.subheader("📋 3. 今日產生之對照表")
        
        # 顯示整張大表格
        st.dataframe(
            res_df,
            use_container_width=True,
            column_config={
                "區間金額": st.column_config.NumberColumn("區間金額", format="%d円"),
                "稼動率": st.column_config.NumberColumn("稼動率", format="%.1f%%"),
            },
            hide_index=True
        )
        
        # 提供下載 CSV 按鈕 (供明天上傳比對)
        csv_data = res_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="💾 下載今日報表 CSV (請保存此檔案，供明日比對上傳)",
            data=csv_data,
            file_name=f"料金紀錄_{update_date_str.replace('/', '_')}.csv",
            mime="text/csv"
        )
