import math
import random
from flask_app import app
from flask import render_template, redirect, flash, session, request, url_for
from flask_bcrypt import Bcrypt

from flask_app.models.member import Member
bcrypt = Bcrypt(app)

import paypalrestsdk
ADMINEMAIL = '3ndi.mimini@gmail.com'
PASSWORD = "cokjpzxoznoeyvww"

from datetime import datetime
from urllib.parse import unquote
UPLOAD_FOLDER = 'flask_app/static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import os
from werkzeug.exceptions import RequestEntityTooLarge

from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from werkzeug.exceptions import HTTPException, NotFound
import urllib.parse

import smtplib


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if 'user_id' in session:
        data = {
            'id': session['user_id']
        }
        user = Member.get_member_by_id(data)
        if user['isVerified'] == 0:
            return redirect('/verify/account')
        return redirect('/dashboard')
    return redirect('/logout')
@app.route('/verify/account')
def verifyAccount():
    if 'user_id' in session:
        data = {
            'id': session['user_id']
        }
        user = Member.get_member_by_id(data)
        if user['isVerified'] == 0:
            return render_template('verifyAccount.html')
        
    return redirect('/')

@app.route('/verify/account', methods = ['POST'])
def confirmAccountVerification():
    if 'user_id' in session:
        data = {
            'id': session['user_id']
        }
        user = Member.get_member_by_id(data)
        if user['verificationCode'] != request.form['verificationCode']:
            flash('Incorrect verification code', 'verificationCode')
            return redirect(request.referrer)
        Member.approve(data)
    return redirect('/')




@app.route('/register')
def registerPage():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('register.html')


@app.route('/register', methods = ['POST'])
def registerMember():
    if 'user_id' in session:
        return redirect('/')
    if not Member.validate_userRegister(request.form):
        return redirect(request.referrer)
    user = Member.get_member_by_email(request.form)
    if user:
        flash('This account already exists', 'emailRegister')
        return redirect(request.referrer)
    

    string = '0123456789ABCDEFGHIJKELNOPKQSTUV'
    vCode = ""
    length = len(string)
    for i in range(8) :
        vCode += string[math.floor(random.random() * length)]
    verificationCode = vCode

    # line- i know for sure that my validate_user was true. User had all the required info
    data = {
        'firstName': request.form['firstName'],
        'lastName': request.form['lastName'],
        'email': request.form['email'],
        'password': bcrypt.generate_password_hash(request.form['password']),
        'verificationCode': verificationCode
    }
    session['user_id'] = Member.create(data)

    LOGIN = ADMINEMAIL
    TOADDRS  = request.form['email']
    SENDER = ADMINEMAIL
    SUBJECT = 'Verify Your Account'
    msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
        % ((SENDER), "".join(TOADDRS), SUBJECT) )
    msg += f'Use this verification code to activate your account: {verificationCode}'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.login(LOGIN, PASSWORD)
    server.sendmail(SENDER, TOADDRS, msg)
    server.quit()

    
    return redirect('/')



@app.route('/login/member', methods = ['POST'])
def loginMember():
    if 'user_id' in session:
        return redirect('/')
    if not Member.validate_user(request.form):
        return redirect(request.referrer)
    user = Member.get_member_by_email(request.form)
    if not user:
        flash('This email doesnt exist', 'emailLogin')
        return redirect(request.referrer)
    if not bcrypt.check_password_hash(user['password'], request.form['password']):
        flash('Incorrect password', 'passwordLogin')
        return redirect(request.referrer)
    
    session['user_id']= user['id']
    return redirect('/')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = Member.get_member_by_id(data)
    if user['isVerified'] == 0:
        return redirect('/verify/account')
    return render_template('profile.html', loggedUser = user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/update/profile/pic', methods = ['POST'])
def updateProfilePice():
    if 'user_id' not in session:
        return redirect('/')
    if 'profilePic' not in request.files:
        flash('Please upload an image', 'profilePic')
        return redirect(request.referrer)
    profile = request.files['profilePic']
    if not allowed_file(profile.filename):
        flash('The file should be in png, jpg or jpeg format!', 'profilePic')
        return redirect(request.referrer)
    if profile and allowed_file(profile.filename):
        filename1 = secure_filename(profile.filename)
        time = datetime.now().strftime("%d%m%Y%S%f")
        time += filename1
        filename1 = time
        profile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
        data = {
            'profilePic': filename1,
            'id': session['user_id']
        }
        Member.update_profile_pic(data)
        return redirect(request.referrer)
    return redirect('/')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = Member.get_member_by_id(data)
    if user['isVerified'] == 0:
        return redirect('/verify/account')
    return render_template('dashboard.html', loggedUser = Member.get_member_by_id(data), pagesat = Member.get_allUserPayments(data))


@app.route('/checkout/paypal')
def checkoutPaypal():
    if 'user_id' not in session:
            return redirect('/')
    cmimi = 100
    ora = 2
    targa = 'AA123AA'
    totalPrice = round(cmimi * ora)

    try:
        paypalrestsdk.configure({
            "mode": "sandbox", # Change this to "live" when you're ready to go live
            "client_id": "AYckYn5asNG7rR9A2gycCw-N2Du3GXH4ytNfU5ueLeYKaUwjKFL-aZMu3owCwfs_D1fydp2W-HSVieZ0",
            "client_secret": "EJu8H94UNn6b2Xigp26rf1pIs6NW-WrweGw-RkboWLUjWfHK2m46qrFObh_rL_HPSwvfipNyFoYdoa3K"
        })

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": totalPrice,
                    "currency": "USD"  # Adjust based on your currency
                },
                "description": f"Pagese per parkim per makinen me targe {targa} per {ora} orë!"
            }],
            "redirect_urls": {
                "return_url": url_for('paymentSuccess', _external=True, totalPrice=totalPrice),
                "cancel_url": "http://example.com/cancel"
            }
        })

        if payment.create():
            approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
            return redirect(approval_url)
        else:
            flash('Something went wrong with your payment', 'creditCardDetails')
            return redirect(request.referrer)
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'creditCardDetails')
        return redirect(request.referrer)






@app.route("/success", methods=["GET"])
def paymentSuccess():
    payment_id = request.args.get('paymentId', '')
    payer_id = request.args.get('PayerID', '')
    try:
        paypalrestsdk.configure({
            "mode": "sandbox", # Change this to "live" when you're ready to go live
            "client_id": "AYckYn5asNG7rR9A2gycCw-N2Du3GXH4ytNfU5ueLeYKaUwjKFL-aZMu3owCwfs_D1fydp2W-HSVieZ0",
            "client_secret": "EJu8H94UNn6b2Xigp26rf1pIs6NW-WrweGw-RkboWLUjWfHK2m46qrFObh_rL_HPSwvfipNyFoYdoa3K"
        })
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            
            
            ammount = request.args.get('totalPrice')
            status = 'Paid'
            member_id = session['user_id']
            data = {
                'ammount': ammount,
                'status': status,
                'member_id': member_id
            }
            Member.createPayment(data)
           
            flash('Your payment was successful!', 'paymentSuccessful')
            return redirect('/dashboard')
        else:
            flash('Something went wrong with your payment', 'paymentNotSuccessful')
            return redirect('/')
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'paymentNotSuccessful')
        return redirect('/dashboard')


@app.route("/cancel", methods=["GET"])
def paymentCancel():
    flash('Payment was canceled', 'paymentCanceled')
    return redirect('/dashboard')

