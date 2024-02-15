from flask_app import app
from flask import render_template, redirect, flash, session, request
from flask_app.models.admin import Admin
from flask_app.models.trainer import Trainer
from flask_bcrypt import Bcrypt

from flask_app.models.member import Member
from flask_app.models.trainer import Trainer

bcrypt = Bcrypt(app)


@app.errorhandler(404) 
def invalid_route(e): 
    return render_template('404.html')

@app.route('/login')
def loginPage():
    if 'user_id' in session:
        return redirect('/')
    return render_template('login.html')


@app.route('/login/trainer', methods = ['POST'])
def loginTrainer():
    if 'user_id' in session:
        return redirect('/')
    if not Trainer.validate_user(request.form):
        return redirect(request.referrer)
    user = Trainer.get_trainer_by_email(request.form)
    if not user:
        flash('This email doesnt exist', 'emailLogin')
        return redirect(request.referrer)
    if not bcrypt.check_password_hash(user['password'], request.form['password']):
        flash('Incorrect password', 'passwordLogin')
        return redirect(request.referrer)
    
    session['user_id']= user['id']
    return redirect('/')
