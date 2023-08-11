from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from forms import CreateProjectForm, RegisterForm, LoginForm, ContactForm
from functools import wraps
from flask import abort
import smtplib
import os


app = Flask(__name__)
# Set secret key as environment variable
app.config['SECRET_KEY'] = os.environ["CONFIG_SECRET_KEY"]
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLES
class ProjectPost(db.Model):
    __tablename__ = "project_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


#Create the User Table
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))


#Create Contacts Table
class Contact(db.Model):
    __tablename__ = "contacts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)


# Only need to run this code the first time
with app.app_context():
    db.create_all()


@app.route('/')
def get_all_projects():
    projects = ProjectPost.query.all()
    return render_template("index.html", all_projects=projects, current_user=current_user, year=date.today().year)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # If user's email already exists
        if User.query.filter_by(email=form.email.data).first():
            # Send flash message
            flash("You've already signed up with that email, log in instead!")
            # Redirect to /login route.
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()

        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("get_all_projects"))

    return render_template("register.html", form=form, current_user=current_user)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Only I need to post projects, so I have made a secret 'admin' path for logging in
@app.route('/admin', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_projects'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_projects'))


@app.route("/project/<int:project_id>")
def show_project(project_id):
    requested_project = ProjectPost.query.get(project_id)
    return render_template("project.html", project=requested_project, current_user=current_user, year=date.today().year)


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user, year=date.today().year)


@app.route("/contact", methods=["GET", "POST"])
def contact():

    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        subject = form.subject.data
        message = form.message.data

        # Create a new contact instance
        new_contact = Contact(name=name, email=email, subject=subject, message=message)

        db.session.add(new_contact)
        db.session.commit()

        flash("Message sent! I will get back to you as soon as possible!")

        # Logic to send contact form message to my gmail account
        my_email = os.environ["MY_EMAIL"]
        my_password = os.environ["MY_EMAIL_PASSWORD"]

        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=my_password)
            connection.sendmail(
                from_addr=my_email,
                to_addrs=my_email,
                msg=f"Subject:{new_contact.subject}\n\n{new_contact.message}\nSent from: {new_contact.name}\nEmail address: {new_contact.email}"  # This is the message
            )

        return redirect(url_for('contact'))

    return render_template("contact.html", form=form, current_user=current_user, year=date.today().year)


#Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function


@app.route("/new-project", methods=["GET", "POST"])
# Mark with decorator
@admin_only
def add_new_project():
    form = CreateProjectForm()
    if form.validate_on_submit():
        new_project = ProjectPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for("get_all_projects"))
    return render_template("make-project.html", form=form, current_user=current_user)


@app.route("/edit-project/<int:project_id>", methods=["GET", "POST"])
@admin_only
def edit_project(project_id):
    project = ProjectPost.query.get(project_id)
    edit_form = CreateProjectForm(
        title=project.title,
        subtitle=project.subtitle,
        img_url=project.img_url,
        body=project.body
    )
    if edit_form.validate_on_submit():
        project.title = edit_form.title.data
        project.subtitle = edit_form.subtitle.data
        project.img_url = edit_form.img_url.data
        project.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_project", project_id=project.id))

    return render_template("make-project.html", form=edit_form, is_edit=True, current_user=current_user)


@app.route("/delete/<int:project_id>")
@admin_only
def delete_project(project_id):
    project_to_delete = ProjectPost.query.get(project_id)
    db.session.delete(project_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_projects'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
