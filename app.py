"""Personal Learning Journal App."""

from flask import (Flask, g, render_template, redirect,
                   url_for, flash, abort)
from flask_login import (LoginManager, login_user, current_user,
                         login_required, logout_user)
from flask_bcrypt import check_password_hash

import models
import forms
import utils

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


@app.route('/', methods=('GET', 'POST'))
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


@app.route('/entries/new', methods=('GET', 'POST'))
@login_required
def new():
    """Define new entry view."""
    form = forms.EntryForm()
    if form.validate_on_submit():
        slug = utils.slugcheck(form)
        entry = models.Entries.create(username=g.user.
                                      _get_current_object(),
                                      title=form.title.data.strip(),
                                      slug=slug,
                                      date=form.date.data,
                                      timeSpent=form.timeSpent.data,
                                      whatILearned=form.whatILearned.data,
                                      resourcesToRemember=form.
                                      ResourcesToRemember.data)
        if form.tags.data:  # add the tags (if entered)
            add_tags(form.tags.data, entry.id)
        flash("Entry created successfully!", "success")
        return redirect(url_for('index'))

        #     try:
        #     entry = models.Entries.create(username=g.user.
        #                                   _get_current_object(),
        #                                   title=form.title.data.strip(),
        #                                   slug=slugify(form.title.data),
        #                                   date=form.date.data,
        #                                   timeSpent=form.timeSpent.data,
        #                                   whatILearned=form.whatILearned.data,
        #                                   resourcesToRemember=form.
        #                                   ResourcesToRemember.data)
        #     if form.tags.data:  # add the tags (if entered)
        #         add_tags(form.tags.data, entry.id)
        #     flash("Entry created successfully!", "success")
        #     return redirect(url_for('index'))
        # except models.IntegrityError:
        #     flash("Title already exits. Please choose another.", "error")

    for field, errors in form.errors.items():
        for error in errors:
            flash(error, "error")

    return render_template('new.html', form=form)


def add_tags(tagdata, current_entry_id):
    """Add the tags."""
    tags = utils.tagger(tagdata)
    for tag in tags:
        try:  # write the tag to the DB and get its id
            current_tag = models.Tag.create(tag=tag)
            current_tag_id = current_tag.id
        except models.IntegrityError:  # unless already exits, get existing id
            current_tag = models.Tag.get(tag=tag)
            current_tag_id = current_tag.id

        models.EntriesTagged.create(entry_ref=current_entry_id,
                                    tag_ref=current_tag_id
                                    )


@app.route('/entries/<slug>')
def detail(slug):
    """Show the detail page via slug."""
    entry = models.Entries.select().where(models.Entries.slug == slug)
    if entry.count() == 0:
        abort(404)  # This needs handling!
    return render_template('detail.html', entry=entry)


@app.route('/entries')
@app.route('/entries/')
@app.route('/entries/<int:id>')
@app.route('/entries/<int:id>/')
def detail_id(id=None):
    """Show the detail page via id or tag."""
    if id:
        entry = models.Entries.select().where(models.Entries.id == id)
        if entry.count() == 0:
            abort(404)
        return render_template('detail.html', entry=entry)
    else:
        entries = models.Entries.select().order_by(models.Entries.date.desc(),
                                                   models.Entries.id.desc())
        return render_template('index.html', entries=entries)


@app.route('/entries/tag/<tag>')
@app.route('/entries/tag/<tag>/')
def all_tagged(tag):
    """Show all entries tagged with X."""
    try:
        tagid = models.Tag.get(models.Tag.tag == tag)
    except models.DoesNotExist:
        abort(404)

    entries = (models.Entries.select()
               .join(models.EntriesTagged)
               .join(models.Tag)
               .where(models.EntriesTagged.tag_ref == tagid)
               .order_by(models.Entries.date.desc(), models.Entries.id.desc())
               )

    if entries.count() == 0:
        abort(404)
    return render_template('tags.html', entries=entries, tag=tag)


@app.route('/entries/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    """Edit the entry."""
    form = forms.EditForm()
    entry = models.Entries.select().where(models.Entries.id == id)
    if form.validate_on_submit():  # Form has passed validation
        try:
            record = models.Entries.get(models.Entries.id == id)
            record.title = form.title.data.strip()
            record.slug = utils.slugcheck(form)
            record.date = form.date.data
            record.timeSpent = form.timeSpent.data
            record.whatILearned = form.whatILearned.data
            record.resourcesToRemember = form.ResourcesToRemember.data
            record.save()
            # process the tags
            new_tags = utils.tagger(form.tags.data)
            tags_in_db = {tag.tag for tag in models.Entries.tags(id)}
            tags_to_delete = tags_in_db - new_tags


            print('tags_in_db: {}'.format(tags_in_db))
            print('new_tags: {}'.format(new_tags))
            print('tags_to_delete: {}'.format(tags_to_delete))

            for tag_to_delete in tags_to_delete:
                tagref = (models.Tag.select()
                          .where(models.Tag.tag == tag_to_delete))
                for tag in tagref:
                    print('tagid: {}'.format(tag.id))






            flash("Entry edited successfully!", "success")
            return redirect(url_for('index'))
        except models.IntegrityError:
            flash("Title already exits. Please choose another.", "error")
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, "error")

    return render_template('edit.html', form=form, entry=entry)


@app.route('/entries/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete(id):
    """Delete the entry."""
    try:
        record = models.Entries.get(models.Entries.id == id)
        user = g.user._get_current_object()
        author = record.username
        # Get refernces to the tags from this entry
        tagrefs = (models.EntriesTagged.select()
                   .where(models.EntriesTagged.entry_ref == id))
        if user == author:
            record.delete_instance()
            for tagref in tagrefs:
                tagrecord = (models.EntriesTagged
                             .get(models.EntriesTagged.id == tagref))
                tagrecord.delete_instance()

            flash("Entry deleted successfully!", "success")
        else:
            flash("Entry can only be deleted by its author", "error")
    except models.DoesNotExist:
        abort(404)

    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    """Handle the 404 error view."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    models.initalize()
    try:
        models.User.create_user(
            username='admin',
            email='admin@admin.com',
            password='password',
            admin=True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)
