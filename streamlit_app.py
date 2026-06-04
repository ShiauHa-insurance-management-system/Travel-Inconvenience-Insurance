import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

# 1. 台灣時區設定 (確保時間絕對準確)
tw_tz = timezone(timedelta(hours=8))
st.set_page_config(page_title="旅平險投保系統", layout="centered")

DB_FILE = "travel_data.csv"

# 2. 欄位定義 (對齊 9 大被保險人核心資訊 + 系統必要欄位)
CORE_COLUMNS = [
    "投稿時間", 
    "被保險人身分證號(居留證號)", 
    "被保險人姓名", 
    "被保險人出生年月日", 
    "被保險人行動電話", 
    "被保險人國籍", 
    "旅平險保額(萬)", 
    "法定代理人姓名", 
    "法定代理人身份證字號", 
    "法定代理人關係", 
    "旅遊目的地", 
    "出發時間", 
    "回程時間", 
    "繳費方式", 
    "LINE_ID", 
    "處理狀態"
]

# 初始化資料庫函數
def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # 確保讀取時欄位完整，避免舊版本檔案衝突
        for col in CORE_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[CORE_COLUMNS]
    return pd.DataFrame(columns=CORE_COLUMNS)

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
    now_time = datetime.now(tw_tz).strftime('%Y-%m-%d %H:%M:%S')
    st.info(f"📋 系統自動記錄投稿時間：{now_time}")

    with st.form("client_form", clear_on_submit=True):
        st.subheader("👤 被保險人基本資料")
        st.caption("💡 主被保險人請填在第一位，所有被保險人都需在此表內。")
        
        c1, c2 = st.columns(2)
        ins_id = c1.text_input("1. 被保險人身分證號 / 居留證號 *", placeholder="請填寫正確ID，外籍人士請填ARC")
        ins_name = c2.text_input("2. 被保險人姓名 *", placeholder="主被保險人姓名")
        
        c3, c4 = st.columns(2)
        ins_bday = c3.text_input("3. 被保險人出生年月日 *", max_chars=7, placeholder="民國年格式，例：0840520 (7碼文字)")
        ins_phone = c4.text_input("4. 被保險人行動電話 *", max_chars=10, placeholder="10碼文字，例：0912345678")
        
        c5, c6 = st.columns(2)
        ins_nation = c5.text_input("5. 被保險人國籍 *", value="TW", placeholder="如台灣請填寫TW")
        ins_amount = c6.number_input("6. 旅平險保額(萬) *", min_value=0, max_value=1500, value=500, step=50)
        
        st.divider()
        st.subheader("👥 法定代理人資訊 (未滿15歲或有需填寫者填寫)")
        st.caption("💡 若無帳務或法定代理人需求，可填寫「無」或留空（依業務申報習慣）。")
        
        c7, c8 = st.columns(2)
        legal_name = c7.text_input("7. 法定代理人姓名")
        legal_id = c8.text_input("8. 法定代理人身份證字號")
        
        legal_rel = st.selectbox(
            "9. 法定代理人關係 (2碼文字)", 
            ["", "01", "02", "03", "04", "05"],
            format_func=lambda x: {
                "": "請選擇關係碼 (非必填)",
                "01": "01 父子", 
                "02": "02 父女", 
                "03": "03 母子", 
                "04": "04 母女", 
                "05": "05 其他"
            }[x]
        )
        
        st.divider()
        st.subheader("🗓️ 旅遊行程與聯繫管道")
        u_dest = st.text_input("旅遊目的地 *")
        
        c9, c10 = st.columns(2)
        u_start = c9.text_input("出發日期與時間 *", placeholder="例：2026-05-01 09:00")
        u_end = c10.text_input("回程日期與時間 *", placeholder="例：2026-05-05 18:00")
        
        u_pay = st.selectbox("繳費方式 *", ["請選擇", "超商繳費單", "刷卡"])
        u_line = st.text_input("業務或您的 LINE ID *")
        
        submit_btn = st.form_submit_button("✅ 確認送出資料")

    # --- 漏填檢查邏輯 ---
    if submit_btn:
        # 核心必填項查核
        check_list = [ins_id, ins_name, ins_bday, ins_phone, ins_nation, u_dest, u_start, u_end, u_line]
        
        if not all(check_list) or u_pay == "請選擇":
            st.error("⚠️ 傳送失敗！請檢查帶有 * 的必填欄位及繳費方式是否皆填寫完整。")
        elif len(ins_bday) != 7:
            st.error("⚠️ 傳送失敗！『被保險人出生年月日』必須為 7 碼民國年文字（如 0840520）。")
        elif len(ins_phone) != 10:
            st.error("⚠️ 傳送失敗！『被保險人行動電話』必須為 10 碼數字。")
        else:
            # 建立新列資料
            new_row = pd.DataFrame([{
                "投稿時間": now_time,
                "被保險人身分證號(居留證號)": ins_id.strip().upper(), # 自動轉大寫
                "被保險人姓名": ins_name.strip(),
                "被保險人出生年月日": ins_bday.strip(),
                "被保險人行動電話": ins_phone.strip(),
                "被保險人國籍": ins_nation.strip().upper(),
                "旅平險保額(萬)": f"{ins_amount}萬",
                "法定代理人姓名": legal_name.strip() if legal_name else "無",
                "法定代理人身份證字號": legal_id.strip().upper() if legal_id else "無",
                "法定代理人關係": legal_rel if legal_rel else "無",
                "旅遊目的地": u_dest.strip(),
                "出發時間": u_start.strip(),
                "回程時間": u_end.strip(),
                "繳費方式": u_pay,
                "LINE_ID": u_line.strip(),
                "處理狀態": "未處理"
            }])
            
            df = load_data()
            pd.concat([df, new_row], ignore_index=True).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
            st.success("🎉 提交成功！我們已收到您的投保申請。")
            st.balloons()

