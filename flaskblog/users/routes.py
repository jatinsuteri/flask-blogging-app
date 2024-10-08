from flask import Blueprint,redirect,render_template,flash,url_for,request,flash
from flask_login import current_user,login_required,logout_user,login_user
from flaskblog.models import User, Post
from flaskblog import db,bcrypt
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flaskblog.users.utils import save_picture, send_reset_email
users = Blueprint('users', __name__)

@users.route('/login', methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect('home')
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(url_for(next_page[1:])) if next_page else redirect(url_for('main.home'))    
        else:
            flash('Login Unsuccessful, check your username and password')
    return render_template('login.html', title='Login', form=form)


@users.route('/register',methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data , password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account Created, Please Login','success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/route')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods = ["GET" , "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account is Updated!" , "success")
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email    
    image_file = url_for('static' , filename = "profile_pics/" + current_user.image_file)
    return render_template('account.html', title = 'Account', image_file = image_file, form = form)


@users.route('/user/<string:username>') 
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author = user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html',user=user,posts=posts)


@users.route('/reset_password', methods = ['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect('home')
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        send_reset_email(user)
        flash('an email has been send with instructions to reset your password')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title = 'Reset Password', form = form)

@users.route('/reset_password/<token>', methods = ['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect('home')
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated!','success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title = "Reset Password", form = form)
    