import MySQLdb
import feedparser
import requests
import json
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log_file = open('/home/ec2-user/espress/logs.log','a')
source = 'espressmorningnews@gmail.com'
month_to_decimal_map = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04',
						'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08',
						'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}

def create_dict(interests):
	dict = {}
	for interest in interests:
		# dict[interest] = []
		# dict[interest].append({})
		dict[interest] = {}
	return dict

try:
	db = MySQLdb.connect(host="jd-db-instance.csuhsua8cx8a.us-east-1.rds.amazonaws.com",
	                     user="jdonohue44",
	                     passwd="dubaiguy$$",
	                     db="Dubai")
	cur = db.cursor()
	cur.execute("SELECT * FROM USERS WHERE ID = 11")
	users = cur.fetchall()
except Exception:
	print("ERROR connecting to DB")
	log_file.write("ERROR connecting to DB\n")

for user in users:
	uid  = user[0]
	name = user[1]
	dest = user[2]
	interests = []

	cur.execute("""
	SELECT INTERESTS.Interest FROM USER_INTERESTS
	INNER JOIN USERS ON USERS.ID = USER_INTERESTS.User_ID
	INNER JOIN INTERESTS ON INTERESTS.ID = USER_INTERESTS.Interest_ID
	where USERS.ID = %s;
	""", (uid,))
	interest_rows = cur.fetchall()

	# get the interest name (interest[0])
	for interest in interest_rows:
		interests.append(interest[0])

	# create interest information dictionary --> {'interest':{'query':'','title':'','link':'','date':''}}
	# 										 --> {'interest':[{'query':'','title':'','link':'','date':''}]}
	interest_info_dict = create_dict(interests)

	# Put Queries into interest information dictionary
	# len(d['entries']) = number of articles
	for interest in interest_info_dict:
		query = ''
		words = interest.lower().split()
		for num in range(0,len(words)-1):
			query += words[num] + "+"
		query += words[len(words)-1]
		interest_info_dict[interest]['query'] = query

	# Put news info into interest information dictionary
	# time.strftime directives:
	# %m = month(01,12) %d = day(01,31) %H = hour(00,23) %M = minute(00,59)
	# type(d) = feedparser.FeedParserDict (dictionary storing RSS feed info)
	for interest in interest_info_dict:
		d = feedparser.parse(
			'https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q='+
			 interest_info_dict[interest]['query'] + '&output=rss')

		# rank articles by most recently published
		now = int(time.strftime("%m%d%H%M"))
		most_recent = (now - (
					  int(month_to_decimal_map[d['entries'][0]['published'][8:11]] +
					  d['entries'][0]['published'][5:7] +
					  d['entries'][0]['published'][17:19] +
					  d['entries'][0]['published'][20:22])))
		index = 0
		for x in range(1,len(d['entries'])):
			cur = (now - (
				  int(month_to_decimal_map[d['entries'][x]['published'][8:11]] +
				  d['entries'][x]['published'][5:7] +
				  d['entries'][x]['published'][17:19] +
				  d['entries'][x]['published'][20:22])))
			if((cur < most_recent) and (cur > 0)):
				most_recent = cur
				index = x

		# Use the most recent article, and get remaining information needed.
		interest_info_dict[interest]['link']   = d['entries'][index]['link']
		interest_info_dict[interest]['date']   = d['entries'][index]['published'][:-13]
		interest_info_dict[interest]['source'] = d['entries'][index]['title'].split("-")[-1]
		interest_info_dict[interest]['title']  = d['entries'][index]['title'][:-(len(interest_info_dict[interest]['source'])+2)]

	# Mail Service
	message = MIMEMultipart()
	message['From'] = source
	message['To'] = dest
	message['Subject'] = 'Your Espress Newsletter'

	f1 = open('/home/ec2-user/espress/html/template1.html','r')
	f2 = open('/home/ec2-user/espress/html/template2.html','r')

	# build email by concatenating HTML and data from interest_info_dict
	html = f1.read()
	for interest in interest_info_dict:
		html += "<tr><td style='padding: 20px;'>"
		html += "<div style='text-align:center; padding: 10px;'><b style='font-weight: 100; font-size: 24px; font-family: sans-serif;'>" + interest_info_dict[interest]['title'] + "</b></div>"
		html += "<p style='text-align: center; font-size: 11px; margin-top: 4px;'>Retrieved from " + interest_info_dict[interest]['source'] + " on " + interest_info_dict[interest]['date'] + ", based on your interest in <b>" + interest + "</b></p>"
		html += "<div style='text-align:right;'><a style='padding:6px; font-size: 16px; text-decoration: underline; margin-right: 30px;' href ='" + interest_info_dict[interest]['link'] + "'>Read Article</a></div>"
		html += "</td></tr>"
	html += f2.read()

	message.attach(MIMEText(html.encode('utf-8'), 'html', 'utf-8'))

	# email account info
	smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
	smtp_server.starttls()
	smtp_server.login(source, '5638JabroniStreet**')

	# send the email
	try:
	   smtp_server.sendmail(source, dest, message.as_string())
	   smtp_server.quit()
	   log_file.write("Successfully sent email -- " + time.strftime("%m-%d-%Y %H:%M") + "\n")
	except smtplib.SMTPException:
	   print("Error: unable to send email")
	   log_file.write("ERROR sending email to" + dest + " -- " + time.strftime("%m-%d-%Y %H:%M") + "\n")

db.close()
