from flask import Flask, request, session
from flask import render_template, redirect, url_for
from function import get_user
import auth
import db
import settings
import re
import json
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY
email_service = auth.init_service(client_secrets_file='data/client_secret_620369742470-9kv0kkroc2n54llap78f8uj8h7850ed7.apps.googleusercontent.com.json')

@app.route('/')
def home_page():
    return render_template('main/home.html', user=get_user())

@app.route('/catalog')
def catalog():
    return render_template('main/catalog.html', user=get_user())

@app.route('/login')
def login():
    if session.get('logged_in'): return redirect(url_for('profile'))

    message = request.args.get('message')
    error_message = None
    if message:
        message = json.loads(message)
        error_message = message['msg'] if message['error'] else None

    return render_template('main/login.html', error_message=error_message, user=get_user())

@app.route('/signup')
def signup():
    if session.get('logged_in'): return redirect(url_for('profile'))

    message = request.args.get('message')
    error_message = None
    if message:
        message = json.loads(message)
        error_message = message['msg'] if message['error'] else None

    return render_template('main/signup.html', error_message=error_message, user=get_user())

@app.route('/auth', methods=['POST', 'GET'])
def verify_email():
    if session.get('logged_in'): return redirect(url_for('profile'))
    
    elif request.method == 'POST':
        first_name = request.form.get('fist-name')
        last_name = request.form.get('last-name')
        email = request.form.get('email')
        save_phone_number = phone_number = request.form.get('phone-number')
        birthday = request.form.get('date')
        privacy_policy = request.form.get('policy')
        code = request.form.get('verify-code')

        auth_type = 'signup' if first_name and last_name and email and phone_number and birthday and privacy_policy else 'login'

        if not phone_number: phone_number = session.get('phone_number')
        if not email: email = session.get('email')


        if auth_type == 'signup':
            phone_number = ''.join(''.join(''.join(phone_number.split()).split('(')).split(')'))
            pattern = r'^\+373(6|7)\d{7}$'
            if re.match(pattern, phone_number) is None:
                message = {
                    'error': True,
                    'msg': 'Incorrect phone number!'
                }
                return redirect(url_for('login', message=json.dumps(message)) if auth_type == 'login' else url_for('signup', message=json.dumps(message)))

        user_by_phone: tuple[Any, ...] | None = db.get_user_by_phone(value=phone_number)
        user_by_email = db.get_user_by_email(value=email)
        if auth_type == 'signup':
            if (user_by_phone and user_by_email and user_by_phone[0] != user_by_email[0]) or user_by_phone or user_by_email:
                message = {
                    'error': True,
                    'msg': 'An account with this phone number or email address already exists!'
                }
                return redirect(url_for('login', message=json.dumps(message)) if auth_type == 'login' else url_for('signup', message=json.dumps(message)))
        elif auth_type == 'login' and not user_by_email and not code:
            message = {
                'error': True,
                'msg': 'This email is not in the database! You should register!'
            }
            return redirect(url_for('login', message=json.dumps(message)) if auth_type == 'login' else url_for('signup', message=json.dumps(message)))
        
        if auth_type == 'login' and user_by_email:
            phone_number = user_by_email[4]

        if code is None and email:
            session['first_name'] = first_name
            session['last_name'] = last_name
            session['email'] = email
            session['phone_number'] = phone_number
            session['birthday'] = birthday
            session['privacy_policy'] = privacy_policy
            session['auth_type'] = auth_type
            if user_by_phone: session['id'] = user_by_phone[0]

            try:
                # Send verification code
                auth_code = auth.generate_auth_code()
                msg = auth.generate_verification_message(
                    to=session['email'],
                    content={
                        'code': auth_code
                    }
                )
                status = auth.send_email(
                    service=email_service,
                    message=msg
                )

                if status != 0: raise Exception('Internal error')

                session['auth_code'] = auth_code
                session['auth_code_created_at'] = datetime.utcnow().isoformat()
            except Exception as e:
                message = {
                    'error': True,
                    'msg': 'Internal Error!'
                }
                return redirect(url_for('login', message=json.dumps(message)) if auth_type == 'login' else url_for('signup', message=json.dumps(message)))
        else:
            try:  
                # Verify verification code
                auth_code = session.get('auth_code')
                auth_code_created_at = datetime.fromisoformat(session.get('auth_code_created_at'))

                if datetime.utcnow() - auth_code_created_at > timedelta(minutes=1):
                    message = {
                        'error': True,
                        'msg': 'This code has already expired!'
                    }
                    return redirect(url_for('login', message=json.dumps(message)) if auth_type == 'login' else url_for('signup', message=json.dumps(message)))

                if auth_code and auth_code == code and ((session.get('auth_type') == 'login' and user_by_email) or session.get('auth_type') == 'signup'):  
                    if not user_by_email:
                        created_user = db.create_new_user(
                            first_name=session.get('first_name'),
                            last_name=session.get('last_name'),
                            email=session.get('email'),
                            phone_number=session.get('phone_number'),
                            birth_date=session.get('birthday'),
                            accepted_privacy_policy=session.get('privacy_policy')
                        )

                        if created_user is False:
                            session.clear()
                            message = {
                                'error': True,
                                'msg': 'The account could not be created!'
                            }
                            return redirect(url_for('signup', message=json.dumps(message)))
                        
                        user_by_email = db.get_user_by_email(value=email)
                        if user_by_email: session['id'] = user_by_email[0]
                
                    user_by_email = db.get_user_by_email(value=email)

                    session['id'] = user_by_email[0]
                    session['first_name'] = user_by_email[1]
                    session['last_name'] = user_by_email[2]
                    session['email'] = user_by_email[3]
                    session['phone_number'] = user_by_email[4]
                    session['birthday'] = user_by_email[5]
                    session['privacy_policy'] = user_by_email[6]
                    session['logged_in'] = True
                    return redirect(url_for('home_page'))
                
                else:
                    return render_template('main/verify_number.html', error_message='Invalid code!', user=get_user())

            except Exception as e:
                message = {
                    'error': True,
                    'msg': 'Internal Error!'
                }
                return redirect(url_for('login', message=json.dumps(message)) if auth_type == 'login' else url_for('signup', message=json.dumps(message)))

        return render_template('main/verify_number.html', user=get_user())
    else:
        return redirect(url_for('home_page'))
    
