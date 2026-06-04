import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

# 1. 台灣時區與網頁設定
tw_tz = timezone(timedelta(hours=8))
st.set_page_config(page_title="旅平險投保系統", layout="wide")

DB_FILE = "travel_data.csv"

# 資料庫所有欄位定義 (完整保留要保人 + 展開被保險人9大欄位)
DB_COLUMNS = [
    "投稿時間", "要保人姓名", "要保人身分證", "要保人生日", "通訊地址", 
    "手機號碼", "要保人Email", "旅遊目的地", "出發時間", "回程時間", "繳費方式", "LINE_ID",
    "被保人身分證號_居留證號", "被保人姓名", "被保人出生年月日_7碼", "被保人行動電話_10碼",
    "被保人國籍", "旅平險保額_萬", "法定代理人姓名", "法定代理人身份證字號", "法定代理人關係_2碼",
    "處理狀態"
]

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        for col in DB_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[DB_COLUMNS]
    return pd.DataFrame(columns=DB_COLUMNS)

# --- 側邊欄：分頁控制 ---
with st.sidebar:
    st.title("🛡️ 系統選單")
    mode = st.radio("切換頁面：", ["📝 客戶投保填寫", "📊 業務管理後台"])
    st.divider()
    if mode == "📊 業務管理後台":
        pwd = st.text_input("輸入管理密碼", type="password")
        if pwd != "085799":
            st.warning("請輸入正確密碼以進入後台。")
            st.stop()

