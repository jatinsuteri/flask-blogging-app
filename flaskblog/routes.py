from flask import render_template,flash,url_for,redirect,request,abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import LoginForm,PostForm,RegistrationForm, UpdateAccountForm,RequestResetForm,ResetPasswordForm
from flaskblog.models import User, Post
from flask_login import login_user,current_user,logout_user,login_required
import secrets,os
from PIL import Image
from flask_mail import Message



@app.route('/')
@app.route('/home') 
def home():
    page = request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html',page = page,posts=posts)
    

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


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.static_folder, 'profile_pics', picture_fn)
    
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn


@app.route("/account", methods = ["GET" , "POST"])
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

@app.route("/post/new", methods = ['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content=form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('your post has been created!','success')
        return redirect(url_for('home'))
    return render_template('create_post.html',form = form,
                           legend = 'Update Post', title = 'New Post')


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title = post.title, post = post)


@app.route('/post/<int:post_id>/update', methods = ['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('your post has been updated!' , 'success')
        return redirect(url_for("post", post_id = post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html',form = form, legend = 'Update Post',title = 'Update Post')
    

@app.route('/post/<int:post_id>/delete', methods = ['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('your post has been deleted!' , 'success')
    return redirect(url_for('home'))

@app.route('/user/<string:username>') 
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author = user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html',user=user,posts=posts)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password reset request', sender='jatinsuteri@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, ignore it.
'''
    mail.send(msg)

@app.route('/reset_password', methods = ['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect('home')
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        send_reset_email(user)
        flash('an email has been send with instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title = 'Reset Password', form = form)

@app.route('/reset_password/<token>', methods = ['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect('home')
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated!','success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title = "Reset Password", form = form)
    