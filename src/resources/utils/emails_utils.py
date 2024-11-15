from flask_mailman import EmailMessage

from flask import url_for
from itsdangerous import URLSafeTimedSerializer

def send_email_confirmation(email, nombrepaciente, cita_id):

    # Crea el token único de confirmación
    serializer = URLSafeTimedSerializer('your_secret_key')
    token = serializer.dumps(cita_id, salt='confirm-cita')

    url = url_for('confirmar_cita', )

    asunto = 'Confirmación cita médica'
    cuerpo = f"Hola {nombrepaciente}, su hora ha sido reservada, por favor a continuación confirme su asistencia"

    ############# SOLO DE PRUEBA #############
    body_html = f"""
    <html>
        <body>
            <h2>Confirmación de Cita</h2>
            <p>Hola {nombrepaciente},</p>
            <p>Haz clic en el siguiente enlace para confirmar tu cita:</p>
            <p><a href="{url}">Confirmar Cita</a></p>
            <p>Gracias por confiar en nuestros servicios.</p>
        </body>
    </html>
    """
    ############# SOLO DE PRUEBA #############

    # Enviar mensaje
    msg = EmailMessage(
        asunto,
        cuerpo,
        'centromédico@gmail.com',    # Correo desde donde se envía
        ['joaquinsandovalreyes04@gmail.com', 'correoejemplo@gmail.com']     # Correo al que llegará
    )
    msg.html_message = body_html
    msg.send()
