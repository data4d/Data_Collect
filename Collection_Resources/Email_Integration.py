 # Email Integration for Notifications

import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
 
## Import Passwords - Importing Passwords from a file stored elsewhere on my computer
# sys.path.append('C:/Users/GTayl/Desktop/Finance Modeling')
# from passwords import Gmail as pwd

def send_mail(fromaddr,toaddr,password,subject,text):
    
    fromaddr = fromaddr
    toaddr = toaddr
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject

    body = text
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, password)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()