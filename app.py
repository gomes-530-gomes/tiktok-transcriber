from flask import Flask, request, jsonify, render_template
import yt_dlp
import whisper
import os

app = Flask(__name__)

# 動画のダウンロード
def download_video(url, output_path):
    options = {
        'format': 'mp4',
        'outtmpl': output_path
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

# 文字起こし
def transcribe_video(video_path):
    model = whisper.load_model("base")
    result = model.transcribe(video_path)
    return result["text"]

@app.route('/')
def index():
    return render_template('index.html')  # フォームページを表示

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        tiktok_url = request.form.get('url')
        if not tiktok_url:
            return jsonify({"error": "URLを入力してください"}), 400

        video_path = "downloaded_video.mp4"
        download_video(tiktok_url, video_path)

        transcription = transcribe_video(video_path)

        os.remove(video_path)  # 不要になった動画を削除

        return jsonify({"transcription": transcription})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

import os

if __name__ == "__main__":
    # Renderが提供するPORT環境変数を使用
    port = int(os.environ.get("PORT", 5000))  # PORTが未設定の場合、ローカルでは5000を使用
    app.run(host="0.0.0.0", port=port, debug=True)