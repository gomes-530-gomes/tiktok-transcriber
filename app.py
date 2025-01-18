from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

# AssemblyAIのAPIキーを設定
API_KEY = "334acc98b51c4c049a4520f3d26bdcb4"
HEADERS = {"authorization": API_KEY}

def upload_audio(file_path):
    """
    音声ファイルをAssemblyAIにアップロードする関数
    """
    with open(file_path, "rb") as f:
        response = requests.post(
            "https://api.assemblyai.com/v2/upload", headers=HEADERS, files={"file": f}
        )
    response.raise_for_status()
    return response.json()["upload_url"]

def transcribe_audio(audio_url):
    """
    AssemblyAIに音声文字起こしリクエストを送信する関数
    """
    transcript_request = {"audio_url": audio_url}
    response = requests.post(
        "https://api.assemblyai.com/v2/transcript", json=transcript_request, headers=HEADERS
    )
    response.raise_for_status()
    transcript_id = response.json()["id"]

    # ポーリングして文字起こし結果を取得
    while True:
        polling_response = requests.get(
            f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=HEADERS
        )
        status = polling_response.json()["status"]
        if status == "completed":
            return polling_response.json()["text"]
        elif status == "failed":
            raise Exception("Transcription failed")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    # ファイルを保存
    audio_file = request.files["file"]
    file_path = os.path.join("uploads", audio_file.filename)
    audio_file.save(file_path)

    try:
        # AssemblyAIに音声ファイルをアップロード
        audio_url = upload_audio(file_path)
        # 音声文字起こし
        transcript_text = transcribe_audio(audio_url)
        return jsonify({"text": transcript_text})
    finally:
        os.remove(file_path)  # 処理後にファイルを削除

if __name__ == "__main__":
    # Renderが提供するPORT環境変数を取得
    port = int(os.environ.get("PORT", 5000))
    # ホストは"0.0.0.0"を指定する必要があります
    app.run(host="0.0.0.0", port=port)