# --- 【前台介面】 ---
if mode == "📝 客戶投保填寫":
    st.title("✈️ 旅平險投保資料填寫")
    now_time = datetime.now(tw_tz).strftime('%Y-%m-%d %H:%M:%S')
    st.info(f"📋 系統自動記錄投稿時間：{now_time}")

    with st.form("client_form", clear_on_submit=False):
        # 部位一：完整保留要保人基本資料
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
        
        # 部位二：行程與繳費
        st.subheader("🗓️ 旅遊行程與繳費")
        u_dest = st.text_input("旅遊目的地 *")
        
        c5, c6 = st.columns(2)
        u_start = c5.text_input("出發日期與時間 *", placeholder="例：2026-05-01 09:00")
        u_end = c6.text_input("回程日期與時間 *", placeholder="例：2026-05-05 18:00")
        
        u_pay = st.selectbox("繳費方式 *", ["請選擇", "超商繳費單", "刷卡"])
        u_line = st.text_input("業務或您的 LINE ID *")
        
        st.divider()
        
        # 部位三：全面升級「動態被保險人名冊」
        st.subheader("👥 被保險人名冊錄入 (含主被保人與隨行人員)")
        st.caption("💡 規範提示：1.主被保險人請填在第一位。 2.外籍人士身分證請填ARC居留證號。 3.生日請填7碼民國年(如0840520)。 4.關係碼：01父子 02父女 03母子 04母女 05其他。 (支援從 Excel 複製多筆直接貼上表格)")
        
        # 定義互動表格的空樣板
        init_df = pd.DataFrame([
            {"身分證號/居留證號": "", "姓名": "", "出生年月日(民國7碼)": "", "行動電話(10碼)": "", "國籍": "TW", "保額(萬)": 500, "法代姓名": "", "法代身分證": "", "法代關係碼": ""}
        ])
        
        # 使用 Streamlit 高級數據編輯器
        edited_df = st.data_editor(
            init_df,
            num_rows="dynamic", # 允許自由新增/刪除資料列
            use_container_width=True,
            column_config={
                "法代關係碼": st.column_config.SelectboxColumn(
                    options=["", "01", "02", "03", "04", "05"],
                    help="01父子 02父女 03母子 04母女 05其他"
                ),
                "保額(萬)": st.column_config.NumberColumn(min_value=0, max_value=2000, step=50)
            },
            key="ins_editor"
        )
        
        submit_btn = st.form_submit_button("✅ 確認送出資料")

    # --- 漏填與格式檢查邏輯 ---
    if submit_btn:
        # 1. 檢查要保人與行程基本項
        base_check = [u_name, u_id, u_phone, u_email, u_addr, u_dest, u_start, u_end, u_line]
        
        # 2. 清理並過濾被保險人表格（剔除完全空白列）
        cleaned_ins_df = edited_df.dropna(subset=["身分證號/居留證號", "姓名"]).loc[
            (edited_df["身分證號/居留證號"].str.strip() != "") & (edited_df["姓名"].str.strip() != "")
        ]
        
        if not all(base_check) or u_pay == "請選擇":
            st.error("⚠️ 傳送失敗！要保人資料、行程、繳費方式等必填欄位不可留空。")
        elif cleaned_ins_df.empty:
            st.error("⚠️ 傳送失敗！請至少填寫一位完整的被保險人資料。")
        else:
            # 3. 檢查被保人表格內的格式細節
            format_error = False
            for _, idx_row in cleaned_ins_df.iterrows():
                bday_str = str(idx_row["出生年月日(民國7碼)"]).strip()
                phone_str = str(idx_row["行動電話(10碼)"]).strip()
                
                if len(bday_str) != 7:
                    st.error(f"⚠️ 格式錯誤：被保人【{idx_row['姓名']}】的出生年月日必須為 7 碼民國年文字（例如：0840520）。")
                    format_error = True
                    break
                if len(phone_str) != 10:
                    st.error(f"⚠️ 格式錯誤：被保人【{idx_row['姓名']}】的行動電話必須為 10 碼文字（例如：0912345678）。")
                    format_error = True
                    break
            
            if not format_error:
                # 4. 格式完全正確，展開並扁平化儲存至資料庫 (一筆被保人存成一列，共用同一個要保人與行程資訊)
                new_rows = []
                for _, idx_row in cleaned_ins_df.iterrows():
                    new_rows.append({
                        "投稿時間": now_time,
                        "要保人姓名": u_name.strip(),
                        "要保人身分證": u_id.strip().upper(),
                        "要保人生日": str(u_bday),
                        "通訊地址": u_addr.strip(),
                        "手機號碼": u_phone.strip(),
                        "要保人Email": u_email.strip(),
                        "旅遊目的地": u_dest.strip(),
                        "出發時間": u_start.strip(),
                        "回程時間": u_end.strip(),
                        "繳費方式": u_pay,
                        "LINE_ID": u_line.strip(),
                        # 被保人 9 大欄位對齊
                        "被保人身分證號_居留證號": str(idx_row["身分證號/居留證號"]).strip().upper(),
                        "被保人姓名": str(idx_row["姓名"]).strip(),
                        "被保人出生年月日_7碼": bday_str,
                        "被保人行動電話_10碼": phone_str,
                        "被保人國籍": str(idx_row["國籍"]).strip().upper(),
                        "旅平險保額_萬": f"{idx_row['保額(萬)']}萬",
                        "法定代理人姓名": str(idx_row["法代姓名"]).strip() if pd.notna(idx_row["法代姓名"]) and str(idx_row["法代姓名"]).strip() != "" else "無",
                        "法定代理人身份證字號": str(idx_row["法代身分證"]).strip().upper() if pd.notna(idx_row["法代身分證"]) and str(idx_row["法代身分證"]).strip() != "" else "無",
                        "法定代理人關係_2碼": str(idx_row["法代關係碼"]).strip() if pd.notna(idx_row["法代關係碼"]) and str(idx_row["法代關係碼"]).strip() != "" else "無",
                        "處理狀態": "未處理"
                    })
                
                df_to_save = pd.DataFrame(new_rows)
                df_existing = load_data()
                pd.concat([df_existing, df_to_save], ignore_index=True).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                
                st.success(f"🎉 提交成功！已成功錄入 {len(df_to_save)} 筆隨行被保險人投保申請。")
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
        st.sidebar.download_button(
            "📥 下載完備名冊 (Excel/CSV)", 
            df.to_csv(index=False).encode('utf-8-sig'), 
            f"travel_backup_{datetime.now(tw_tz).strftime('%m%d')}.csv"
        )
        
        # 依案件倒序顯示
        for idx, row in df.iloc[::-1].iterrows():
            with st.expander(f"【{row['處理狀態']}】被保人：{row['被保人姓名']} ➔ 要保人：{row['要保人姓名']} ({row['🟢 投稿時間'] if '🟢 投稿時間' in df.columns else row['投稿時間']})"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("##### 👤 要保人資訊")
                    st.write(f"**姓名/身分證：** {row['要保人姓名']} / `{row['要保人身分證']}`")
                    st.write(f"**手機/Email：** {row['手機號碼']} / {row['要保人Email']}")
                    st.write(f"**通訊地址：** {row['通訊地址']}")
                    st.write(f"**行程：** {row['出發時間']} ~ {row['回程時間']}")
                    st.write(f"**目的地/繳費：** {row['旅遊目的地']} / {row['繳費方式']}")
                with c2:
                    st.markdown("##### 🛡️ 被保險人 9 大精準申報資料")
                    st.write(f"**1. 身分證(居留證)：** `{row['...居留證號'] if '...居留證號' in df.columns else row['被保人身分證號_居留證號']}`")
                    st.write(f"**2. 被保人姓名：** {row['被保人姓名']}")
                    st.write(f"**3. 出生年月日(民7碼)：** `{row['...7碼'] if '...7碼' in df.columns else row['被保人出生年月日_7碼']}`")
                    st.write(f"**4. 行動電話(10碼)：** `{row['...10碼'] if '...10碼' in df.columns else row['被保人行動電話_10碼']}`")
                    st.write(f"**5. 國籍 / 6. 保額：** `{row['被保人國籍']}` / {row['旅平險保額_萬']}")
                    st.write(f"**7. 法代姓名 / 8. 法代ID：** {row['法定代理人姓名']} / `{row['法定代理人身份證字號']}`")
                    st.write(f"**9. 法代關係代碼：** `{row['法定代理人關係_2碼']}`")
                
                st.divider()
                
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