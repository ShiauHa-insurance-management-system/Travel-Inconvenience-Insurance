import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

# 台灣時區設定 (解決時間不對的問題)
tw_tz = timezone(timedelta(hours=8))

st.set_page_config(page_title="旅平險投保資料填寫", layout="centered")

# 隱藏側邊選單，讓客戶看不到後台
st.markdown("<style>[data-testid='stSidebar'] {display: none;} #MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

DB_FILE = "travel_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["投稿時間", "要保人姓名", "要保人身分證", "要保人生日", "通訊地址", "手機號碼", "要保人Email", "旅遊目的地", "出發時間", "回程時間", "繳費方式", "同遊人資訊", "LINE_ID", "處理狀態"])

st.title("✈️ 旅平險投保資料填寫")
st.info(f"🇹🇼 台灣目前時間：{datetime.now(tw_tz).strftime('%Y-%m-%d %H:%M')}")

with st.form("client_form", clear_on_submit=True):
    st.subheader("👤 要保人基本資料")
    name = st.text_input("要保人姓名 *")
    id_no = st.text_input("要保人身分證字號 *")
    bday_val = st.date_input("要保人出生年月日 *", value=datetime(1990,1,1))
    phone = st.text_input("手機號碼 *")
    email = st.text_input("要保人 E-mail *")
    address = st.text_input("通訊地址 *")
    
    st.divider()
    st.subheader("🗓️ 旅遊行程與繳費")
    dest = st.text_input("旅遊目的地 *")
    start_t = st.text_input("出發日期與時間 * (例: 05/01 08:30)")
    end_t = st.text_input("回程日期與時間 * (例: 05/05 18:00)")
    pay_method = st.selectbox("繳費方式 *", ["請選擇", "超商繳費單", "刷卡"])
    line_id = st.text_input("業務或您的 LINE ID *")
    
    st.divider()
    st.subheader("👥 同遊人資訊")
    st.caption("若無請填『無』。格式：姓名/身分證/生日 (可填寫至 1000 筆)")
    fellows = st.text_area("同遊人名單 *", height=200)
    
    submit_btn = st.form_submit_button("✅ 確認送出資料")

if submit_btn:
    # --- 欄位防漏填檢查邏輯 ---
    if not all([name, id_no, phone, email, address, dest, start_t, end_t, fellows, line_id]) or pay_method == "請選擇":
        st.error("⚠️ 資料未填寫完整！請檢查所有帶有 * 的欄位。")
    else:
        now_tw = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame([{
            "投稿時間": now_tw, "要保人姓名": name, "要保人身分證": id_no, "要保人生日": str(bday_val),
            "通訊地址": address, "手機號碼": phone, "要保人Email": email, "旅遊目的地": dest,
            "出發時間": start_t, "回程時間": end_t, "繳費方式": pay_method,
            "同遊人資訊": fellows, "LINE_ID": line_id, "處理狀態": "未處理"
        }])
        df = load_data()
        pd.concat([df, new_row], ignore_index=True).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
        st.success(f"🎉 送出成功！投稿時間：{now_tw}")
        st.balloons()