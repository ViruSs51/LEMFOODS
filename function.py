from flask import session
import db


def get_user():
    return {
        'id': session.get('id'),
        'first_name': session.get('first_name'),
        'last_name': session.get('last_name'),
        'email': session.get('email'),
        'phone_number': session.get('phone_number'),
        'birth_date': session.get('birthday'),
        'connected': session.get('logged_in')
    }

def get_products():
    categories = db.get_categories()
    