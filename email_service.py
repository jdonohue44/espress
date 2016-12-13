import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

source =  'espressmorningnews@gmail.com'
mailing_list = ['jared.donohue@gmail.com']

message = MIMEMultipart()
message['From'] = source
message['To'] = ", ".join(mailing_list)
message['Subject'] = 'Good Morning from Espress, Today is ' + time.strftime("%d/%m/%Y")

body = 		"""Good Morning Jared! Here is today's news\n
\tStory 1: \n
\tStory 2: \n
\tStory 3: \n
Thanks for subscribing and have a great day!\n
~ Jared from Espress Morning News """

message.attach(MIMEText(body, 'plain'))

smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
smtp_server.starttls()
smtp_server.login(source, '5638JabroniStreet**')

try:
   smtp_server.sendmail(source, mailing_list, message.as_string())
   smtp_server.quit()
   print("Successfully sent email")
except smtplib.SMTPException:
   print("Error: unable to send email")
