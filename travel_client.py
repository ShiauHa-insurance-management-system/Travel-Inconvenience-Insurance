import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 設定頁面
st.set_page_config(page_title="旅平險投保資料填寫", layout="centered")

# 隱藏選單與側邊欄
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "travel_data.csv"

# 初始化/載入資料函數
def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except:
            pass
    return pd.DataFrame(columns=[
        "投稿時間", "要保人姓名", "要保人身分證", "要保人生日", "通訊地址", 
        "手機號碼", "要保人Email", "旅遊目的地", "出發時間", "回程時間", 
        "繳費方式", "同遊人資訊", "LINE_ID", "處理狀態"
    ])

st.title("✈️ 旅平險投保資料填寫")
st.info("請務必填寫完整資料，系統將自動記錄您的申請時間。")

with st.form("client_form", clear_on_submit=True):
    st.subheader("👤 要保人基本資料")
    c1, c2 = st.columns(2)
    name = c1.text_input("要保人姓名 *")
    id_no = c2.text_input("要保人身分證字號 *")
    
    c3, c4 = st.columns(2)
    bday = c3.date_input("要保人出生年月日 *", value=datetime(1990,1,1), min_value=datetime(1900,1,1))
    phone = c4.text_input("手機號碼 *")
    
    email = st.text_input("要保人 E-mail *")
    address = st.text_input("通訊地址 *")
    
    st.divider()
    st.subheader("🗓️ 旅遊行程與繳費")
    dest = st.text_input("旅遊目的地 *")
    
    c5, c6 = st.columns(2)
    start_t = c5.text_input("出發日期與時間 *", placeholder="2026-05-01 08:30")
    end_t = c6.text_input("回程日期與時間 *", placeholder="2026-05-05 18:00")
    
    pay_method = st.selectbox("繳費方式 *", ["請選擇", "超商繳費單", "刷卡"])
    line_id = st.text_input("業務或您的 LINE ID *")
    
    st.divider()
    st.subheader("👥 同遊人資訊")
    st.caption("若無同遊人請輸入「無」。格式：姓名/身分證/生日 (每位一行)")
    fellows = st.text_area("同遊人名單 *", height=150)
    
    submit_btn = st.form_submit_button("✅ 確認送出資料")

# 點擊送出後的「嚴格檢查」邏輯
if submit_btn:
    # 檢查是否有任何欄位為空值或未選擇
    if not all([name, id_no, phone, email, address, dest, start_t, end_t, fellows, line_id]) or pay_method == "請選擇":
        st.error("⚠️ 資料未填寫完整！請檢查所有帶有 * 的欄位（含同遊人，若無請填『無』）。")
    else:
        # 準備新資料
        new_row = pd.DataFrame([{
            "投稿時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "要保人姓名": name,
            "要保人身分證": id_no,
            "要保人生日": str(bday),
            "通訊地址": address,
            "手機號碼": phone,
            "要保人Email": email,
            "旅遊目的地": dest,
            "出發時間": start_t,
            "回程時間": end_t,
            "繳費方式": pay_method,
            "同遊人資訊": fellows,
            "LINE_ID": line_id,
            "處理狀態": "未處理"
        }])
        
        # 強制讀取並合併
        current_df = load_data()
        updated_df = pd.concat([current_df, new_row], ignore_index=True)
        
        # 存檔並確認
        updated_df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
        st.success(f"🎉 送出成功！投稿時間：{datetime.now().strftime('%H:%M:%S')}")
        st.balloons()