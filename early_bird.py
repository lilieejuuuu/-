import pandas as pd
import streamlit as st

st.set_page_config(page_title="早鳥比例調整計算機", page_icon="🧮", layout="wide")

st.title("🧮 早鳥價格比例調整計算機")
st.write("輸入早鳥原價與變動後的常態價格，自動算出建議下調的比例 % 數。")

st.write("---")

# --- 1. 設定早鳥原價與方案 ---
col1, col2 = st.columns(2)

with col1:
    early_bird_orig = st.number_input("早鳥原價 (円)：", value=13300, step=100)

with col2:
    eb_scheme = st.selectbox(
        "選擇早鳥方案：",
        ["早鳥 30 天 (便宜 5%)", "早鳥 60 天 (便宜 10%)", "早鳥 90 天 (便宜 15%)"]
    )

# 折扣率映射
discount_map = {
    "早鳥 30 天 (便宜 5%)": 0.95,
    "早鳥 60 天 (便宜 10%)": 0.90,
    "早鳥 90 天 (便宜 15%)": 0.85
}
current_discount = discount_map[eb_scheme]

st.write("---")

# --- 2. 輸入變動後的常態價格 ---
st.subheader("📊 輸入變動後的常態價格")
normal_prices_input = st.text_input(
    "請輸入或貼上最新常態價格 (可以貼單個或多個數字，用空格隔開，例如: 12000 13500 14000)：",
    value="12000"
)

# --- 3. 運算與輸出表格 ---
if normal_prices_input.strip():
    # 提取所有數字
    prices = [float(p) for p in normal_prices_input.replace(",", "").split() if p.replace(".", "", 1).isdigit()]
    
    results = []
    for p in prices:
        target_eb_price = p * current_discount
        if early_bird_orig > 0:
            adj_ratio = ((target_eb_price - early_bird_orig) / early_bird_orig) * 100
        else:
            adj_ratio = 0.0
            
        results.append({
            "早鳥原價": early_bird_orig,
            "常態價格": int(p),
            "目標早鳥價": int(target_eb_price),
            "比例調整": f"{adj_ratio:+.2f}%"
        })
    
    if results:
        st.write("---")
        st.subheader("📋 計算結果")
        res_df = pd.DataFrame(results)
        st.dataframe(
            res_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "早鳥原價": st.column_config.NumberColumn("早鳥原價", format="%d円"),
                "常態價格": st.column_config.NumberColumn("常態價格", format="%d円"),
                "目標早鳥價": st.column_config.NumberColumn("目標早鳥價", format="%d円"),
                "比例調整": st.column_config.TextColumn("比例調整")
            }
        )
