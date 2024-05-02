import os, secrets
from PIL import Image
from flask import url_for
from flaskblog import mail
from flask import current_app
from flask_mail import Message


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.static_folder, 'profile_pics', picture_fn)
    
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password reset request', sender='jatinsuteri@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request, ignore it.
'''
    mail.send(msg)