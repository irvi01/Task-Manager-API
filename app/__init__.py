import os
from flask import Flask
from .models import db
from .routes import api_blueprint
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    # Inicializa o banco de dados com a instância do app
    db.init_app(app)

    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "091020@Dy")  # Use um valor forte em produção
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=1)  # Expiração do token

    # Registra o blueprint das rotas
    app.register_blueprint(api_blueprint)
    
    
    
    return app
