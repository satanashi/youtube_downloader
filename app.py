from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
from flask_cors import CORS
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Для публичного сервера используем системную папку загрузок
DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def sanitize_filename(filename):
    # Удаляем недопустимые символы
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Ограничиваем длину имени файла
    max_length = 255  # Максимальная длина имени файла в Windows
    if len(filename) > max_length:
        # Обрезаем слишком длинное имя файла
        filename = filename[:max_length]
    
    return filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        url = data.get('url')
        download_type = data.get('type', 'video')

        if not url:
            return jsonify({"error": "URL не передан"}), 400

        # Определяем формат скачивания
        format_selector = 'best[height<=720]' if download_type == 'video' else 'bestaudio/best'
        
        ydl_opts = {
            'format': format_selector,
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        }

        logger.info(f"Скачивание {download_type}: {url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Видео')
            
            # Очищаем имя файла
            sanitized_title = sanitize_filename(title)
            filepath = os.path.join(DOWNLOAD_FOLDER, f"{sanitized_title}.{info.get('ext', 'mp4')}")
            
            # Отправляем файл напрямую клиенту
            return send_file(filepath, as_attachment=True, download_name=f"{sanitized_title}.mp4")

    except yt_dlp.DownloadError as e:
        error_msg = str(e)
        logger.error(f"Ошибка скачивания: {error_msg}")
        
        # Красивая обработка ошибок авторизации
        if "Sign in" in error_msg or "bot" in error_msg or "authentication" in error_msg.lower():
            return jsonify({
                "error": "❌ Это видео требует авторизации. Пожалуйста, используйте публичные видео без возрастных ограничений."
            }), 400
            
        return jsonify({"error": f"❌ Ошибка скачивания: {error_msg}"}), 500
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Неожиданная ошибка: {error_msg}")
        return jsonify({"error": "❌ Произошла ошибка. Попробуйте другое видео."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)