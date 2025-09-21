import os
from flask import Flask, render_template, request, redirect
from models import db, DailyReport
from datetime import datetime


if os.getenv("RENDER") is None:
    from dotenv import load_dotenv
    load_dotenv()

app = Flask(__name__)

db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
# with app.app_context():
#     db.create_all()

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()

if AI_PROVIDER == "openai":
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
elif AI_PROVIDER == "gemini":
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini_model = genai.GenerativeModel("gemini-1.5-pro-latest")

def generate_report(tasks, tone, audience, format_type):
    prompt = f"""
条件(固定部分)
あなたは日報作成の専門家です。私が今日の業務内容やメモを箇条書きで伝えたら、以下の形式で整理された日報を作成してください:
・「本日行ったこと」「課題・気づき」「明日の予定」の3つの見出しでまとめる
・日付と担当者名 (田中太郎)を冒頭に入れる

以下の箇条書きの作業内容を、{tone}な文体で、{audience}向けに、{format_type}形式で整形してください。
※Markdown形式指定の時のみ、Markdown形式で整形してください。

作業内容:
{tasks}
"""
    try:
        if AI_PROVIDER == "openai":
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        elif AI_PROVIDER == "gemini":
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
        else:
            return "AIプロバイダーが未設定です。"
    except Exception as e:
        return f"エラーが発生しました: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    tasks = tone = audience = format_type = ""
    if request.method == "POST":
        tasks = request.form["tasks"]
        tone = request.form["tone"]
        audience = request.form["audience"]
        format_type = request.form["format"]
        result = generate_report(tasks, tone, audience, format_type)

        report = DailyReport(
            tasks=tasks,
            tone=tone,
            audience=audience,
            format_type=format_type,
            result=result
        )
        db.session.add(report)
        db.session.commit()

    return render_template("index.html", result=result, ai_provider=AI_PROVIDER,
                           tasks=tasks, tone=tone, audience=audience, format_type=format_type)

@app.route("/history")
def history():
    reports = DailyReport.query.order_by(DailyReport.created_at.desc()).all()
    return render_template("history.html", reports=reports)

@app.route("/load/<int:report_id>")
def load(report_id):
    report = DailyReport.query.get(report_id)
    return render_template("index.html", result="", ai_provider=AI_PROVIDER,
                           tasks=report.tasks, tone=report.tone,
                           audience=report.audience, format_type=report.format_type)
