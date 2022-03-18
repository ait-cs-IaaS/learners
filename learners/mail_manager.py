from flask_mail import Mail

"""
Mail manager to send form results to admins
"""

mail = Mail()


def init_mail(app):
    global mail
    mail.init_app(app)
