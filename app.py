import os
from flask import Flask, render_template, request

# ローカル環境のみ .env を読み込む
if os.getenv("RENDER") is None:
    from dotenv import load_dotenv
    load_dotenv()

app = Flask(__name__)

# 使用するAIプロバイダーを環境変数で指定（"openai" または "gemini"）
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()

# OpenAI設定
if AI_PROVIDER == "openai":
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")

# Gemini設定
elif AI_PROVIDER == "gemini":
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini_model = genai.GenerativeModel("gemini-1.5-pro-latest")  # または "gemini-1.5-flash"

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        tasks = request.form["tasks"]
        tone = request.form["tone"]
        audience = request.form["audience"]
        format_type = request.form["format"]

#         prompt = f"""
# あなたは日報整形アシスタントです。
# 以下の箇条書きの作業内容を、{tone}な文体で、{audience}向けに、{format_type}形式で整形してください。

# 作業内容:
# {tasks}
# """
        prompt = f"""
条件(固定部分)
あなたは日報作成の専門家です。私が今日の業務内容やメモを
箇条書きで伝えたら、以下の形式で整理された日報を作成して
ください:
・「本日行ったこと」「課題・気づき」「明日の予定」の3つの見
出しでまとめる
・日付と担当者名 (田中太郎)を冒頭に入れる

以下の箇条書きの作業内容を、{tone}な文体で、{audience}向けに、{format_type}形式で整形してください。
※Markdown形式指定の時のみ、Markdown形式で整形してください。

日報にまとめたい情報 (可変部分)
作業内容:
{tasks}
"""
        try:
            if AI_PROVIDER == "openai":
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.choices[0].message.content.strip()

            elif AI_PROVIDER == "gemini":
                response = gemini_model.generate_content(prompt)
                result = response.text.strip()

            else:
                result = "AIプロバイダーが未設定です。"

        except Exception as e:
            result = f"エラーが発生しました: {e}"

    return render_template("index.html", result=result, ai_provider=AI_PROVIDER)
