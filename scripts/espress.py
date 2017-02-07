def create_dict(interests):
	dict = {}
	for i in interests:
		dict[i] = {}
	return dict

import MySQLdb
import feedparser
import requests
import json
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Feed/Parse Variables
interests = []
google_news_rss_url = 'https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q='
google_finance_feed = 'http://www.google.com/finance/info?q=NASDAQ:'

#Mail Variables
source =  'espressmorningnews@gmail.com'
dest   =  ''
name   =  ''

db = MySQLdb.connect(host="jd-db-instance.csuhsua8cx8a.us-east-1.rds.amazonaws.com",    # your host, usually localhost
                     user="jdonohue44",         # your username
                     passwd="dubaiguy$$",  # your password
                     db="Dubai")        # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

# Use all the SQL you like
cur.execute("SELECT * FROM USERS")

# print each user in DB
for user in cur.fetchall():
	uid  = user[0]
	name = user[1]
	dest = user[2]
	cur.execute("""
	SELECT INTERESTS.Interest FROM USER_INTERESTS
	INNER JOIN USERS ON USERS.ID = USER_INTERESTS.User_ID
	INNER JOIN INTERESTS ON INTERESTS.ID = USER_INTERESTS.Interest_ID
	where USERS.ID = %s;
	""", (uid,))
	for interest in cur.fetchall():
		interests.append(interest[0])

	# iid = interest information dictionary --> {'interest':{'query':'','title':'','link':'','date':''}}
	iid = create_dict(interests)

	# Put Queries into Artist dictionary
	for i in iid:
		query = ''
		words = i.lower().split()
		for num in range(0,len(words)-1):
			query += words[num] + "+"
		query += words[len(words)-1]
		iid[i]['query'] = query

	# Put news info into Artist dictionary
	for i in iid:
		d = feedparser.parse(google_news_rss_url + iid[i]['query'] + '&output=rss')
		iid[i]['link']   = d['entries'][1]['link']
		iid[i]['date']   = d['entries'][1]['published'][:-13]
		iid[i]['source'] = d['entries'][1]['title'].split("-")[-1]
		iid[i]['title']  = d['entries'][1]['title'][:-(len(iid[i]['source'])+2)]

	# Mail Service
	message = MIMEMultipart()
	message['From'] = source
	message['To'] = dest
	message['Subject'] = 'Good Morning from Espress, Today is ' + time.strftime("%d/%m/%Y")

	f1 = open('/home/ec2-user/espress/html/template1.html','r')
	f2 = open('/home/ec2-user/espress/html/template2.html','r')
	log_file = open('/home/ec2-user/espress/logs.log','a')

	html = f1.read()
	for i in iid:
		html += "<tr><td style='padding-bottom: 10px; border-color: #f2f2f2; border-style: solid; border-width: 10px'>"
		html += "<b>(" + iid[i]['date'] + ")</b> " + " <b>" + iid[i]['source'] + "</b><br />"
		html += "<a href ='" + iid[i]['link'] + "'> " + iid[i]['title'] + "</a>"
		html += "</td></tr>"
	html += f2.read()

	message.attach(MIMEText(html.encode('utf-8'), 'html', 'utf-8'))

	smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
	smtp_server.starttls()
	smtp_server.login(source, '5638JabroniStreet**')

	try:
	   smtp_server.sendmail(source, dest, message.as_string())
	   smtp_server.quit()
	   log_file.write("Successfully sent email -- " + time.strftime("%m-%d-%Y %H:%M") + "\n")
	except smtplib.SMTPException:
	   print("Error: unable to send email")
	   log_file.write("ERROR sending email to" + dest + " -- " + time.strftime("%m-%d-%Y %H:%M") + "\n")

db.close()
