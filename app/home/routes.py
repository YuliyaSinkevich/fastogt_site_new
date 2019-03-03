from flask import render_template, request, redirect, url_for, flash, session
from flask_mail import Message
from flask_babel import gettext

from werkzeug.security import generate_password_hash, check_password_hash

from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from app import app, mail, babel
import app.utils as utils
from app.home import home
import app.constants as constants

from .forms import SignupForm, SigninForm, ContactForm

CONFIRM_LINK_TTL = 3600
SALT_LINK = 'email-confirm'

confirm_link_generator = URLSafeTimedSerializer(app.config['SECRET_KEY'])


def flash_success(text: str):
    flash(text, 'success')


def flash_error(text: str):
    flash(text, 'danger')


def send_email(email: str, subject: str, message: str):
    config = app.config['PUBLIC_CONFIG']
    msg = Message(subject, recipients=[config['support']['contact_email']])
    msg.body = 'From: {0} <{0}> {1}'.format(email, message)
    mail.send(msg)


# routes

@home.route('/', methods=['POST', 'GET'])
def start():
    languages = constants.AVAILABLE_LOCALES_PAIRS
    return render_template('index.html', languages=languages)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if request.method == 'POST':
        if not form.validate_on_submit():
            flash('All fields are required.')
            return render_template('contact.html', form=form)

        send_email(form.email.data, form.subject.data, form.message.data)
        return render_template('contact.html', success=True)

    elif request.method == 'GET':
        return render_template('contact.html', form=form)


@home.route('/language/<language>')
def set_language(language=constants.DEFAULT_LOCALE):
    founded = next((x for x in constants.AVAILABLE_LOCALES if x == language), None)
    if founded:
        session['language'] = founded

    return redirect(url_for('home.start'))


@home.route('/private_policy')
def private_policy():
    config = app.config['PUBLIC_CONFIG']
    return render_template('home/private_policy.html', contact_email=config['support']['contact_email'],
                           title=config['site']['title'])


@home.route('/term_of_use')
def term_of_use():
    config = app.config['PUBLIC_CONFIG']
    return render_template('home/term_of_use.html', contact_email=config['support']['contact_email'],
                           title=config['site']['title'])


@babel.localeselector
def get_locale():
    if session.get('language'):
        lang = session['language']
        return lang

    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(constants.AVAILABLE_LOCALES)
