import base64
import json
import os
import requests
import pymysql
import functions_framework

def prepare_email(to_email):
    api_key = os.environ.get('MAILGUN_API_KEY')
    domain = os.environ.get('MAILGUN_DOMAIN')

    message = {
        "from": f"do-not-reply <postmaster@{domain}>",
        "to": [to_email, "nonsense171@gmail.com"],
        "subject": "BlogApp Verify Email Address",
        "text": f"Hello, please verify your email address by clicking on this link: https://{domain}/verify/{to_email}"
    }

    response = requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data=message
    )

def update_user_record(email):

    try:
        host = os.environ.get('DB_HOST')
        user = os.environ.get('DB_USER')
        password = os.environ.get('DB_PASSWORD')
        database = os.environ.get('DB_DATABASE')

        conn = pymysql.connect(host=host, user=user, password=password, database=database)
        
        cursor = conn.cursor()
        query = "UPDATE user SET email_sent_time = NOW() WHERE username = %s"
        cursor.execute(query, (email,))
        conn.commit()
    except Exception as e:
        print(f"Error updating user record: {e}")
    finally:
        conn.close()

@functions_framework.cloud_event
def send_email(cloud_event):
    message_data = base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8')

    message_json = json.loads(message_data)
    email_address = message_json.get('email')

    if email_address:
        prepare_email(email_address)
        update_user_record(email_address)
    else:
        print(f'Email address not found in message: {message_json}')
    