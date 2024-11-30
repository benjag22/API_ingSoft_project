from flask_mailman import Mail

mail = Mail()

def configure_mail(app):
    app.config['MAIL_SERVER'] = 'smtp.fastmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = 'centromedico@fastmail.com'
    app.config['MAIL_PASSWORD'] = '2e3m5r6376476a9e'

    mail.init_app(app)
