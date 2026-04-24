from flask import Flask, render_template, request, send_file
import io

app = Flask(__name__)

# ----------------------------------------------------
# 1. 画面を表示する処理
# ----------------------------------------------------
@app.route("/")
def index():
    # templatesフォルダの中にある index.html を表示する
    return render_template("index.html")

# ----------------------------------------------------
# 2. 音声を合成する処理（API）
# ----------------------------------------------------
@app.route("/synthesize", methods=["POST"])
def synthesize():
    # HTML（JavaScript）から送られてきたデータを受け取る
    data = request.get_json()
    text = data.get("text", "")
    pitch = float(data.get("pitch", 1.0))
    
    # 🌟 本来はここに pyworld などの処理を書きます！
    # 今回はテスト用なので、処理した「つもり」の仮の動きにします
    print(f"【サーバー】リクエスト受信: テキスト='{text}', ピッチ={pitch}")
    
    # ※ダミーとして既存のWAVファイルを返すか、エラーにならないように仮の処理をします
    # ここでは仮に、ローカルにある "dummy.wav" を返すようなコードの形にしておきます
    # return send_file("dummy.wav", mimetype="audio/wav")
    
    return "処理の繋ぎこみは後で行います", 200

# ----------------------------------------------------
# アプリの起動
# ----------------------------------------------------
if __name__ == "__main__":
    # Google Cloudなどで動かす場合は host="0.0.0.0" を指定します
    app.run(host="0.0.0.0", port=8080, debug=True)
