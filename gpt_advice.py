import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def query_gpt(user_question, similar_cases_text):
    prompt = f"""以下は失敗事例集の一部です。
{similar_cases_text}

この事例を参考に、次の質問に対してアドバイスをお願いします。
質問：{user_question}

できるだけ具体的なアドバイスを、わかりやすく記述してください。
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは製造業の技術者です。以下の資料を必ず参考にしながら、質問に対してアドバイスを出してください。\n"
    "特に該当する事例のタイトルや具体的な問題点・対策があればそれをもとに答えてください。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content
