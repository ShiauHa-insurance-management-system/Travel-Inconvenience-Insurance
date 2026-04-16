import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

# 1. 台灣時區設定
tw_tz = timezone(timedelta(hours=8))

st.set_page_config(page_title="旅平險投保系統", layout="centered")

# 隱藏側邊欄與選單
st.markdown("<style>[data-testid='stSidebar'] {display: none;} #MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

DB_FILE = "travel_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["投稿時間", "姓名", "身分證", "生日", "地址", "手機", "Email", "目的地", "出發", "回程", "繳費", "同遊人", "LINE_ID", "狀態"])

st.title("✈️ 旅平險投保資料填寫")
st.write(f"🇹🇼 目前時間：{datetime.now(tw_tz).strftime('%Y-%m-%d %H:%M')}")

with st.form("my_form", clear_on_submit=True):
    st.subheader("👤 要保人資料")
    c1, c2 = st.columns(2)
    name = c1.text_input("要保人姓名 *")
    id_no = c2.text_input("身分證字號 *")
    bday = st.date_input("出生年月日 *", value=datetime(1990,1,1))
    
    addr = st.text_input("通訊地址 *")
    phone = st.text_input("手機號碼 *")
    email = st.text_input("要保人 E-mail *")
    
    st.divider()
    st.subheader("🗓️ 旅遊行程")
    dest = st.text_input("旅遊目的地 *")
    t1 = st.text_input("出發日期時間 * (例: 05/01 09:00)")
    t2 = st.text_input("回程日期時間 * (例: 05/05 18:00)")
    pay = st.selectbox("繳費方式 *", ["請選擇", "超商繳費單", "刷卡"])
    line = st.text_input("業務或您的 LINE ID *")
    
    st.divider()
    st.subheader("👥 同遊人資訊 (上限1000筆)")
    fellows = st.text_area("格式：姓名/身分證/生日 (若無請填『無』) *", height=150)
    
    submit = st.form_submit_button("✅ 確認送出")

if submit:
    # 嚴格檢查
    if not all([name, id_no, addr, phone, email, dest, t1, t2, line, fellows]) or pay == "請選擇":
        st.error("⚠️ 資料未填寫完整！請檢查所有帶有 * 的欄位。")
    else:
        # 自動捉取時間 (固定的)
        now_str = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")
        new_data = pd.DataFrame([{
            "投稿時間": now_str, "姓名": name, "身分證": id_no, "生日": str(bday),
            "地址": addr, "手機": phone, "Email": email, "目的地": dest,
            "出發": t1, "回程": t2, "繳費": pay, "同遊人": fellows, "LINE_ID": line, "狀態": "未處理"
        }])
        df = load_data()
        pd.concat([df, new_data], ignore_index=True).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
        st.success(f"🎉 提交成功！時間：{now_str}")
        st.balloons()