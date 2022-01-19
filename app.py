from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config.config import DevelopmentConfig
from flask import render_template, request, url_for, flash, g
from flask import session
from flask import send_from_directory
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import datetime

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
db = SQLAlchemy(app)

### MODELO

class User(db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(40),unique=True)
    password = db.Column(db.String(66))
    create_date = db.Column(db.DateTime,default=datetime.datetime.now)
    
    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = self.create_password(password)
    
    def create_password(self,password):
        return generate_password_hash(password)
    def verify_password(self,password):
        return check_password_hash(self.password, password)

### FIN MODELO

@app.before_request
def before_login():
    g.user = session.get('email') 
    if g.user is None and request.endpoint in ['dashboard','logout']:
        return redirect(url_for('index'))
    elif g.user is not None and request.endpoint in ['login','register']:
        return redirect(url_for('dashboard'))
        
@app.after_request
def after_login(response):
    return response


### ROUTES
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user is not None and user.verify_password(password):
            session['email'] = email
            # flash(f'Usuario {user.username} logeado correctamente')
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    if g.user:
        session.pop('email')
    return redirect(url_for('index'))

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        userName = request.form['username']
        email = request.form['email']
        password = request.form['password']
        V_user = User.query.filter_by(email=email).first()
        if V_user is None:
            newUser = User(userName,email,password)
            db.session.add(newUser)
            db.session.commit()
            session['email'] = email
            # flash(f'usuario {email} creado')
            return redirect(url_for('dashboard'))
        # else:
        #     flash('El usuario ya existe')
    return render_template('login.html')

@app.route('/static/video/<namevideo>')
def directory(namevideo):
    return send_from_directory('static/video',namevideo)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

### END ROUTE

if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run()