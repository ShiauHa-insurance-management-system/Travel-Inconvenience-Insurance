import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 設定頁面
st.set_page_config(page_title="旅平險投保資料填寫", layout="centered")

# 強制隱藏側邊欄與選單，防止客戶亂點
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "travel_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=[
        "投稿時間", "要保人姓名", "要保人身分證", "要保人生日", "通訊地址", 
        "手機號碼", "要保人Email", "旅遊目的地", "出發時間", "回程時間", 
        "繳費方式", "同遊人資訊", "LINE_ID", "處理狀態"
    ])

st.title("✈️ 旅平險投保資料填寫")
st.info("您好，請填寫投保資訊。系統會自動記錄您的申請時間。")

with st.form("client_form", clear_on_submit=True):
    st.subheader("👤 要保人基本資料")
    c1, c2 = st.columns(2)
    name = c1.text_input("要保人姓名（必填）")
    id_no = c2.text_input("要保人身分證字號（必填）")
    
    c3, c4 = st.columns(2)
    bday = c3.date_input("要保人出生年月日", value=datetime(1990,1,1), min_value=datetime(1900,1,1))
    phone = c4.text_input("手機號碼（必填）")
    
    email = st.text_input("要保人 E-mail（必填）")
    address = st.text_input("通訊地址")
    
    st.divider()
    st.subheader("🗓️ 旅遊行程與繳費")
    dest = st.text_input("旅遊目的地")
    
    c5, c6 = st.columns(2)
    start_t = c5.text_input("出發日期與時間", placeholder="例：2026-05-01 08:30")
    end_t = c6.text_input("回程日期與時間", placeholder="例：2026-05-05 18:00")
    
    pay_method = st.selectbox("繳費方式", ["請選擇", "超商繳費單", "刷卡"])
    line_id = st.text_input("業務或您的 LINE ID")
    
    st.divider()
    st.subheader("👥 同遊人資訊")
    st.caption("格式：姓名/身分證/生日 (每位一行，上限 1000 筆)")
    fellows = st.text_area("同遊人名單", height=200, placeholder="範例：\n王大同/A123456789/1985-01-01\n李小美/B223344556/1992-10-10")
    
    if st.form_submit_button("✅ 確認送出資料"):
        if name and id_no and phone and email:
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
            df = load_data()
            pd.concat([df, new_row], ignore_index=True).to_csv(DB_FILE, index=False)
            st.success("🎉 送出成功！業務人員將盡速聯繫您。")
        else:
            st.error("❌ 請填寫姓名、身分證、手機與 Email。")