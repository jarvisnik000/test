import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_app, get_db, using_postgres
from models import Note
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)
CORS(app)

# Инициализируем базу данных
init_app(app)

@app.route('/')
def index():
    return jsonify({
        'message': 'Notes API',
        'version': '1.0.0',
        'endpoints': {
            'GET /api/notes': 'Get all notes',
            'GET /api/notes/<id>': 'Get note by ID',
            'POST /api/notes': 'Create new note',
            'PUT /api/notes/<id>': 'Update note',
            'DELETE /api/notes/<id>': 'Delete note',
            'GET /api/notes/tag/<tag>': 'Search notes by tag',
            'GET /api/health': 'Health check'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        db = get_db()
        if using_postgres():
            with db.cursor() as cur:
                cur.execute('SELECT 1')
        else:
            db.execute('SELECT 1')
        db_type = 'postgresql' if using_postgres() else 'sqlite'
        return jsonify({
            'status': 'healthy',
            'database': db_type,
            'connected': True
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Получить все заметки"""
    try:
        notes = Note.get_all()
        return jsonify(notes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Получить заметку по ID"""
    note = Note.get_by_id(note_id)
    if note:
        return jsonify(note)
    return jsonify({'error': 'Note not found'}), 404

@app.route('/api/notes', methods=['POST'])
def create_note():
    """Создать новую заметку"""
    try:
        data = request.get_json()
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        note_id = Note.create(
            title=data['title'],
            content=data['content'],
            tags=data.get('tags', [])
        )
        
        return jsonify({
            'message': 'Note created successfully',
            'id': note_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Обновить существующую заметку"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        Note.update(
            note_id=note_id,
            title=data.get('title', ''),
            content=data.get('content', ''),
            tags=data.get('tags', [])
        )
        
        return jsonify({'message': 'Note updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Удалить заметку"""
    try:
        Note.delete(note_id)
        return jsonify({'message': 'Note deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/tag/<tag>', methods=['GET'])
def search_by_tag(tag):
    """Найти заметки по тегу"""
    try:
        notes = Note.search_by_tag(tag)
        return jsonify(notes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)