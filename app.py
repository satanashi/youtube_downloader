from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import tempfile
import shutil
from urllib.parse import urlparse
import re
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# CORS включён для удобства разработки (можно отключить в продакшене)
from flask_cors import CORS
CORS(app)

# Разрешённые домены (можно расширить при необходимости)
ALLOWED_DOMAINS = {
    'youtube.com', 'youtu.be',
    'rutube.ru', 'rutube.com',
    'vk.com', 'vimeo.com',
    'dailymotion.com', 'soundcloud.com',
    'twitch.tv', 'instagram.com', 'facebook.com'
}

def is_allowed_url(url):
    """Проверяет, разрешён ли домен в URL."""
    try:
        domain = urlparse(url).netloc.lower()
        return any(allowed in domain for allowed in ALLOWED_DOMAINS)
    except Exception:
        return False

def sanitize_filename(filename):
    """Удаляет недопустимые символы и ограничивает длину имени файла."""
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    max_length = 255
    if len(filename) > max_length:
        filename = filename[:max_length]
    return filename.strip()

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

        if not url:
            return jsonify({"error": "URL не передан"}), 400

        if not is_allowed_url(url):
            return jsonify({"error": "❌ Недопустимый источник видео. Поддерживаются только публичные платформы (YouTube, Rutube, VK и др.)."}), 400

        # Выбор формата
        format_selector = 'best[height<=720]' if download_type == 'video' else 'bestaudio/best'

        # Создаём временную папку
        temp_dir = tempfile.mkdtemp()

        ydl_opts = {
            'format': format_selector,
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
        }

        logger.info(f"Начало скачивания ({download_type}): {url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # yt-dlp сам формирует имя файла
            filename = ydl.prepare_filename(info)
            filepath = os.path.join(temp_dir, filename)

            if not os.path.exists(filepath):
                return jsonify({"error": "❌ Файл не был создан. Возможно, видео недоступно."}), 500

            # Подготавливаем безопасное имя для скачивания
            title = info.get('title', 'video')
            ext = info.get('ext', 'mp4')
            safe_title = sanitize_filename(title)
            download_name = f"{safe_title}.{ext}"

            logger.info(f"Файл готов: {download_name}")
            return send_file(filepath, as_attachment=True, download_name=download_name)

    except yt_dlp.DownloadError as e:
        error_msg = str(e)
        logger.error(f"Ошибка yt-dlp: {error_msg}")

        if any(keyword in error_msg.lower() for keyword in ["sign in", "authentication", "age", "private", "bot"]):
            return jsonify({
                "error": "❌ Это видео требует авторизации или имеет возрастные ограничения. Используйте только публичные видео."
            }), 400

        return jsonify({"error": f"❌ Ошибка при скачивании: {error_msg}"}), 500

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Неожиданная ошибка: {error_msg}")
        return jsonify({"error": "❌ Произошла внутренняя ошибка. Попробуйте другое видео."}), 500

    finally:
        # Всегда удаляем временную папку
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.info(f"Временная папка удалена: {temp_dir}")

if __name__ == '__main__':
    # Запуск только в локальной сети (не публичный сервер без HTTPS и аутентификации!)
    app.run(host='127.0.0.1', port=5000, debug=False)
