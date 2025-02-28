import time
import json
from kafka import KafkaProducer
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from config import Config

# Variável relacionada ao db
db = SQLAlchemy()

# Objeto responsável por gerenciar o login
login_manager = LoginManager()

# Objeto responsável pela estilização da página
bootstrap = Bootstrap()

# Tenta uma conexão com o Kafka
def wait_for_kafka(broker_url, timeout=60):
    start_time = time.time()
    connected = False
    while not connected and (time.time() - start_time) < timeout:
        try:
            producer = KafkaProducer(bootstrap_servers=[broker_url], api_version=(7,3,0))          
            producer.close()
            connected = True
        except Exception as e:
            print(f"Waiting for Kafka at {broker_url} to be available...")
            time.sleep(5) 
    return connected

# Cria uma instância de app com as configurações necessárias
def create_app():

    # Cria instância de app
    app = Flask(__name__, instance_relative_config=False, instance_path=None)
    app.config.from_object(Config)

    # Espera se conectar com o Kafka
    wait_for_kafka('broker:29092')
    producer = KafkaProducer(
        bootstrap_servers=['broker:29092'],
        value_serializer=lambda m: json.dumps(m).encode('ascii'),
        api_version=(7,3,0)
    )

    # Cria tópicos kafka enviando uma mensagem de inicialização
    producer.send('robot-control', {'init':'greetings'})
    producer.send('user-events', {'init':'greetings'})
    producer.send('robot-events', {'init':'greetings'})
    producer.close()

    # Inicia o banco de dados
    db.init_app(app)

    # Inicia o gerencidaor de login
    login_manager.init_app(app)

    # Inicia o objeto de estilização
    bootstrap.init_app(app)

    # Indica a página de login
    login_manager.login_view = 'main.login'

    # Coloca mensagens amarelas por padrão
    login_manager.login_message_category = 'warning'

    migrate = Migrate(app, db)
    from .models import User

    # Mantém o track do id do usuário    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
