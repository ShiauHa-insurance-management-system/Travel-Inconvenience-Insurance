import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="旅平險管理後台", layout="wide")

DB_FILE = "travel_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame()

# 登入邏輯
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 業務管理後台登入")
    pwd = st.text_input("請輸入密碼", type="password")
    if st.button("登入"):
        if pwd == "085799":
            st.session_state.auth = True
            st.rerun()
        else: st.error("密碼錯誤")
else:
    # 側邊欄控制
    with st.sidebar:
        st.title("⚙️ 管理選單")
        if st.button("安全登出"):
            st.session_state.auth = False
            st.rerun()
        st.divider()
        # 備份按鍵
        df_all = load_data()
        if not df_all.empty:
            csv = df_all.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 下載全系統資料備份", csv, "backup.csv", "text/csv")

    st.title("👨‍💻 投保收件名單")
    df = load_data()
    if df.empty:
        st.info("目前尚無資料。")
    else:
        for idx, row in df.iloc[::-1].iterrows():
            with st.expander(f"【{row['處理狀態']}】{row['要保人姓名']} - {row['旅遊目的地']}"):
                st.write(f"**時間：** {row['投稿時間']} | **LINE：** {row['LINE_ID']}")
                st.write(f"**身分證/生日：** `{row['要保人身分證']}` / {row['要保人生日']}")
                st.write(f"**手機/行程：** {row['手機號碼']} / {row['出發時間']} ~ {row['回程時間']}")
                st.info(f"**同遊人：**\n\n{row['同遊人資訊']}")
                
                # 狀態與操作
                new_s = st.selectbox(f"處理進度", ["未處理", "已讀資料處理中", "已處理"], index=["未處理", "已讀資料處理中", "已處理"].index(row['處理狀態']), key=f"s_{idx}")
                c1, c2 = st.columns([1, 4])
                if c1.button("儲存", key=f"v_{idx}"):
                    df.at[idx, '處理狀態'] = new_s
                    df.to_csv(DB_FILE, index=False)
                    st.rerun()
                if c2.button("刪除", key=f"d_{idx}"):
                    df.drop(idx).to_csv(DB_FILE, index=False)
                    st.rerun()