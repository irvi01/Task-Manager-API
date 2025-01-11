import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Testa a resposta da página inicial."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Bem-vindo ao Gerenciador de Tarefas" in response.data

def test_create_task(client):
    """Testa a criação de uma nova tarefa."""
    response = client.post('/tasks', json={
        'title': 'Nova Tarefa',
        'description': 'Descrição da nova tarefa'
    })
    assert response.status_code == 201
    assert b"Tarefa criada com sucesso" in response.data

def test_get_tasks(client):
    """Testa a obtenção da lista de tarefas."""
    response = client.get('/tasks')
    assert response.status_code == 200
    assert b"tarefas" in response.data
