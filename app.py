from flask import Flask, render_template,flash,url_for,redirect,request
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' 
app.config['SECRET_KEY'] = 'jatinsuteri'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    image_file = db.Column(db.String(20), nullable = False, default = 'default.jpg')
    password = db.Column(db.String(60), nullable = False)
    posts = db.relationship('Post', backref = 'author', lazy = True)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}','{self.image_file}')"
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Post('{self.title}', '{self.content}')"


posts = [
    {
        'author': "jatinsuteri",
        'title': 'blog post 1',
        'content' : 'first blog post',
        'date_posted': '12 july, 2003'       
    },
    {
        'author': "yash suteri",
        'title': 'blog post 2',
        'content' : 'second blog post',
        'date_posted': '14 july, 2003'  
    }
]

@app.route('/')
@app.route('/home')  # Corrected route decorator
def home():
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html', title="About")

@app.route('/login', methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Logged In','success')
        return redirect('home')
    elif request.method == "POST":
        flash('Login Unsuccessful, please check username and password')
    return render_template('login.html', title='Login', form=form)

@app.route('/register',methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'account created for {form.username.data}!','success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

if __name__ == "__main__":
    app.run(debug=True)
