from flask_mailman import EmailMessage

def send_email_confirmation(email, nombrepaciente, cita_id):
    frontend_url = f"http://localhost:5173/confirmar-cita/{cita_id}"

    asunto = 'Confirmación de cita médica'
    cuerpo = f"""
    Hola {nombrepaciente},

    Para confirmar tu cita médica, haz clic en el siguiente enlace:
    {frontend_url}

    Si no solicitaste esta cita, puedes ignorar este mensaje.
    """

    body_html = f"""
    <html>
        <body>
            <h2>Confirmación de Cita Médica</h2>
            <p>Hola {nombrepaciente},</p>
            <p>Para confirmar tu cita médica, haz clic en el siguiente botón:</p>
            <a href="{frontend_url}" style="
                display: inline-block;
                padding: 10px 20px;
                font-size: 16px;
                color: #ffffff;
                background-color: #007bff;
                text-decoration: none;
                border-radius: 5px;
                text-align: center;
            ">Confirmar Cita</a>
            <p>Si no solicitaste esta cita, puedes ignorar este mensaje.</p>
        </body>
    </html>
    """

    msg = EmailMessage(
        asunto,
        cuerpo,
        'centromedico@fastmail.com',
        [email]
    )
    msg.html_message = body_html
    msg.send()
