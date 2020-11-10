import smtplib, ssl, os, base64, json
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
secret_name = ""
project_id = ""
request = {"name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"}
response = client.access_secret_version(request)
secret = response.payload.data.decode("UTF-8")
s = json.loads(secret)

def build_message(request):
    receiver_email = request.get('receiver_email')
    subject = request.get('subject')
    text = MIMEText(request.get('message'), "plain")
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = s.get("SENDER_EMAIL")
    message["To"] = receiver_email
    message.attach(text)
    return message


def send_tls(event, context):
    request = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    message = build_message(request=request)
    server = smtplib.SMTP_SSL(s.get("SMTP_SERVER"), s.get("SMTP_PORT"))
    server.login(user=s.get("SENDER_EMAIL"),password=s.get("SENDER_PASSWORD"))
    server.sendmail(from_addr=message.get('From'), to_addrs=message.get('To'), msg=message.as_string())
    server.close()
    print("Email sent")
