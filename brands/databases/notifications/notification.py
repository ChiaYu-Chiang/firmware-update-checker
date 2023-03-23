from email.message import EmailMessage
import smtplib
import requests
import os


def send_email_notification(message):
    smtp_server = "mail.adsl.chief.net.tw"
    smtp_port = 25

    from_email = "Firmware_Crawler@chief.com.tw"
    to_email = ["brian_chiang@chief.com.tw"]
    cc_email = [""]

    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = ", ".join(to_email)
    msg["Cc"] = ", ".join(cc_email)
    msg["Subject"] = "New data committed"
    msg.set_content(message)

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.send_message(msg)
    server.quit()


def send_line_notification(message):
    line_notify_access_token = os.environ.get("line_notify_access_token")
    headers = {
        "Authorization": "Bearer " + str(line_notify_access_token),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    params = {"message": message}
    requests.post(
        "https://notify-api.line.me/api/notify", headers=headers, params=params
    )
