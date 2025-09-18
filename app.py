import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
import openai

# ローカル環境のみ .env を読み込む
if os.getenv("RENDER") is None:
    from dotenv import load_dotenv
    load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        tasks = request.form["tasks"]
        tone = request.form["tone"]
        audience = request.form["audience"]
        format_type = request.form["format"]

        prompt = f"""
あなたは日報整形アシスタントです。
以下の箇条書きの作業内容を、{tone}な文体で、{audience}向けに、{format_type}形式で整形してください。

作業内容:
{tasks}
"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()

    return render_template("index.html", result=result)
