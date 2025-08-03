# app.py
import streamlit as st
import os
import csv
from io import BytesIO
import pandas as pd
import pdfplumber
from docx import Document
from datetime import datetime

from gpt_advice import query_gpt
from main import load_all_records, search_similar_records

st.set_page_config(page_title="失敗事例アドバイスBot", layout="wide")
st.title("🛠️ 失敗事例アドバイスBot")

# 📤 ファイルアップロード（CSV, PDF, Excel, Word対応）
st.sidebar.header("📤 失敗事例ファイルのアップロード")
uploaded_files = st.sidebar.file_uploader(
    "CSV, Excel, PDF, Word に対応しています", 
    type=["csv", "xlsx", "pdf", "docx"], 
    accept_multiple_files=True
)

def extract_text_records_from_upload(file):
    ext = os.path.splitext(file.name)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(file)
        return [(str(row.get("タイトル", "タイトルなし")), str(row.get("本文", "本文なし"))) for _, row in df.iterrows()]

    elif ext == ".xlsx":
        df = pd.read_excel(file, header=1)
        return [(str(row.get("タイトル", "タイトルなし")), str(row.get("本文", "本文なし"))) for _, row in df.iterrows()]

    elif ext == ".pdf":
        records = []
        with pdfplumber.open(BytesIO(file.read())) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    records.append((f"{file.name} ページ{i+1}", text.strip()))
        return records

    elif ext == ".docx":
        doc = Document(file)
        records = []
        current_title = ""
        for para in doc.paragraphs:
            if para.style.name.startswith("Heading"):
                current_title = para.text.strip()
            elif para.text.strip():
                records.append((current_title or "タイトルなし", para.text.strip()))
        return records

    else:
        return []

# 事前登録済み＋アップロードファイルを合体
@st.cache_resource
def load_records():
    return load_all_records("data")

base_records = load_records()
uploaded_records = []
for file in uploaded_files:
    uploaded_records.extend(extract_text_records_from_upload(file))

records = uploaded_records + base_records
st.caption(f"📊 使用中の事例数：{len(records)} 件")

# 💬 ユーザー入力
query = st.text_input("質問を入力してください（例：ネジが緩む原因は？）")

# セッション履歴保持
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if query:
    # ① 類似事例検索
    results = search_similar_records(query, records)
    similar_text = "\n".join([f"【{title}】\n{body}" for _, title, body in results])

    # ② GPTアドバイス生成
    with st.spinner("GPTが考え中です..."):
        answer = query_gpt(query, similar_text)

    # ③ ログ保存
    os.makedirs("logs", exist_ok=True)
    with open("logs/chat_log.csv", mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), query, answer])

    # ④ セッション履歴保存
    st.session_state.chat_history.append((query, answer))

    # 🔍 類似事例表示
    st.subheader("🔍 類似事例（上位3件）")
    for score, title, body in results:
        with st.expander(f"{title}（スコア: {score:.2f}）"):
            st.write(body)

    # 💡 GPTアドバイス表示
    st.subheader("💡 GPTによるアドバイス")
    st.success(answer)

    # 📥 ダウンロードボタン（全文）
    download_text = ""
    for score, title, body in results:
        download_text += f"【{title}】（スコア: {score:.2f}）\n{body}\n\n"

    st.download_button(
        label="📥 類似事例をテキストでダウンロード",
        data=download_text,
        file_name="similar_cases.txt",
        mime="text/plain"
    )

# 📖 セッション内履歴表示
if st.session_state.chat_history:
    with st.expander("📖 これまでのやり取り（このセッション）"):
        for i, (q, a) in enumerate(reversed(st.session_state.chat_history), 1):
            st.markdown(f"**Q{i}：{q}**")
            st.markdown(f"🧠 A{i}：{a}")
