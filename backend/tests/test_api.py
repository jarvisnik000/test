import pytest
import json
import tempfile
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

@pytest.fixture
def client():
    """Создаем тестового клиента"""
    # Используем временную базу данных
    db_fd, db_path = tempfile.mkstemp()
    
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path
    
    with app.test_client() as client:
        with app.app_context():
            from database import init_db, get_db
            init_db()
        yield client
    
    # Закрываем и удаляем временную базу данных
    os.close(db_fd)
    os.unlink(db_path)

def test_health_check(client):
    """Тест проверки работоспособности"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['database'] in ('sqlite', 'postgresql')

def test_create_note(client):
    """Тест создания заметки"""
    note_data = {
        'title': 'Test Note',
        'content': 'Test Content',
        'tags': ['test', 'python']
    }
    
    response = client.post(
        '/api/notes',
        data=json.dumps(note_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data
    assert data['message'] == 'Note created successfully'

def test_get_all_notes(client):
    """Тест получения всех заметок"""
    # Сначала создаем заметку
    note_data = {
        'title': 'Test Note',
        'content': 'Test Content',
        'tags': ['test']
    }
    client.post('/api/notes', 
                data=json.dumps(note_data),
                content_type='application/json')
    
    # Затем получаем все заметки
    response = client.get('/api/notes')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0

def test_create_note_validation(client):
    """Тест валидации при создании заметки"""
    # Тест без обязательных полей
    invalid_data = {'content': 'Only content'}
    response = client.post(
        '/api/notes',
        data=json.dumps(invalid_data),
        content_type='application/json'
    )
    assert response.status_code == 400
    
    # Тест с пустым телом
    response = client.post(
        '/api/notes',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code == 400

def test_search_by_tag(client):
    """Тест поиска по тегам"""
    # Создаем заметку с тегом
    note_data = {
        'title': 'Tagged Note',
        'content': 'Content with tag',
        'tags': ['important', 'work']
    }
    client.post('/api/notes',
                data=json.dumps(note_data),
                content_type='application/json')
    
    # Ищем по тегу
    response = client.get('/api/notes/tag/work')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0

def test_nonexistent_endpoint(client):
    """Тест несуществующего эндпоинта"""
    response = client.get('/api/nonexistent')
    assert response.status_code == 404