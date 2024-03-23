from flask import render_template,flash,url_for,redirect,request
from flaskblog import app, db, bcrypt
from flaskblog.forms import LoginForm,RegistrationForm, UpdateAccountForm
from flaskblog.models import User, Post
from flask_login import login_user,current_user,logout_user,login_required

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
    if current_user.is_authenticated:
        return redirect('home')
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(url_for(next_page[1:])) if next_page else redirect(url_for('home'))    
        else:
            flash('Login Unsuccessful, check your username and password')
    return render_template('login.html', title='Login', form=form)

@app.route('/register',methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data , password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account Created, Please Login','success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/route')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods = ["GET" , "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account is Updated!" , "success")
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email    
    image_file = url_for('static' , filename = "profile_pics/" + current_user.image_file)
    return render_template('account.html', title = 'Account', image_file = image_file, form = form)

