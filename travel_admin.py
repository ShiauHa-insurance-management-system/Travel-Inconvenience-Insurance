import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="旅平險管理後台", layout="wide")

DB_FILE = "travel_data.csv"

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 業務管理後台登入")
    pwd = st.text_input("請輸入管理密碼", type="password")
    if st.button("登入系統"):
        if pwd == "085799":
            st.session_state.auth = True
            st.rerun()
        else: st.error("密碼錯誤")
else:
    st.title("👨‍💻 投保收件管理中心")
    
    # 側邊欄控制
    with st.sidebar:
        if st.button("🔓 安全登出"):
            st.session_state.auth = False
            st.rerun()
        st.divider()
        if st.button("🔄 立即刷新名單"):
            st.rerun()

    if os.path.exists(DB_FILE):
        # 這裡強制不快取，每次都重讀檔案
        df = pd.read_csv(DB_FILE)
        
        # 備份按鈕
        csv_backup = df.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button("📥 下載全系統 CSV 備份", csv_backup, "travel_backup.csv", "text/csv")
        
        if df.empty:
            st.info("目前尚無客戶填寫資料。")
        else:
            st.subheader(f"目前共有 {len(df)} 筆申請單")
            for idx, row in df.iloc[::-1].iterrows():
                status = row['處理狀態']
                with st.expander(f"【{status}】 客戶：{row['要保人姓名']} - 目的地：{row['旅遊目的地']}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**投稿時間：** {row['投稿時間']}")
                        st.write(f"**身分證：** `{row['要保人身分證']}` | **生日：** {row['要保人生日']}")
                        st.write(f"**Email：** {row['要保人Email']}")
                    with c2:
                        st.write(f"**手機：** {row['手機號碼']} | **LINE：** {row['LINE_ID']}")
                        st.write(f"**行程：** {row['出發時間']} ~ {row['回程時間']}")
                        st.write(f"**繳費：** {row['繳費方式']}")
                    
                    st.text_area("同遊人名單", row['同遊人資訊'], height=100, key=f"f_{idx}")
                    
                    new_s = st.radio("變更狀態", ["未處理", "已讀資料處理中", "已處理"], 
                                     index=["未處理", "已讀資料處理中", "已處理"].index(status),
                                     key=f"s_{idx}", horizontal=True)
                    
                    b1, b2 = st.columns([1, 4])
                    if b1.button("💾 儲存", key=f"sv_{idx}"):
                        current_df = pd.read_csv(DB_FILE)
                        current_df.at[idx, '處理狀態'] = new_s
                        current_df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                        st.rerun()
                    if b2.button("🗑️ 刪除", key=f"dl_{idx}"):
                        current_df = pd.read_csv(DB_FILE)
                        current_df.drop(idx).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                        st.rerun()
    else:
        st.info("資料庫尚未建立（尚無人填寫）。請點擊刷新或等待客戶送件。")