import datetime

from app import app, db
from app.models import User, Questions, QuestionnaireInfo, Questionnaire, Membership, Teams
from flask import render_template, redirect, url_for, request
from werkzeug.urls import url_parse
from app.forms import LoginForm, SignupForm, QuestionnairePersonal
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
            return render_template('login.html', tittle='Авторизация', form=form, err=True)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Авторизация', form=form)


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
            # team=str(form.team.data),
            # role=str(form.role.data),
            courses=form.courses.data,
            birthday=form.birthday.data,
            education=form.education.data,
            work_exp=form.work_exp.data,
            sex=form.sex.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        user_team = Membership(user_id=User.query.filter_by(email=form.email.data).first().id,
                               team_id=Teams.query.filter_by(name=form.team.data).first().id,
                               role_id=int(form.role.data))
        db.session.add(user_team)
        db.session.commit()
        return redirect(url_for('login'))
    print(form.errors)
    return render_template('signup.html', title='Регистрация', form=form)


@app.route('/questionnaire_self', methods=['GET', 'POST'])
def questionnaire_self():
    if not current_user.is_authenticated:
        return redirect('login')

    form = QuestionnairePersonal()
    questions = Questions.query.filter_by(type=1)
    if form.validate_on_submit():
        q = Questionnaire(user_id=current_user.id,
                          team_id=Membership.query.filter_by(user_id=current_user.id).first().team_id,
                          date=datetime.datetime.today(),
                          type=1)
        db.session.add(q)
        db.session.commit()
        answs = [form.qst_personal_growth.data, form.qst_controllability.data,
                 form.qst_selfcontrol.data, form.qst_strategy.data]
        i = 0

        # ID СЕССИИ АНКЕТЫ (QUESTIONNAIRE_ID) ПЕРЕДАЕТСЯ НЕККОРЕКТНО

        for question in questions:
            answ = QuestionnaireInfo(question_id=question.id,
                                     questionnaire_id=Questionnaire.query.all()[-1].id,
                                     question_num=i+1,
                                     question_answ=answs[i])
            db.session.add(answ)
            i += 1
        db.session.commit()
        return redirect(url_for('home'))
    print(form.errors)
    return render_template('questionnaire_self.html', title='Личная анкета', form=form, q1=questions[0].text,
                           q2=questions[1].text, q3=questions[2].text, q4=questions[3].text)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
