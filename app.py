import io
import numpy as np
import pyopenjtalk
import pyworld as pw
import soundfile as sf
from flask import Flask, render_template, request, send_file

app = Flask(__name__)


@app.route("/")
def index():
    # templates/index.html を読み込んで画面を表示
    return render_template("index.html")


@app.route("/synthesize", methods=["POST"])
def synthesize():
    # 1. フロントエンドからのデータを受け取る
    data = request.get_json()
    text = data.get("text", "テキストが空です")
    pitch_ratio = float(data.get("pitch", 1.0))
    formant_ratio = float(data.get("formant", 1.0))
    speed_ratio = float(data.get("speed", 1.0))

    print(
        f"【サーバー】合成開始: テキスト='{text}', ピッチ={pitch_ratio}, 声質={formant_ratio}, スピード={speed_ratio}"
    )

    try:
        # 2. Open JTalk でベース音声を生成
        x, sr = pyopenjtalk.tts(text)
        x = x.astype(np.float64)

        # 3. pyworld (WORLDボコーダー) で音声を3要素に分解
        # がたがた感を抑えるため、高精度な harvest アルゴリズムを採用
        f0, t = pw.harvest(x, sr)
        sp = pw.cheaptrick(x, f0, t, sr)
        ap = pw.d4c(x, f0, t, sr)

        # 4. ピッチ（F0: 声の高さ）の変更
        modified_f0 = f0.copy()
        modified_f0[modified_f0 > 0] *= pitch_ratio
        modified_f0 = np.ascontiguousarray(modified_f0, dtype=np.float64)

        # 5. フォルマント（SP: 声質・響き）の変更
        modified_sp = np.zeros_like(sp)
        freq_axis = np.arange(sp.shape[1])
        for i in range(sp.shape[0]):
            modified_sp[i] = np.interp(
                freq_axis / formant_ratio, freq_axis, sp[i]
            )
        modified_sp = np.ascontiguousarray(modified_sp, dtype=np.float64)

        # 6. スピードの変更と音声の再合成
        # 標準のコマ間隔 5.0ms を speed_ratio で割ることで再生速度を調整
        new_frame_period = 5.0 / speed_ratio
        y = pw.synthesize(
            modified_f0, modified_sp, ap, sr, frame_period=new_frame_period
        )

        # 7. 生成した波形をメモリ上のWAVファイル形式に変換
        out_io = io.BytesIO()
        sf.write(out_io, y, sr, format="WAV")
        out_io.seek(0)

        # 8. 音声データとしてブラウザへ返却
        return send_file(out_io, mimetype="audio/wav")

    except Exception as e:
        print(f"【エラー】合成処理中にエラーが発生しました: {e}")
        return str(e), 500


if __name__ == "__main__":
    # ローカルサーバーの起動 (ポート: 8080)
    app.run(host="0.0.0.0", port=8080, debug=True)