import mysql.connector
from mysql.connector import Error
import feedparser
import requests
import json
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# log_file = open('/home/ec2-user/espresso/logs.log','a')
source = 'espressmorningnews@gmail.com'
customers = []

def create_article_info_dict(interests, num_articles):
	dict = {}
	index = 0
	for interest in interests:
		dict[interest] = []
		for i in range(num_articles[index]):
			dict[interest].append({})
		index += 1
	return dict

def get_query(interest):
	query = ''
	words = interest.lower().split()
	for num in range(0,len(words)-1):
		query += words[num] + "+"
	query += words[len(words)-1]
	return query

try:
	connection = mysql.connector.connect(host='dubai.csuhsua8cx8a.us-east-1.rds.amazonaws.com',
                                         database='Espresso',
                                         user='jdonohue44',
                                         password='dubaiguy$$')
	if connection.is_connected():
	    cursor = connection.cursor()
	    cursor.execute("select * from Customer;")
	    customers = cursor.fetchall()
	    print("Customers: ", customers)

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

for customer in customers:
	interests_dict = json.loads(customer[1])
	# for each interest we need to store num_articles articles info
	article_info_dict = {}
	for interest in interests_dict:
		num_articles = interests_dict[interest]
		# {"dogs": [{"title":"", "date":"", "link":""}, {}]}
		article_info_dict[interest] = []

		try:
			# get some news based on interests
			print("retrieving news on", interest, "for", customer[0])
			rss_data = feedparser.parse(
				'https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q='+
			 	get_query(interest) + '&output=rss')
		except Exception:
			print("ERROR parsing google news RSS.", Exception)
			# log_file.write("ERROR parsing (feedparser.parse) google news RSS.\n")

		# need source, title, date, link, interest
		entries = rss_data['entries']
		article_info = {}
		for i in range(num_articles):
			article_info['link']   = entries[i]['link']
			article_info['date']   = entries[i]['published'][:-13]
			article_info['source'] = entries[i]['title'].split("-")[-1]
			article_info['title']  = entries[i]['title'][:-(len(article_info['source'])+2)]
			article_info_dict[interest].append(article_info)
			article_info = {}

	print("preparing articles:", article_info_dict)
	# Mail Service info
	dest = customer[0] # email address for this customer
	message = MIMEMultipart()
	message['From'] = source
	message['To'] = dest
	message['Subject'] = 'Today\'s Espresso Newsletter'

	f1 = open('/Users/jareddonohue/AWS/espress/html/template1.html','r')
	f2 = open('/Users/jareddonohue/AWS/espress/html/template2.html','r')

	# build email by concatenating HTML and data from interest_info_dict
	html = f1.read()
	for interest in article_info_dict:
		for i in range(len(article_info_dict[interest])):
			html += "<tr><td style='padding: 20px;'>"
			html += "<div style='text-align:center; padding: 10px;'><b style='font-weight: 100; font-size: 24px; font-family: sans-serif;'>" + article_info_dict[interest][i]['title'] + "</b></div>"
			html += "<p style='text-align: center; font-size: 11px; margin-top: 4px;'>Retrieved from " + article_info_dict[interest][i]['source'] + " on " + article_info_dict[interest][i]['date'] + ", based on your interest in <b>" + interest + "</b></p>"
			html += "<div style='text-align:right;'><a style='padding:6px; font-size: 16px; text-decoration: underline; margin-right: 30px;' href ='" + article_info_dict[interest][i]['link'] + "'>Read Article</a></div>"
			html += "</td></tr>"
	html += f2.read()

	message.attach(MIMEText(html.encode('utf-8'), 'html', 'utf-8'))

	# login to email account
	try:
		smtp_server = smtplib.SMTP('smtp.gmail.com', 587, None, 30)
		smtp_server.starttls()
		smtp_server.login(source, '5638JabroniStreet**')
	except Exception as e:
		print("ERROR connecting to email server", str(e))
		# log_file.write("ERROR connecting to email server\n")

	# send email
	try:
	   smtp_server.sendmail(source, dest, message.as_string())
	   smtp_server.quit()
	   print("Successfully sent email to", dest)
	   # log_file.write("Successfully sent email -- " + time.strftime("%m-%d-%Y %H:%M") + "\n")
	except smtplib.SMTPException:
	   print("Error: unable to send email")
	   # log_file.write("ERROR sending email to" + dest + " -- " + time.strftime("%m-%d-%Y %H:%M") + "\n")
