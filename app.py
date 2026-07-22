from datetime import date
import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Staysee 稼動率與料金判定系統", page_icon="🏭", layout="centered")

st.title("🏭 Staysee 稼動率與料金判定系統")
st.caption("支援「複製貼上 Staysee 文字」或「手動輸入」，自動對照料金與比對昨日價格。")

st.write("---")

# --- 1. 直接複製貼上區塊 ---
st.subheader("📋 步驟 1：貼上 Staysee 數據（可選）")
pasted_text = st.text_area(
    "請直接從 Staysee 畫面複製「合計」那一列文字並貼在此處：",
    placeholder="例：合計 73.3 90.2 71.8 80.8 62.1 ...",
    height=100
)

parsed_utilization = None

if pasted_text.strip():
    # 使用正規表達式找出所有數字 (包含小數)
    numbers = re.findall(r"\d+\.?\d*", pasted_text)
    if numbers:
        st.success(f"✅ 成功從貼上內容中解析出 {len(numbers)} 個數據！")
    else:
        st.warning("⚠️ 貼上的文字中未找到有效數字，請重新複製。")

# --- 2. 日期與稼動率設定 ---
st.write("---")
st.subheader("📅 步驟 2：設定日期與比對資料")

col1, col2 = st.columns(2)

with col1:
    target_date = st.date_input("選擇要查詢/設定的「目標日期」", value=date.today())

# 若有貼上數據，嘗試根據日期 (day) 自動帶入對應位置的數字
default_util = 50.0
if pasted_text.strip() and 'numbers' in locals() and numbers:
    day_num = target_date.day
    # 假設複製出來的數字順序對應 1日~31日
    if day_num <= len(numbers):
        try:
            default_util = float(numbers[day_num - 1])
            st.info(f"💡 已自動擷取 {target_date.month}/{day_num} 日的稼動率為：**{default_util}%**")
        except ValueError:
            pass

with col2:
    utilization = st.number_input(
        "當天預估「稼動率 (%)」",
        min_value=0.0,
        max_value=100.0,
        value=default_util,
        step=0.1,
        help="自動帶入貼上數據，亦可在此手動微調"
    )

yesterday_price = st.number_input(
    "輸入昨日更新的同日料金 (日圓, 若無請填 0)",
    min_value=0,
    value=12000,
    step=100
)

# --- 3. 淡旺季判定邏輯 ---
month = target_date.month
day = target_date.day

is_low_season = False

# 淡季判定：1月、2月、6月、9月、7/1~7/10、8/20~8/31、12/1~12/15
if month in [1, 2, 6, 9]:
    is_low_season = True
elif month == 7 and 1 <= day <= 10:
    is_low_season = True
elif month == 8 and 20 <= day <= 31:
    is_low_season = True
elif month == 12 and 1 <= day <= 15:
    is_low_season = True

season_text = "淡季" if is_low_season else "旺季"

# --- 4. 料金區間判斷邏輯 ---
calculated_price = 0
price_display_text = ""

if is_low_season:
    # 淡季料金表
    if utilization <= 30:
        calculated_price = 11000
        price_display_text = "11,000 円"
    elif utilization <= 50:
        calculated_price = 12000
        price_display_text = "12,000 円"
    elif utilization <= 60:
        calculated_price = 12500
        price_display_text = "12,500 円"
    elif utilization <= 70:
        calculated_price = 14110
        price_display_text = "14,110 円"
    else:  # 71% 以上
        calculated_price = 16000
        price_display_text = "16,000 円 以上調整"
else:
    # 旺季料金表
    if utilization <= 30:
        calculated_price = 12500
        price_display_text = "12,500 円"
    elif utilization <= 50:
        calculated_price = 13500
        price_display_text = "13,500 円"
    elif utilization <= 60:
        calculated_price = 14000
        price_display_text = "14,000 円"
    elif utilization <= 75:
        calculated_price = 14250
        price_display_text = "14,250 円"
    elif utilization <= 85:
        calculated_price = 14525
        price_display_text = "14,525 円"
    else:  # 85% 以上
        calculated_price = 17500
        price_display_text = "17,500 円 以上調整"

# --- 5. 結果呈現區塊 ---
st.write("---")
st.subheader("📊 步驟 3：試算與比對結果")

# 顯示淡旺季標籤
if is_low_season:
    st.info(f"🗓️ **目標日期：** {target_date}（判定為：**淡季**）")
else:
    st.error(f"🔥 **目標日期：** {target_date}（判定為：**旺季**）")

# 顯示今日算出的料金
st.metric(label="今日對應料金", value=price_display_text)

# --- 6. 異動提醒邏輯 ---
if yesterday_price > 0:
    if calculated_price != yesterday_price:
        st.warning(f"⚠️ **料金有變動，原先料金為 \"{yesterday_price:,}円\"**")
    else:
        # 價格沒變動保持空白
        pass
