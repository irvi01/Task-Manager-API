class Config:
    SECRET_KEY = '091020@Dy' # Chave secreta para proteger a aplicação
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tasks.db'  # Usando SQLite para testes locais
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Desabilita o track modifications do SQLAlchemy
