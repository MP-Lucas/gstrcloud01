import json
import requests
from kafka import KafkaProducer
from flask import jsonify
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from . import db
from .models import User, Robot
from .forms import LoginForm, RegistrationForm, RobotForm

main = Blueprint('main', __name__)

# Cria um produtor Kafka
producer = KafkaProducer(
    bootstrap_servers=['broker:29092'],
    value_serializer=lambda m: json.dumps(m).encode('ascii'),
    api_version=(7,3,0)
)

@main.route('/home')
@main.route('/', methods=['GET'])
def home():
    return render_template('home.html')


# Rota para o login, realizando a validação do username e senha
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            producer.send('user-events', {'event': 'login', 'email':form.email.data})
            return redirect(url_for('main.manager'))
        flash('Email ou senha inválida', 'danger')
    return render_template('login.html', form=form)

# Registrar um novo usuário no sistema validando nao duplicidade de username e email
@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Nome de usuário já foi utilizado', 'warning')
            return render_template('register.html', form=form)

        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Endereço de e-mail já foi utilizado', 'warning')
            return render_template('register.html', form=form)

        user = User(email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Parabéns! Você agora está registrado!', 'success')
        producer.send('user-events', {'event': 'register', 'username': form.username.data, 'email':form.email.data})
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)

# Direciona à página para gerenciar os robôs
@main.route('/manager')
@login_required
def manager():
    robots = Robot.query.filter_by(user_id=current_user.id).all()
    return render_template('manager.html', robots=robots)

# Direciona à página para controlar o respectivo robô determinado pelo seu id(robot_id)
@main.route('/control-robot/<int:robot_id>')
@login_required
def control_robot(robot_id):
    robot = Robot.query.filter_by(id=robot_id, user_id=current_user.id).first_or_404()
    return render_template('control-robot.html', robot=robot)

# Comandos do robô
@main.route('/api-robot/<int:robot_id>/<string:command>', methods=['POST'])
@login_required
def api_robot(robot_id, command):
    print("CALLED")
    robot = Robot.query.filter_by(id=robot_id, user_id=current_user.id).first()
    if robot is None:
        return jsonify({"status": "error", "message": "Robot does not exist"}), 400
    
    robot_ip = robot.ip_address
    robot_port = robot.port

    commands = {
        'forward':'1',
        'backward':'2',
        'right':'3',
        'left':'4'
    }

    producer.send('robot-control', {'command':commands[command],'ip':robot_ip, 'robot_id':robot.robot_id, 'robot_password': robot.robot_password})

    return jsonify({"status": "success", "message": "Command executed successfully"}),200


# Deletar o robô conforme o id dele
@main.route('/delete-robot/<int:robot_id>', methods=['POST'])
@login_required
def delete_robot(robot_id):
    robot = Robot.query.filter_by(id=robot_id, user_id=current_user.id).first()
    if robot is None:
        flash('Robô especificado não foi encontrado', 'danger')
        return redirect(url_for('main.manager'))

    db.session.delete(robot)
    db.session.commit()

    # Enviar mensagem ao Kafka indicando que o robô foi deletado
    producer.send('robot-events', {
        'event': 'delete', 
        'robot-name':robot.name ,
        'robot-ip':robot.ip_address, 
        'robot-port':robot.port, 
        'user_id':current_user.id
    })
    
    flash('Robô deleteado com sucesso', 'success')
    return redirect(url_for('main.manager'))

# Registrar um novo robô 
@main.route('/register-robot', methods=['GET', 'POST'])
@login_required
def register_robot():
    form = RobotForm()
    if form.validate_on_submit():
        robot = Robot(name=form.name.data, ip_address=form.ip_address.data, port=form.port.data, user_id=current_user.id, robot_id=form.robot_id.data, robot_password=form.robot_password.data)
        db.session.add(robot)
        db.session.commit()
        
        # Enviar mensagem ao Kafka indicando que o robô foi registrado
        producer.send('robot-events', {
            'event': 'add', 
            'robot-name':form.name.data ,
            'robot-ip':form.ip_address.data, 
            'robot-port':form.port.data, 
            'user_id':current_user.id
        })

        flash('Robô registrado com sucesso!', 'success')
        return redirect(url_for('main.register_robot')) 
    return render_template('register-robot.html', form=form)

# Direciona à página de edição dos dados do respectivo robô determinado pelo seu id(robot_id)
@main.route('/edit-robot/<int:robot_id>', methods=['GET', 'POST'])
@login_required
def edit_robot(robot_id):
    robot = Robot.query.filter_by(id=robot_id, user_id=current_user.id).first_or_404()
    
    # Pré-carrega o formulário com os dados do robô
    form = RobotForm(obj=robot)  

    if form.validate_on_submit():
        robot.name = form.name.data
        robot.ip_address = form.ip_address.data
        robot.port = form.port.data
        robot.robot_id = form.robot_id.data
        robot.robot_password = form.robot_password.data
        db.session.commit()
        
        # Enviar mensagem ao Kafka indicando que o robô foi editado
        producer.send('robot-events', {
            'event': 'edit',
            'robot-id': robot.id,
            'robot-name': robot.name,
            'robot-ip': robot.ip_address,
            'robot-port': robot.port,
            'user-id': current_user.id
        })

        flash('Robô atualizado com sucesso!', 'success')
        return redirect(url_for('main.manager'))
    
    return render_template('register-robot.html', form=form, robot=robot)

# Deslogar do sistema
@main.route('/logout')
@login_required
def logout():

    # Enviar mensagem ao Kafka indicando que um usuário efetetuou log out
    producer.send('user-events', {
        'event': 'logout',
        'userid':current_user.id
        })
    
    logout_user()
    return redirect(url_for('main.home'))