def verify_number():
    if session.get('logged_in'): return redirect(url_for('profile'))
    
    elif request.method == 'POST':
        first_name = request.form.get('fist-name')
        last_name = request.form.get('last-name')
        email = request.form.get('email')
        save_phone_number = phone_number = request.form.get('phone-number')
        birthday = request.form.get('date')
        privacy_policy = request.form.get('policy')
        code = request.form.get('verify-code')

        auth_type = 'signup' if first_name and last_name and email and phone_number and birthday and privacy_policy else 'login'

        if not phone_number: phone_number = session.get('phone_number')

        phone_number = ''.join(''.join(''.join(phone_number.split()).split('(')).split(')'))
        pattern = r'^\+373(6|7)\d{7}$'
        if re.match(pattern, phone_number) is None:
            message = {
                'error': True,
                'msg': 'Incorrect phone number!'
            }
            return redirect(url_for('login', message=json.dumps(message)) if auth_type == 'login' else url_for('signup', message=json.dumps(message)))

        user_by_phone: tuple[Any, ...] | None = db.get_user_by_phone(value=phone_number)
        if auth_type == 'signup':
            user_by_email = db.get_user_by_email(value=email)

            if (user_by_phone and user_by_email and user_by_phone[0] != user_by_email[0]) or user_by_phone or user_by_email:
                message = {
                    'error': True,
                    'msg': 'An account with this phone number or email address already exists!'
                }
                return redirect(url_for('login', message=json.dumps(message)) if auth_type == 'login' else url_for('signup', message=json.dumps(message)))
        elif auth_type == 'login' and not user_by_phone and not code:
            message = {
                'error': True,
                'msg': 'This number is not in the database! You should register!'
            }
            return redirect(url_for('login', message=json.dumps(message)) if auth_type == 'login' else url_for('signup', message=json.dumps(message)))

        if code is None and save_phone_number:
            session['first_name'] = first_name
            session['last_name'] = last_name
            session['email'] = email
            session['phone_number'] = phone_number
            session['birthday'] = birthday
            session['privacy_policy'] = privacy_policy
            session['auth_type'] = auth_type
            if user_by_phone: session['id'] = user_by_phone[0]

            try:
                verification = settings.client.verify \
                    .services(settings.VERIFY_SERVICE_SID) \
                    .verifications \
                    .create(to=session.get('phone_number'), channel='sms')
            except Exception as e:
                message = {
                    'error': True,
                    'msg': 'Internal Error!'
                }
                return redirect(url_for('login', message=json.dumps(message)) if auth_type == 'login' else url_for('signup', message=json.dumps(message)))
        else:
            try:  
                verification_check = settings.client.verify \
                    .services(settings.VERIFY_SERVICE_SID) \
                    .verification_checks \
                    .create(to=session.get('phone_number'), code=code)

                if verification_check.status == 'approved' and ((session.get('auth_type') == 'login' and user_by_phone) or session.get('auth_type') == 'signup'):  
                #if True and ((session.get('auth_type') == 'login' and user_by_phone) or session.get('auth_type') == 'signup'): 
                    if not user_by_phone:
                        created_user = db.create_new_user(
                            first_name=session.get('first_name'),
                            last_name=session.get('last_name'),
                            email=session.get('email'),
                            phone_number=session.get('phone_number'),
                            birth_date=session.get('birthday'),
                            accepted_privacy_policy=session.get('privacy_policy')
                        )

                        if created_user is False:
                            session.clear()
                            message = {
                                'error': True,
                                'msg': 'The account could not be created!'
                            }
                            return redirect(url_for('signup', message=json.dumps(message)))
                        
                        user_by_phone = db.get_user_by_phone(value=phone_number)
                        if user_by_phone: session['id'] = user_by_phone[0]
                
                    session['id'] = user_by_phone[0]
                    session['first_name'] = user_by_phone[1]
                    session['last_name'] = user_by_phone[2]
                    session['email'] = user_by_phone[3]
                    session['phone_number'] = user_by_phone[4]
                    session['birthday'] = user_by_phone[5]
                    session['privacy_policy'] = user_by_phone[6]
                    session['logged_in'] = True
                    return redirect(url_for('home_page'))
                
                else:
                    return render_template('main/verify_number.html', error_message='Invalid code!', user=get_user())

            except Exception as e:
                message = {
                    'error': True,
                    'msg': 'Internal Error!'
                }
                return redirect(url_for('login', message=json.dumps(message)) if auth_type == 'login' else url_for('signup', message=json.dumps(message)))

        return render_template('main/verify_number.html', user=get_user())
    else:
        return redirect(url_for('home_page'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home_page'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not get_user()['connected']:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        first_name = request.form.get('fist-name')
        last_name = request.form.get('last-name')
        email = request.form.get('email')
        id = session.get('id')

        session['first_name'] = first_name
        session['last_name'] = last_name
        session['email'] = email

        update_user = db.update_user_by_id(
            first_name=first_name,
            last_name=last_name,
            email=email,
            id=id
        )

        if not update_user:
            return render_template('main/profile.html', error_message='You were not allowed to edit your account details!', user=get_user())

    return render_template('main/profile.html', user=get_user())
