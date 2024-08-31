# Project Portfolio Website

## Description
This is a Flask-based web application for showcasing your project portfolio. It features user authentication, a contact form, and the ability to create, edit, and delete project posts.

### Features

* User registration and login system
* Admin-only access to create, edit, and delete projects
* Contact form with email notification
* Responsive design using Bootstrap
* Rich text editing for project content using CKEditor

### Technologies
* Python
* HTML
* CSS

### Python Libs
* Flask
* Flask-Bootstrap
* Flask-CKEditor
* Flask-SQLAlchemy
* Flask-Login
* Flask-WTF
* Werkzeug

## Getting Started
1. Clone this repository.
2. Create virtual environment.
3. Install [requirements](requirements.txt).
4. Set up environment variables:
    1. `CONFIG_SECRET_KEY`: A secret key for Flask
    2. `DATABASE_URL`: Your database URL
    3. `MY_EMAIL`: Your email address for receiving contact form messages
    4. `MY_EMAIL_PASSWORD`: Your email password (Consider using app-specific passwords for security)
6. Run [script](main.py) in Python. 

##Project Structure
* `main.py`: The main application file containing routes and database models
* `forms.py`: Contains the form classes used in the application
* `templates/`: Directory containing HTML templates for the pages
* `static/`: Directory for static files (CSS, JavaScript, images)

## Usage
1. Visit /register to create a new user account.
2. Visit /admin to log in as an admin.
3. Use the navigation bar to browse projects, view the about page, or contact the site owner.
4. As an admin, you can create new projects, edit existing ones, or delete projects.

## Customization
* Modify the HTML templates in the `templates/` directory to change the appearance of the website.
* Add or remove fields from the project post model in `main.py` to change what information is stored for each project.
* Customize the `contact` form email content in the contact route in `main.py`.
