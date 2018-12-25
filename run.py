import os
import logging
from datetime import datetime, timedelta


from flask import Flask, url_for, redirect, request
from flask_admin import base, helpers, expose
from flask_admin.contrib import sqla
from flask_sqlalchemy import SQLAlchemy
from wtforms import form, fields, validators
from werkzeug.security import generate_password_hash, check_password_hash

import atexit
from apscheduler.scheduler import Scheduler
import flask_admin as admin
import flask_login as login

from utils import Curation, Steemit as _Steemit
import settings

app = Flask(__name__)

voted_txt = 'voted.txt'
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'steemit'
app.config['DATABASE_FILE'] = 'steemit.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(64))

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.login


class Steemit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    user = db.relationship(User)

    author = db.Column(db.String(200))
    key = db.Column(db.String(500))

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return '<steemit_user %r>' % (self.author)


class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(400))
    expire_time = db.Column(db.DateTime)

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return '<url %r>' % (self.url[10:30])


class UrlAction(db.Model):
    url_id = db.Column(db.Integer(), db.ForeignKey(Url.id), primary_key=True)
    steemit_id = db.Column(db.Integer(), db.ForeignKey(Steemit.id), primary_key=True)
    url = db.relationship(Url)
    steemit = db.relationship(Steemit)
    voted = db.Column(db.Boolean)
    expire_time = db.Column(db.DateTime)

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return '<url %r - %r>' % (self.url_id, self.steemit_id)


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()


class RegistrationForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    email = fields.StringField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated


# Create customized index view class that handles login & registration
class MyAdminIndexView(base.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = ''
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))
    
# Flask views
@app.route('/admin')
def admin():
    return redirect(url_for('admin.login_view'))

init_login()

# Create admin
admin = base.Admin(app, 'Curations', index_view=MyAdminIndexView(), base_template='my_master.html')
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Steemit, db.session))
admin.add_view(MyModelView(Url, db.session))
admin.add_view(MyModelView(UrlAction, db.session))

def build_sample_db():
    db.drop_all()
    db.create_all()

    test_user = User(login="test", password=generate_password_hash("test"))
    db.session.add(test_user)
    db.session.commit()
    return

class PostVote:
    def __init__(self, username, steem_key):
        self.steemit = _Steemit(username, steem_key)
        self.vote = self.vote_list()
        self.voted = self.voted_list()

    def vote_list(self):
        if not self.steemit.get_vp() >= settings.limit_power and self.steemit.get_rc() < 0.1 :
            return []
        return Curation(settings.type, settings.results).result

    def voted_list(self):
        with open(voted_txt, 'r+') as file:
            lines = file.read().splitlines()
        return lines

    def voting_list(self):
        votings = list(set(self.vote) - set(self.voted))
        logging.info(votings)
        for voting in votings:
            username = list(filter(lambda x: '@' in x, voting.split('/')))[0].replace('@','')
            try:
                self.steemit.post_vote(username, voting)
                with open(voted_txt, "a") as f:
                    f.write("{}\n".format(voting))
            except:
                pass
        logging.info('TODO: Logger.info(Done!)')

    def removed_list(self):
        with open(voted_txt, "w") as f:
            f.write('')

def control_flow():
    cron = Scheduler(daemon=True)
    cron.start()

    @cron.interval_schedule(minutes=1)
    def job_function():
        steemit_user = Steemit.query.all()
        for steem in steemit_user:
            vote_commit = PostVote(steem.author, steem.key)
            vote_commit.voting_list()

    atexit.register(lambda: cron.shutdown(wait=False))


def clear_list():
    cron = Scheduler(daemon=True)
    cron.start()

    @cron.interval_schedule(days=4)
    def job_function():
        vote_commit = PostVote()
        vote_commit.removed_list()

    atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == '__main__':
    try:
        control_flow()
        clear_list()
    except:
        pass

    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()
    port = int(os.environ.get('PORT', 9090))
    app.run(host='0.0.0.0', port=port)
