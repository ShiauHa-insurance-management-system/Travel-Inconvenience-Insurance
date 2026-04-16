import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

# 1. 台灣時區設定 (確保時間絕對準確)
tw_tz = timezone(timedelta(hours=8))
st.set_page_config(page_title="旅平險投保系統", layout="centered")

DB_FILE = "travel_data.csv"

# 初始化資料庫函數
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=[
        "投稿時間", "要保人姓名", "要保人身分證", "要保人生日", "通訊地址", 
        "手機號碼", "要保人Email", "旅遊目的地", "出發時間", "回程時間", 
        "繳費方式", "同遊人資訊", "LINE_ID", "處理狀態"
    ])

# --- 側邊欄：分頁控制 ---
with st.sidebar:
    st.title("🛡️ 系統選單")
    mode = st.radio("切換頁面：", ["📝 客戶投保填寫", "📊 業務管理後台"])
    st.divider()
    if mode == "📊 業務管理後台":
        pwd = st.text_input("輸入管理密碼", type="password")
        if pwd != "085799":
            st.warning("請輸入正確密碼以進入後台。")
            st.stop() # 阻斷後台顯示

# --- 【前台介面】 ---
if mode == "📝 客戶投保填寫":
    st.title("✈️ 旅平險投保資料填寫")
    # 自動抓取現在時間，僅顯示給客人看，不能修改
    now_time = datetime.now(tw_tz).strftime('%Y-%m-%d %H:%M:%S')
    st.info(f"📋 系統自動記錄投稿時間：{now_time}")

    with st.form("client_form", clear_on_submit=True):
        st.subheader("👤 要保人基本資料")
        c1, c2 = st.columns(2)
        u_name = c1.text_input("要保人姓名 *")
        u_id = c2.text_input("要保人身分證字號 *")
        
        c3, c4 = st.columns(2)
        u_bday = c3.date_input("要保人出生年月日 *", value=datetime(1990,1,1), min_value=datetime(1900,1,1))
        u_phone = c4.text_input("要保人手機號碼 *")
        
        u_email = st.text_input("要保人 E-mail *")
        u_addr = st.text_input("要保人通訊地址 *")
        
        st.divider()
        st.subheader("🗓️ 旅遊行程與繳費")
        u_dest = st.text_input("旅遊目的地 *")
        
        c5, c6 = st.columns(2)
        u_start = c5.text_input("出發日期與時間 *", placeholder="例：2026-05-01 09:00")
        u_end = c6.text_input("回程日期與時間 *", placeholder="例：2026-05-05 18:00")
        
        u_pay = st.selectbox("繳費方式 *", ["請選擇", "超商繳費單", "刷卡"])
        u_line = st.text_input("業務或您的 LINE ID *")
        
        st.divider()
        st.subheader("👥 同遊人資訊")
        st.caption("請輸入姓名、身分證、生日。若無同遊人請填「無」。")
        u_fellows = st.text_area("同遊人名單 (支援 1000 筆資料錄入) *", height=200, placeholder="格式範例：\n王小明/A123456789/1995-01-01\n李小華/B987654321/1998-05-20")
        
        submit_btn = st.form_submit_button("✅ 確認送出資料")

    # --- 關鍵：漏填檢查邏輯 ---
    if submit_btn:
        # 檢查所有必填欄位
        check_list = [u_name, u_id, u_phone, u_email, u_addr, u_dest, u_start, u_end, u_fellows, u_line]
        
        if not all(check_list) or u_pay == "請選擇":
            st.error("⚠️ 傳送失敗！所有帶有 * 的欄位都必須填寫完整，請檢查是否有遺漏。")
        else:
            # 儲存資料
            new_row = pd.DataFrame([{
                "投稿時間": now_time, # 使用系統自動抓取的時間
                "要保人姓名": u_name,
                "要保人身分證": u_id,
                "要保人生日": str(u_bday),
                "通訊地址": u_addr,
                "手機號碼": u_phone,
                "要保人Email": u_email,
                "旅遊目的地": u_dest,
                "出發時間": u_start,
                "回程時間": u_end,
                "繳費方式": u_pay,
                "同遊人資訊": u_fellows,
                "LINE_ID": u_line,
                "處理狀態": "未處理"
            }])
            df = load_data()
            pd.concat([df, new_row], ignore_index=True).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.success(f"🎉 提交成功！我們已收到您的投保申請。")
            st.balloons()

# --- 【後台介面】 ---
elif mode == "📊 業務管理後台":
    st.title("👨‍💻 投保案件管理中心")
    if st.button("🔄 刷新名單"):
        st.rerun()

    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if df.empty:
            st.info("目前尚未有客戶提交資料。")
        else:
            st.sidebar.download_button("📥 下載 Excel/CSV 備份", df.to_csv(index=False).encode('utf-8-sig'), f"backup_{datetime.now(tw_tz).strftime('%m%d')}.csv")
            
            # 從最新的顯示到最舊的
            for idx, row in df.iloc[::-1].iterrows():
                with st.expander(f"【{row['處理狀態']}】{row['要保人姓名']} - {row['旅遊目的地']} ({row['投稿時間']})"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**身分證：** `{row['要保人身分證']}`")
                        st.write(f"**生日：** {row['要保人生日']}")
                        st.write(f"**手機：** {row['手機號碼']}")
                        st.write(f"**Email：** {row['要保人Email']}")
                    with c2:
                        st.write(f"**地址：** {row['通訊地址']}")
                        st.write(f"**LINE ID：** {row['LINE_ID']}")
                        st.write(f"**行程：** {row['出發時間']} ~ {row['回程時間']}")
                        st.write(f"**繳費：** {row['繳費方式']}")
                    
                    st.text_area("👥 同遊人清單內容", str(row['同遊人資訊']), height=100, key=f"f_{idx}")
                    
                    new_s = st.radio("更新進度", ["未處理", "處理中", "已結案"], 
                                     index=["未處理", "處理中", "已結案"].index(row['處理狀態']), key=f"s_{idx}", horizontal=True)
                    
                    b1, b2 = st.columns([1, 4])
                    if b1.button("💾 儲存修改", key=f"sv_{idx}"):
                        current_df = pd.read_csv(DB_FILE)
                        current_df.at[idx, '處理狀態'] = new_s
                        current_df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                        st.success("更新成功！")
                        st.rerun()
                    if b2.button("🗑️ 刪除案件", key=f"dl_{idx}"):
                        current_df = pd.read_csv(DB_FILE)
                        current_df.drop(idx).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                        st.rerun()
    else:
        st.warning("資料庫檔案尚未建立（需先有客戶送出第一份資料）。")