from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy

# Configurações
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_manager.db'

db = SQLAlchemy(app)


# Tabelas
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    tasks = db.relationship('Task', backref='owner', lazy=True)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, title, description, user_id):
        self.title = title
        self.description = description
        self.user_id = user_id


# Inicia o banco de dados
with app.app_context():
    db.create_all()


# Rotas
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    # Recolhe os valores inseridos
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # Verifica se já existe um nome e email cadastrados
    verify_email = User.query.filter_by(email=email).first()
    verify_name = User.query.filter_by(username=username).first()
    if verify_email or verify_name:
        flash('Este nome ou email já está cadastrado', 'warning')
        return redirect(url_for('index'))

    # Registra o usuário no banco de dados
    object_user = User(username, email, password)
    db.session.add(object_user)
    db.session.commit()

    flash('Sua conta foi criada com sucesso!', 'success')
    return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login():
    # Recolhe os dados dos formulários
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email, password=password).first()

    # Verifica se existe um email e senha cadastrados
    if user and password:
        session['user_id'] = user.id
        flash(f'Seja Bem-Vindo {user.username}!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Algo deu errado. Verifique se o email ou senha estão corretos', 'warning')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    # Verifica se existe uma sessão
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']

    # Recolhe todas as tarefas do usuário
    tasks = Task.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', tasks=tasks)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você se desconectou com sucesso!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
