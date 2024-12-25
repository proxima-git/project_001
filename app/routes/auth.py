from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import login_user, logout_user
from ..forms import SignupForm, LoginForm
from ..extensions import db, bcrypt
from ..models.auth import User
from ..functions import save_picture


auth = Blueprint('auth', __name__)

@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        avatar_filename = save_picture(form.avatar.data)
        user = User(name=form.name.data,
                    login=form.login.data, 
                    password=hashed_password, 
                    avatar=avatar_filename)
        try:
            db.session.add(user)
            db.session.commit()
            flash(f'You have successfully registered, {form.login.data}!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(str(e))
            flash(f'Registration failed!', 'danger')
    return render_template('/signup.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'You are successfully authorized!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash(f'Authorization failed - Please check your login and password.', 'danger')
    return render_template('/login.html', form=form)

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main.home'))
