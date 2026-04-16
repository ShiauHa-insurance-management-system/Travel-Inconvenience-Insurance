import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="後台管理", layout="wide")

DB_FILE = "travel_data.csv"

# 簡單登入機制
if "admin_login" not in st.session_state: st.session_state.admin_login = False

if not st.session_state.admin_login:
    st.title("🔐 管理登入")
    pwd = st.text_input("請輸入密碼", type="password")
    if st.button("登入"):
        if pwd == "085799":
            st.session_state.admin_login = True
            st.rerun()
        else: st.error("密碼錯誤")
else:
    st.title("👨‍💻 投保名單管理")
    if st.button("🔄 刷新名單"): st.rerun()
    if st.button("🔓 安全登出"):
        st.session_state.admin_login = False
        st.rerun()

    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        st.sidebar.download_button("📥 下載備份", df.to_csv(index=False).encode('utf-8-sig'), "backup.csv")
        
        for idx, row in df.iloc[::-1].iterrows():
            with st.expander(f"【{row['狀態']}】{row['姓名']} - {row['目的地']} ({row['投稿時間']})"):
                st.write(f"身分證：`{row['身分證']}` | 手機：{row['手機']} | Email：{row['Email']}")
                st.write(f"行程：{row['出發']} ~ {row['回程']} | 方式：{row['繳費']}")
                st.text_area("同遊人名單", str(row['同遊人']), key=f"f_{idx}")
                
                new_status = st.radio("修改狀態", ["未處理", "處理中", "已結案"], index=["未處理", "處理中", "已結案"].index(row['狀態']), key=f"s_{idx}", horizontal=True)
                if st.button("💾 儲存變更", key=f"save_{idx}"):
                    df.at[idx, '狀態'] = new_status
                    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                    st.success("儲存成功")
                    st.rerun()
    else:
        st.info("目前無資料。")