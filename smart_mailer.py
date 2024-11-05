import os
import smtplib
import time
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import argparse
import requests
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration constants
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
TRACKING_IMAGE_URL = 'http://13.215.200.90/track.png'
COUNTER_URL = 'http://13.215.200.90/counter'
DELAY_BETWEEN_EMAILS = 5  # Delay in seconds to avoid spam

# Regular expression for validating email format
EMAIL_REGEX = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'


# Function to check email validity
def is_valid_email(email):
    return re.match(EMAIL_REGEX, email) is not None


# Function to check email validity
def check_email():
    while True:
            SMTP_USER = input("Enter your email address: ")
            if not is_valid_email(SMTP_USER):
                print("Invalid email address. Please try again.")
            else: 
                return SMTP_USER
            

# Function to check email validity
def check_txt_file():
    while True:
        email_template_path = input("Enter email template file name (such as email_template.txt), file should be in same folder/directory as this app: ")
        if not check_txt_file_extension(email_template_path):
            print("Invalid file extension. Please try again.")
        else:
            return email_template_path


# Function to check txt file extension
def check_txt_file_extension(file_path):
    if not file_path.endswith('.txt'):
        print("File extension is not .txt")
        return False
    
    if not os.path.exists(file_path):
        print("File does not exist.")
        return False
    
    with open(file_path, 'r') as file:
        content = file.read()
        required_elements = ["<html>", "<body>", "#name#", "#department#", "</body>", "</html>"]
        start_index = 0
        for element in required_elements:
            start_index = content.find(element, start_index)
            if start_index == -1:
                print(f"Missing required element: {element}")
                return False
        return True
    

# Function to check CSV validity
def check_csv_file_validity(file_path):
    if not file_path.endswith('.csv'):
        print("File extension is not .csv")
        return False
    
    if not os.path.exists(file_path):
        print("File does not exist.")
        return False
    
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        field_names = reader.fieldnames
        expected_fields = ['email', 'name', 'department_code']
        if field_names[:3] != expected_fields:
                print("The first 3 fields are not in the expected order.")
                return False
        # for row in reader:
        #     if any(field == '' for field in row.values()):
        #         print("There are blank fields in the data.")
        #     extra_fields = set(field_names) - set(expected_fields)
        #     if extra_fields:
        #         for extra_field in extra_fields:
        #             del row[extra_field]
    return True


# Function to check CSV file
def check_csv_file():
    while True:
        file_path = input("Enter mail data csv file name (such as maildata.csv), file should be in same folder/directory as this app: ")
        if not check_csv_file_validity(file_path):
            print("Invalid file extension. Please try again.")
        else:
            return file_path
        

# Function to read CSV and filter based on department code
def read_csv(file_path, department_code):
    filtered_list = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if department_code == 'all' or row['department_code'] == department_code:
                if is_valid_email(row['email']):  # Check if email is valid
                    filtered_list.append(row)
                else:
                    print(f"Invalid email format: {row['email']} - Skipping")
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
        # Use the predefined tracking URL
        tracking_url = TRACKING_IMAGE_URL
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Replace placeholders and include tracking URL
        body = body.replace('#name#', name).replace('#department#', department)
        body += f'<img src="{tracking_url}" width="1" height="1" alt=""/>'
        
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

# Function to get and display the counter
def display_counter():
    try:
        # Pass verify=False to skip SSL verification
        response = requests.get(COUNTER_URL, verify=False)
        if response.status_code == 200:
            print(response.json()['message'])
        else:
            print(f"Failed to get counter data. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching counter data: {e}")


# Main function with argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart mailer script with email sending and tracking functionalities.")
    parser.add_argument('action', choices=['send', 'count'], help="Specify 'send' to send emails or 'count' to display the tracking counter.")
    
    args = parser.parse_args()
    
    if args.action == 'send':
        SMTP_USER = check_email()
        SMTP_PASSWORD = input("Enter your email password (use an app password if necessary): ")
        csv_file_path = check_csv_file()
        department_code = input("Enter department code (or 'all' for all departments): ")
        email_template_path = check_txt_file()

        send_emails_with_report(csv_file_path, department_code, email_template_path, SMTP_USER, SMTP_PASSWORD)

    elif args.action == 'count':
        display_counter()
