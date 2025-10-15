from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import tempfile
import shutil
from urllib.parse import urlparse
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
from flask_cors import CORS
CORS(app)

ALLOWED_DOMAINS = {
    'youtube.com', 'youtu.be',
    'rutube.ru', 'rutube.com',
    'vk.com', 'vimeo.com',
    'dailymotion.com', 'soundcloud.com',
    'twitch.tv', 'instagram.com'
}

def is_allowed_url(url):
    try:
        domain = urlparse(url).netloc.lower()
        return any(allowed in domain for allowed in ALLOWED_DOMAINS)
    except Exception:
        return False

def sanitize_filename(filename):
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    return filename.strip()[:255] or 'video'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    temp_dir = None
    try:
        data = request.get_json()
        url = data.get('url')
        download_type = data.get('type', 'video')
        quality = data.get('quality', '720')  # "1080", "720", "480"

        if not url:
            return jsonify({"error": "URL не передан"}), 400

        if not is_allowed_url(url):
            return jsonify({"error": "❌ Недопустимый источник видео"}), 400

        # Простой выбор формата БЕЗ ffmpeg
        if download_type == 'video':
            if quality == '1080':
                format_selector = 'best[height<=1080]/best[height<=720]/best[height<=480]/best'
            elif quality == '720':
                format_selector = 'best[height<=720]/best[height<=480]/best'
            elif quality == '480':
                format_selector = 'best[height<=480]/best'
            else:
                format_selector = 'best'
        else:
            format_selector = 'bestaudio/best'

        temp_dir = tempfile.mkdtemp()

        ydl_opts = {
            'format': format_selector,
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            # УБРАЛИ: 'merge_output_format' — не нужен без ffmpeg
        }

        logger.info(f"Скачивание ({download_type}, {quality}p): {url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filepath = os.path.join(temp_dir, filename)

            if not os.path.exists(filepath):
                return jsonify({"error": "Файл не создан"}), 500

            title = info.get('title', 'video')
            ext = info.get('ext', 'mp4')
            safe_title = sanitize_filename(title)
            download_name = f"{safe_title}.{ext}"

            return send_file(filepath, as_attachment=True, download_name=download_name)

    except yt_dlp.DownloadError as e:
        error_msg = str(e).lower()
        logger.error(f"yt-dlp ошибка: {error_msg}")
        if any(kw in error_msg for kw in ["sign in", "authentication", "age", "private", "bot", "unavailable", "copyright"]):
            return jsonify({"error": "❌ Видео приватное или требует авторизации."}), 400
        return jsonify({"error": "❌ Не удалось скачать видео. Попробуйте другое."}), 500

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return jsonify({"error": "❌ Внутренняя ошибка сервера."}), 500

    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.info("Временная папка удалена")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
