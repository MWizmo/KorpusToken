from app import app, db
from app.models import User
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app.forms import LoginForm, SignupForm
from flask_login import current_user, login_user, logout_user, login_required


@app.route('/')
@app.route('/home')
@login_required
def home():
    user = {'username': str(User.query.all())}
    return render_template('homepage.html', title='KorpusToken', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неправильный логин или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', tittle='Авторизация', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            login=form.login.data,
            tg_nickname=form.tg_nickname.data,
            username=form.tg_nickname.data,
            team=form.team.data,
            role=form.role.data,
            courses=form.courses.data,
            birthday=form.birthday.data,
            education=form.education.data,
            work_exp=form.work_exp.data,
            ses=form.sex.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', tittle='Регистрация', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
