from flask import request, jsonify, Blueprint
from app import db
from app.models import Task
from datetime import datetime
import jwt
from app.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from functools import wraps
from datetime import timedelta


api_blueprint = Blueprint('api', __name__)

# Listar todas as tarefas
@api_blueprint.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()  # Recupera todas as tarefas do banco de dados
    result = []
    for task in tasks:
        due_date = task.due_date
        if isinstance(due_date, datetime):
            due_date_str = due_date.isoformat()
        else:
            due_date_str = None
        result.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'due_date': due_date_str,
        })
    return jsonify([task.to_dict() for task in tasks])

# Criar uma nova tarefa
@api_blueprint.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    if not data.get("title"):
        return jsonify({"error": "Título é obrigatório"}), 400
    if not data.get("due_date"):
        return jsonify({"error": "Data de vencimento é obrigatória"}), 400
     
    due_date_str = data.get("due_date")
    if due_date_str:
        try:
            data["due_date"] = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Data inválida. Formato esperado: YYYY-MM-DD"}),
    else:
        data["due_date"] = None
    new_task = Task(
        title=data["title"],
        description=data.get("description"),
        status=data.get("status", "pending"),
        due_date=data.get("due_date"),
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

# Obter detalhes de uma tarefa
@api_blueprint.route("/tasks/<int:id>", methods=["GET"])
def get_task(id):
    task = Task.query.get_or_404(id)
    return jsonify(task.to_dict())

# Atualizar uma tarefa
@api_blueprint.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    task = Task.query.get_or_404(id)
    if task is None:
        return jsonify({"error": "Tarefa não encontrada"}), 404
    data = request.get_json()

    if not data.get("title"):
        return jsonify({"error": "Título é obrigatório"}), 400
    if not data.get("due_date"):    
        return jsonify({"error": "Data de vencimento é obrigatória"}), 400
    
    task.title = data["title"]
    task.description = data.get("description")
    task.status = data.get("status")
    due_date_str = data.get("due_date")
    if due_date_str:
        try:
            task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Data inválida. Formato esperado: YYYY-MM-DD"}), 400
    db.session.commit()
    return jsonify(task.to_dict())

# Deletar uma tarefa
@api_blueprint.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return "", 204


# Autenticação
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # "Bearer <token>"

        if not token:
            return jsonify({'message': 'Token de acesso é necessário!'}), 401

        try:
            # Verifica o token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['id']).first()  # Busca o usuário
        except Exception as e:
            return jsonify({'message': 'Token inválido!', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)

    return decorated_function

#Rota de registro
@api_blueprint.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data.get("username") or not data.get("password"):
        return jsonify({"message": "Username e password são obrigatórios!"}), 400

    hashed_password = generate_password_hash(data["password"], method="pbkdf2:sha256")

    # Criação de um novo usuário
    new_user = User(username=data["username"], password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Usuário criado com sucesso!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erro ao criar usuário", "message": str(e)}), 500

#Rota de login
@api_blueprint.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    # Busca o usuário pelo nome de usuário
    user = User.query.filter_by(username=data.get("username")).first()

    # Validação do usuário e senha
    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"message": "Credenciais inválidas!"}), 401

    # Gera um token JWT
    try:
        expiration_time = current_app.config.get('JWT_EXPIRATION_DELTA', timedelta(hours=1))
        if isinstance(expiration_time, timedelta):
            expiration_time = datetime.utcnow() + expiration_time
        else:
            raise ValueError("JWT_EXPIRATION_DELTA deve ser um timedelta válido")

        token = jwt.encode(
            {'id': user.id, 'exp': expiration_time},
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return jsonify({'token': token}), 200
    except Exception as e:
        return jsonify({"message": "Erro ao gerar o token", "error": str(e)}), 500


#Rota protegida com token
@api_blueprint.route("/protected", methods=["GET"])
@token_required
def protected_route(current_user):
    return jsonify({"message": f"Olá, {current_user.username}! Você tem acesso à rota protegida."})