# --- 【後台介面】 ---
elif mode == "📊 業務管理後台":
    st.title("👨‍💻 投保案件管理中心")
    if st.button("🔄 刷新名單"):
        st.rerun()

    df = load_data()
    if df.empty:
        st.info("目前尚未有客戶提交資料。")
    else:
        # 側邊欄下載按鈕
        st.sidebar.download_button(
            "📥 下載 Excel/CSV 備份", 
            df.to_csv(index=False).encode('utf-8-sig'), 
            f"travel_backup_{datetime.now(tw_tz).strftime('%m%d')}.csv"
        )
        
        # 從最新到最舊排序呈現
        for idx, row in df.iloc[::-1].iterrows():
            with st.expander(f"【{row['處理狀態']}】{row['被保險人姓名']} - {row['旅遊目的地']} ({row['投稿時間']})"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**身分證/居留證：** `{row['被保險人身分證號(居留證號)']}`")
                    st.write(f"**出生年月日(民)：** `{row['被保險人出生年月日']}`")
                    st.write(f"**行動電話：** `{row['被保險人行動電話']}`")
                    st.write(f"**國籍：** `{row['被保險人國籍']}`")
                    st.write(f"**旅平險保額：** {row['旅平險保額(萬)']}")
                with c2:
                    st.write(f"**法定代理人：** {row['法定代理人姓名']}")
                    st.write(f"**法代身分證：** `{row['法定代理人身份證字號']}`")
                    st.write(f"**法代關係碼：** `{row['法定代理人關係']}`")
                    st.write(f"**LINE ID：** {row['LINE_ID']}")
                    st.write(f"**行程區間：** {row['出發時間']} ~ {row['回程時間']}")
                    st.write(f"**繳費方式：** {row['繳費方式']}")
                
                st.divider()
                
                # 進度更新控制項
                new_s = st.radio(
                    "更新進度", ["未處理", "處理中", "已結案"], 
                    index=["未處理", "處理中", "已結案"].index(row['處理狀態']), 
                    key=f"s_{idx}", horizontal=True
                )
                
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