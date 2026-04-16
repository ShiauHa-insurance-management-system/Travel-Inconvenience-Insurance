import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

tw_tz = timezone(timedelta(hours=8))
st.set_page_config(page_title="業務管理後台", layout="wide")

# 指向根目錄的同一個資料庫
DB_FILE = "travel_data.csv"

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 管理後台登入")
    pwd = st.text_input("請輸入密碼", type="password")
    if st.button("登入"):
        if pwd == "085799":
            st.session_state.auth = True
            st.rerun()
        else: st.error("密碼錯誤")
else:
    st.title("👨‍💻 投保收件管理")
    if st.sidebar.button("🔓 安全登出"):
        st.session_state.auth = False
        st.rerun()
    if st.sidebar.button("🔄 刷新名單"):
        st.rerun()

    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if not df.empty:
            st.sidebar.download_button("📥 備份 CSV", df.to_csv(index=False).encode('utf-8-sig'), "backup.csv", "text/csv")
            for idx, row in df.iloc[::-1].iterrows():
                with st.expander(f"【{row['處理狀態']}】{row['要保人姓名']} ({row['投稿時間']})"):
                    st.write(f"身分證：`{row['要保人身分證']}` | 手機：{row['手機號碼']}")
                    st.text_area("同遊人名單", str(row['同遊人資訊']), key=f"f_{idx}")
                    new_s = st.radio("變更狀態", ["未處理", "已讀處理中", "已處理"], index=["未處理", "已讀處理中", "已處理"].index(row['處理狀態']), key=f"s_{idx}", horizontal=True)
                    if st.button("💾 儲存修改", key=f"sv_{idx}"):
                        current_df = pd.read_csv(DB_FILE)
                        current_df.at[idx, '處理狀態'] = new_s
                        current_df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                        st.rerun()
    else:
        st.warning("目前無資料。")