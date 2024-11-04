# File path: smart_mailer.py
import smtplib
import time
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration constants
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
TRACKING_IMAGE_URL = 'https://yourserver.com/tracking_pixel.png'  # Replace with your tracking pixel URL
DELAY_BETWEEN_EMAILS = 5  # Delay in seconds to avoid spam

# Function to read CSV and filter based on department code
def read_csv(file_path, department_code):
    filtered_list = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if department_code == 'all' or row['department_code'] == department_code:
                filtered_list.append(row)
    return filtered_list

# Function to read subject and body from a text file
def read_email_template(file_path):
    with open(file_path, 'r') as file:
        content = file.read().split('\n', 1)
        subject = content[0]
        body = content[1]
    return subject, body

# Function to send email
def send_email(to_email, name, department, subject, body, smtp_user, smtp_password):
    try:
        # Prepare the MIME message
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Replace placeholders
        body = body.replace('#name#', name).replace('#department#', department)
        body += f'<img src="{TRACKING_IMAGE_URL}" width="1" height="1" alt=""/>'
        
        msg.attach(MIMEText(body, 'html'))

        # Connect to the server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False

# Function to send emails with a delay and report results
def send_emails_with_report(csv_file, department_code, email_template_path, smtp_user, smtp_password):
    recipients = read_csv(csv_file, department_code)
    subject, body_template = read_email_template(email_template_path)

    sent_count = {}
    for recipient in recipients:
        email_sent = send_email(
            to_email=recipient['email'],
            name=recipient['name'],
            department=recipient['department_code'],
            subject=subject,
            body=body_template,
            smtp_user=smtp_user,
            smtp_password=smtp_password
        )
        if email_sent:
            sent_count[recipient['department_code']] = sent_count.get(recipient['department_code'], 0) + 1
            print(f"Email sent to {recipient['email']}")
            time.sleep(DELAY_BETWEEN_EMAILS)

    # Print report
    print("\nReport:")
    for dept, count in sent_count.items():
        print(f"Department {dept}: {count} emails sent.")

# Main function to execute the mailer
if __name__ == "__main__":
    # Prompt user for SMTP credentials
    SMTP_USER = input("Enter your email address: ")
    SMTP_PASSWORD = input("Enter your email password (use an app password if necessary): ")

    csv_file_path = 'maildata.csv'
    department_code = input("Enter department code (or 'all' for all departments): ")
    email_template_path = 'email_template.txt'

    send_emails_with_report(csv_file_path, department_code, email_template_path, SMTP_USER, SMTP_PASSWORD)
