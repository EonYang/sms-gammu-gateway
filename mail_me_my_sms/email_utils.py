import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))


def send_to_me(html_content, to_email='yangthere@gmail.com'):
    message = Mail(
        from_email='yangthere@gmail.com',
        to_emails=to_email,
        subject='New SMS Received',
        html_content=html_content)
    try:
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
    except Exception as e:
        print(str(e))
