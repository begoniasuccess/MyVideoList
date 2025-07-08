from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import urlparse, parse_qs
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route("/api/playlist", methods=["POST"])
def get_playlist_videos():
    data = request.get_json()
    playlist_url = data.get("url", "")
    print(f"接收到播放清單 URL：{playlist_url}")

    try:
        # 解析 URL 只保留 list ID
        parsed = urlparse(playlist_url)
        qs = parse_qs(parsed.query)
        playlist_id = qs.get("list", [None])[0]
        if not playlist_id:
            return jsonify({"error": "無法解析播放清單 ID"}), 400
        clean_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        print(f"使用清理後的網址：{clean_url}")

        # 使用 yt_dlp 抓播放清單資訊
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)

        playlist_title = info.get("title", "未命名清單")
        videos = []
        for entry in info.get("entries", []):
            videos.append({
                "id": entry.get("id"),
                "title": entry.get("title")
            })

        return jsonify({
            "title": playlist_title,
            "videos": videos
        })
    except Exception as e:
        print("錯誤內容：", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
