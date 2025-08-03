import os
import pandas as pd
import pdfplumber

# CSV読み込み
def load_csv(filepath):
    df = pd.read_csv(filepath)
    records = []
    for _, row in df.iterrows():
        title = str(row.get("タイトル", "タイトルなし"))
        body = str(row.get("本文", "本文なし"))
        records.append((title, body))
    return records

# Excel読み込み
def load_excel(filepath):
    df = pd.read_excel(filepath, header=1)
    records = []
    for _, row in df.iterrows():
        title = str(row.get("タイトル", "タイトルなし"))
        body = str(row.get("本文", "本文なし"))
        records.append((title, body))
    return records

# PDF読み込み（1ページ1事例として扱う）
def load_pdf(filepath):
    records = []
    with pdfplumber.open(filepath) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                title = f"{os.path.basename(filepath)} ページ{i+1}"
                body = text.strip()
                records.append((title, body))
    return records

# 拡張子ごとに分岐
def extract_text_records(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return load_csv(file_path)
    elif ext == ".xlsx":
        return load_excel(file_path)
    elif ext == ".pdf":
        return load_pdf(file_path)
    else:
        return []  # 未対応の拡張子はスキップ

# 🔁 複数ファイルを一括処理
def load_all_records(folder_path):
    all_records = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.csv', '.xlsx', '.pdf')):
            full_path = os.path.join(folder_path, file)
            print(f"📂 処理中: {file}")
            try:
                records = extract_text_records(full_path)
                all_records.extend(records)
            except Exception as e:
                print(f"❌ エラー: {file} - {e}")
    return all_records

# ✅ 実行部
if __name__ == "__main__":
    folder = "data"
    records = load_all_records(folder)

    print(f"\n✅ 合計読み込み件数: {len(records)} 件\n")
    for title, body in records[:3]:  # 最初の3件だけ表示
        print(f"🔸 {title}\n{body[:100]}...\n")


import pdfplumber
import os
import pandas as pd

def extract_text_from_pdf(filepath):
    try:
        with pdfplumber.open(filepath) as pdf:
            texts = [page.extract_text() for page in pdf.pages if page.extract_text()]
        return "\n".join(texts)
    except Exception as e:
        return f"(PDF読込失敗: {e})"

def extract_text_records(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.csv':
        df = pd.read_csv(filepath)
    elif ext == '.xlsx':
        df = pd.read_excel(filepath)
    elif ext == '.pdf':
        text = extract_text_from_pdf(filepath)
        return [(os.path.basename(filepath), text)]
    else:
        return []

    records = []
    for _, row in df.iterrows():
        title = str(row[0]) if len(row) > 0 else ""
        body = str(row[1]) if len(row) > 1 else ""
        records.append((title, body))
    return records

def load_all_records(folder):
    all_records = []
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if os.path.isfile(path):
            all_records.extend(extract_text_records(path))
    return all_records

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

def search_similar_records(query, records, top_k=3):
    texts = [title + " " + body for title, body in records]
    query_vec = model.encode([query])
    record_vecs = model.encode(texts)

    similarities = cosine_similarity(query_vec, record_vecs)[0]
    top_indices = similarities.argsort()[::-1][:top_k]

    results = []
    for idx in top_indices:
        score = similarities[idx]
        title, body = records[idx]
        results.append((score, title, body))
    return results


from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

def search_similar_records(query, records, top_k=3):
    texts = [title + " " + body for title, body in records]
    query_vec = model.encode([query])
    record_vecs = model.encode(texts)

    similarities = cosine_similarity(query_vec, record_vecs)[0]
    top_indices = similarities.argsort()[::-1][:top_k]

    results = []
    for idx in top_indices:
        score = similarities[idx]
        title, body = records[idx]
        results.append((score, title, body))
    return results
