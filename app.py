"""Personal Learning Journal App."""

from flask import (Flask, g, render_template, redirect,
                   url_for, flash, abort)
from flask_login import (LoginManager, login_user, current_user,
                         login_required, logout_user)
from flask_bcrypt import check_password_hash

import models
import forms

DEBUG = True
PORT = 5000
HOST = '127.0.0.1'

app = Flask(__name__)
app.secret_key = '0PNN0XK$9KGjoYhQ1RxkOn_8imkX5rEn'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    """Look up a user."""
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the DB before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the DB connection after each request."""
    g.db.close()
    return response


@app.route('/')
def index():
    """Define the index view."""
    entries = models.Entries.select().order_by(models.Entries.date.desc(),
                                               models.Entries.id.desc())
    return render_template('index.html', entries=entries)


@app.route('/register', methods=('GET', 'POST'))
def register():
    """Define the registration view."""
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Registration successful.", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """Define the login view."""
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password was not recognised. "
                  "Please try again.", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Login successful.", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password was not recognised. "
                      "Please try again.", "error")
    return render_template('login.html', form=form)  # unsuccesful login


@app.route('/logout')
@login_required
def logout():
    """Define the logout view."""
    logout_user()
    flash("Logout successful.", "success")
    return redirect(url_for('index'))


@app.route('/new', methods=('GET', 'POST'))
@login_required
def new():
    """Define new entry view."""
    form = forms.EntryForm()  # Instantiate the form
    if form.validate_on_submit():  # Form has passed validation
        print('ok')
        print(form.date.data)
        print(form.title.data)
        print(form.timeSpent.data)
        models.Entries.create(username=g.user._get_current_object(),
                              title=form.title.data.strip(),
                              date=form.date.data,
                              timeSpent=form.timeSpent.data,
                              whatILearned=form.whatILearned.data,
                              resourcesToRemember=form.ResourcesToRemember.data
                              )
        flash("Entry created successfully!", "success")
        return redirect(url_for('index'))
    print('no')
    print(form.date.data)
    print(form.title.data)
    print(form.timeSpent.data)
    print(form.errors)
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, "error")

    return render_template('new.html', form=form)


@app.route('/entries')
@app.route('/entries/<int:id>')
def detail(id=None):
    """Show the detail page."""
    if id:
        entry = models.Entries.select().where(models.Entries.id == id)
        if entry.count() == 0:
            abort(404)  # This needs handling!
        return render_template('detail.html', entry=entry)
    else:
        entries = models.Entries.select().order_by(models.Entries.date.desc(),
                                                   models.Entries.id.desc())
        return render_template('index.html', entries=entries)


if __name__ == '__main__':
    models.initalize()
    try:
        models.User.create_user(
            username='chrisguy',
            email='chris@chrisguy.co',
            password='password',
            admin=True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)
