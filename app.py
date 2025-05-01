import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from detector import detect_horses, process_video
from report_generator import generate_report

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATABASE'] = 'database/history.db'

# Создаем папки при запуске
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('database', exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        conn = get_db_connection()
        conn.execute('''CREATE TABLE IF NOT EXISTS requests
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp DATETIME,
                      filename TEXT,
                      horse_count INTEGER,
                      processed_path TEXT)''')
        conn.commit()
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Сохраняем оригинальный файл
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(original_path)
    
    # Обработка файла
    try:
        if file.content_type.startswith('image/'):
            count, processed_img = detect_horses(original_path)
            processed_filename = f"processed_{filename}"
            processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
            processed_img.save(processed_path)
            file_type = 'image'
        elif file.content_type.startswith('video/'):
            processed_path = process_video(original_path)
            count = -1  # Для видео счетчик не считаем
            file_type = 'video'
        else:
            return jsonify({'error': 'Unsupported file type'}), 400
        
        # Сохраняем в БД
        conn = get_db_connection()
        conn.execute('INSERT INTO requests (timestamp, filename, horse_count, processed_path) VALUES (?, ?, ?, ?)',
                     (datetime.now(), filename, count, processed_path))
        conn.commit()
        conn.close()
        
        return jsonify({
            'file_type': file_type,
            'original': filename,
            'processed': os.path.basename(processed_path),
            'count': count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/history')
def show_history():
    conn = get_db_connection()
    requests = conn.execute('SELECT * FROM requests ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('history.html', requests=requests)

@app.route('/generate-report')
def generate_pdf_report():
    conn = get_db_connection()
    requests = conn.execute('SELECT * FROM requests').fetchall()
    conn.close()
    
    report_path = generate_report(requests)
    return send_from_directory('.', report_path, as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)