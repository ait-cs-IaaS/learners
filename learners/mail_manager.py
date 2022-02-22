from flask_mail import Mail

mail = Mail()


def init_mail(app):
    global mail
    mail.init_app(app)
