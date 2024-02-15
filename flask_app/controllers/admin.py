from flask_app import app
from flask import render_template, redirect, flash, session, request
from flask_bcrypt import Bcrypt

from flask_app.models.member import Member
from flask_app.models.admin import Admin
from flask_app.models.trainer import Trainer

bcrypt = Bcrypt(app)




@app.route('/login/admin', methods = ['POST'])
def loginAdmin():
    if 'user_id' in session:
        return redirect('/')
    if not Admin.validate_user(request.form):
        return redirect(request.referrer)
    user = Admin.get_admin_by_email(request.form)
    if not user:
        flash('This email doesnt exist', 'emailLogin')
        return redirect(request.referrer)
    if not bcrypt.check_password_hash(user['password'], request.form['password']):
        flash('Incorrect password', 'passwordLogin')
        return redirect(request.referrer)
    
    session['user_id']= user['id']
    return redirect('/admin')


@app.route('/loginPage/admin')
def loginPageAdmin():
    if 'user_id' in session:
        return redirect('/')
    return render_template('adminLogin.html')

@app.route('/admin')
def adminPage():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = Admin.get_admin_by_id(data)
    if user and user['role'] == 'admin':
        return render_template('adminPage.html', loggedUser = user , trainers = Trainer.get_all())
    return redirect('/logout')

@app.route('/trainer/new')
def newTrainer():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = Admin.get_admin_by_id(data)
    if user and user['role'] == 'admin':
        return render_template('registerTrainer.html')
    return redirect('/logout')
    



@app.route('/register/trainer', methods = ['POST'])
def registerTrainer():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        if not Trainer.validate_userRegister(request.form):
            return redirect(request.referrer)
        user = Trainer.get_trainer_by_email(request.form)
        if user:
            flash('This account already exists', 'emailRegister')
            return redirect(request.referrer)
        data = {
            'firstName': request.form['firstName'],
            'lastName': request.form['lastName'],
            'email': request.form['email'],
            'password': bcrypt.generate_password_hash(request.form['password']),
            'phone': request.form['phone'],
            'speciality': request.form['speciality']
        }
        Trainer.create(data)
        flash('Trajneri krijuar me sukses', 'succesRegister')
        return redirect(request.referrer)
    return redirect('/')