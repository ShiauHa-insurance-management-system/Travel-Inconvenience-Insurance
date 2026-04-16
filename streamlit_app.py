import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# --- 1. 系統設定與視覺優化 ---
st.set_page_config(page_title="旅平險投保資料收件系統", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 3rem; }
    .stDownloadButton>button { 
        width: 100%; border-radius: 10px; font-weight: bold; 
        background-color: #0d47a1; color: white; border: none;
    }
    .stDownloadButton>button:hover { background-color: #1565c0; color: white; }
    .client-header { color: #1565c0; font-weight: 800; padding-bottom: 10px; }
    .status-badge { padding: 5px 10px; border-radius: 5px; color: white; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "travel_data.csv"

# 載入資料函數
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=[
        "投稿時間", "要保人姓名", "要保人身分證", "要保人生日", "通訊地址", 
        "手機號碼", "旅遊目的地", "出發時間", "回程時間", "繳費方式", 
        "同遊人資訊", "LINE_ID", "處理狀態"
    ])

# --- 2. 側邊欄切換 (前後台隔離) ---
with st.sidebar:
    st.title("🛡️ 權限控制")
    mode = st.radio("前往介面：", ["📝 客戶填寫前台", "📊 業務管理後台"])
    st.divider()
    
    if mode == "業務管理後台":
        if "auth_admin" not in st.session_state: st.session_state.auth_admin = False
        if not st.session_state.auth_admin:
            pwd = st.text_input("輸入後台密碼", type="password")
            if st.button("驗證進入"):
                if pwd == "085799": 
                    st.session_state.auth_admin = True
                    st.rerun()
                else: st.error("密碼錯誤")
        else:
            if st.button("🔓 安全登出"):
                st.session_state.auth_admin = False
                st.rerun()
            st.divider()
            # 備份功能
            st.subheader("📥 資料備份中心")
            df_all = load_data()
            if not df_all.empty:
                # 使用 utf-8-sig 確保 Excel 開啟不亂碼
                csv_data = df_all.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="💾 下載全系統 CSV 備份",
                    data=csv_data,
                    file_name=f"travel_insurance_backup_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

# --- 3. 【前台】客戶填寫介面 ---
if mode == "📝 客戶填寫前台":
    st.markdown("<h1 class='client-header'>✈️ 旅平險投保資料填寫</h1>", unsafe_allow_html=True)
    st.info("您好，請填寫以下投保資訊，系統將自動加密傳送給您的業務人員。")
    
    with st.form("travel_form", clear_on_submit=True):
        st.subheader("📋 要保人基本資料")
        c1, c2 = st.columns(2)
        name = c1.text_input("要保人姓名（必填）")
        id_no = c2.text_input("要保人身分證字號（必填）")
        
        c3, c4 = st.columns(2)
        # 萬年曆生日選擇
        bday = c3.date_input("要保人出生年月日", value=datetime(1990,1,1), min_value=datetime(1900,1,1))
        phone = c4.text_input("手機號碼（必填）")
        
        address = st.text_input("通訊地址")
        
        st.divider()
        st.subheader("🗓️ 旅遊行程與繳費")
        dest = st.text_input("旅遊目的地")
        
        c5, c6 = st.columns(2)
        start_t = c5.text_input("出發日期與時間", placeholder="例：2026-05-01 08:30")
        end_t = c6.text_input("回程日期與時間", placeholder="例：2026-05-05 18:00")
        
        pay_method = st.selectbox("繳費方式", ["請選擇", "超商繳費單", "刷卡"])
        line_id = st.text_input("您的 LINE ID (方便核保連繫)")
        
        st.divider()
        st.subheader("👥 同遊人資訊")
        st.caption("若有多位同遊人，請每位一行輸入：姓名/身分證/生日 (上限 1000 筆)")
        fellow_info = st.text_area("同遊人名單", height=200, placeholder="範例：\n王大同/A123456789/1985-01-01\n李小美/B223344556/1992-10-10")
        
        if st.form_submit_button("✅ 確認送出資料"):
            if name and id_no and phone:
                new_row = pd.DataFrame([{
                    "投稿時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "要保人姓名": name,
                    "要保人身分證": id_no,
                    "要保人生日": str(bday),
                    "通訊地址": address,
                    "手機號碼": phone,
                    "旅遊目的地": dest,
                    "出發時間": start_t,
                    "回程時間": end_t,
                    "繳費方式": pay_method,
                    "同遊人資訊": fellow_info,
                    "LINE_ID": line_id,
                    "處理狀態": "未處理"
                }])
                df = load_data()
                pd.concat([df, new_row], ignore_index=True).to_csv(DB_FILE, index=False)
                st.success("🎉 送出成功！資料已安全加密傳送給業務端。")
            else:
                st.error("❌ 請填寫必填欄位：姓名、身分證、手機號碼。")

# --- 4. 【後台】業務管理介面 ---
elif mode == "📊 業務管理後台":
    if st.session_state.get("auth_admin"):
        st.title("👨‍💻 投保收件管理中心")
        df_admin = load_data()
        
        if df_admin.empty:
            st.info("目前尚無新進資料。")
        else:
            # 依據投稿時間排序，最新在上面
            df_admin = df_admin.iloc[::-1]
            
            for idx, row in df_admin.iterrows():
                # 狀態標籤顏色
                status = row['處理狀態']
                header_text = f"【{status}】{row['要保人姓名']} - {row['旅遊目的地']}"
                
                with st.expander(header_text):
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.write(f"**投稿時間：** {row['投稿時間']}")
                        st.write(f"**身分證：** `{row['要保人身分證']}`")
                        st.write(f"**生日：** {row['要保人生日']}")
                        st.write(f"**手機：** {row['手機號碼']}")
                        st.write(f"**LINE ID：** {row['LINE_ID']}")
                    with col_info2:
                        st.write(f"**地址：** {row['通訊地址']}")
                        st.write(f"**行程：** {row['出發時間']} 至 {row['回程時間']}")
                        st.write(f"**方式：** {row['繳費方式']}")
                    
                    st.divider()
                    st.text_area("同遊人名單 (可複製)", row['同遊人資訊'], height=150, key=f"f_{idx}")
                    
                    st.divider()
                    # 處理狀態控制
                    new_status = st.select_slider(
                        f"變更處理進度 (ID:{idx})",
                        options=["未處理", "已讀資料處理中", "已處理"],
                        value=status,
                        key=f"s_{idx}"
                    )
                    
                    c_btn1, c_btn2 = st.columns([1, 4])
                    if c_btn1.button("💾 儲存進度", key=f"sv_{idx}"):
                        full_df = load_data()
                        full_df.at[idx, '處理狀態'] = new_status
                        full_df.to_csv(DB_FILE, index=False)
                        st.rerun()
                    
                    if c_btn2.button("🗑️ 刪除此筆記錄", key=f"dl_{idx}"):
                        full_df = load_data()
                        full_df.drop(idx).to_csv(DB_FILE, index=False)
                        st.rerun()
    else:
        st.warning("請先在左側選單登入後台。")