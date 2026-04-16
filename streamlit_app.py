import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

# 1. 台灣時區設定 (確保投稿時間正確)
tw_tz = timezone(timedelta(hours=8))
st.set_page_config(page_title="旅平險系統", layout="centered")

DB_FILE = "travel_data.csv"

# 初始化資料庫函數
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["投稿時間", "姓名", "身分證", "生日", "地址", "手機", "Email", "目的地", "出發", "回程", "繳費", "同遊人", "LINE_ID", "狀態"])

# --- 側邊欄：權限控制 ---
with st.sidebar:
    st.title("🛡️ 權限控制")
    mode = st.radio("前往介面：", ["📝 客戶填寫前台", "📊 業務管理後台"])
    st.divider()
    if mode == "📊 業務管理後台":
        pwd = st.text_input("輸入管理密碼", type="password")
        if pwd != "085799":
            st.warning("請先在左側選單登入後台。")
            st.stop() # 密碼不對就停在這裡，不顯示後台內容

# --- 前台介面 ---
if mode == "📝 客戶填寫前台":
    st.title("✈️ 旅平險投保資料填寫")
    st.info(f"🇹🇼 台灣目前時間：{datetime.now(tw_tz).strftime('%Y-%m-%d %H:%M:%S')}")

    with st.form("client_form", clear_on_submit=True):
        st.subheader("👤 基本資料")
        c1, c2 = st.columns(2)
        name = c1.text_input("姓名 *")
        id_no = c2.text_input("身分證字號 *")
        bday = st.date_input("出生年月日 *", value=datetime(1990,1,1))
        addr = st.text_input("通訊地址 *")
        phone = st.text_input("手機號碼 *")
        email = st.text_input("E-mail *")
        
        st.divider()
        st.subheader("🗓️ 旅遊行程")
        dest = st.text_input("目的地 *")
        t1 = st.text_input("出發時間 * (例: 05/01 09:00)")
        t2 = st.text_input("回程時間 * (例: 05/05 18:00)")
        pay = st.selectbox("繳費方式 *", ["請選擇", "超商繳費單", "刷卡"])
        line = st.text_input("業務或您的 LINE ID *")
        
        st.divider()
        st.subheader("👥 同遊人資訊")
        fellows = st.text_area("格式：姓名/身分證/生日 *", height=150)
        
        submit = st.form_submit_button("✅ 確認送出資料")

    if submit:
        if not all([name, id_no, addr, phone, email, dest, t1, t2, line, fellows]) or pay == "請選擇":
            st.error("⚠️ 資料未填寫完整！")
        else:
            now_str = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")
            new_row = pd.DataFrame([{
                "投稿時間": now_str, "姓名": name, "身分證": id_no, "生日": str(bday),
                "地址": addr, "手機": phone, "Email": email, "目的地": dest,
                "出發": t1, "回程": t2, "繳費": pay, "同遊人": fellows, "LINE_ID": line, "狀態": "未處理"
            }])
            df = load_data()
            pd.concat([df, new_row], ignore_index=True).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.success(f"🎉 提交成功！時間：{now_str}")

# --- 後台介面 ---
elif mode == "📊 業務管理後台":
    st.title("👨‍💻 投保收件管理中心")
    if st.button("🔄 立即刷新名單"):
        st.rerun()

    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if df.empty:
            st.info("目前資料庫是空的。")
        else:
            st.sidebar.download_button("📥 下載 CSV 備份", df.to_csv(index=False).encode('utf-8-sig'), "backup.csv")
            for idx, row in df.iloc[::-1].iterrows():
                with st.expander(f"【{row['狀態']}】{row['姓名']} - {row['目的地']} ({row['投稿時間']})"):
                    st.write(f"身分證：`{row['身分證']}` | 手機：{row['手機']} | Email：{row['Email']}")
                    st.text_area("同遊人名單", str(row['同遊人']), key=f"f_{idx}")
                    new_s = st.radio("修改狀態", ["未處理", "處理中", "已結案"], index=["未處理", "處理中", "已結案"].index(row['狀態']), key=f"s_{idx}", horizontal=True)
                    if st.button("💾 儲存修改", key=f"btn_{idx}"):
                        current_df = pd.read_csv(DB_FILE)
                        current_df.at[idx, '狀態'] = new_s
                        current_df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                        st.success("更新成功！")
                        st.rerun()
    else:
        st.warning("尚無資料庫檔案。")