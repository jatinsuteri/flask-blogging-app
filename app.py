from flask import Flask, render_template,flash,url_for,redirect,request
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'jatinsuteri'

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
