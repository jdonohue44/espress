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

def create_dict(interests, num_articles):
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
	num_articles = []

	try:
		cur.execute("""
		SELECT INTERESTS.Interest, USER_INTERESTS.Num_Articles FROM USER_INTERESTS
		INNER JOIN USERS ON USERS.ID = USER_INTERESTS.User_ID
		INNER JOIN INTERESTS ON INTERESTS.ID = USER_INTERESTS.Interest_ID
		where USERS.ID = %s;
		""", (uid,))
		interest_rows = cur.fetchall()
		for i in interest_rows:
			print(i)
	except Exception:
		print("ERROR getting user interests from DB.")
		log_file.write("ERROR getting user interests from DB.\n")

	# get the interest name (interest[0])
	for interest in interest_rows:
		interests.append(interest[0])
		num_articles.append(int(interest[1]))

	# create interest information dictionary --> {'interest':{'num_articles' : 3, }[{'query':'','title':'','link':'','date':''}]}
	# {'interest' : [{}, {}, {}] }
	interest_info_dict = create_dict(interests, num_articles)

	# Put news info into interest information dictionary
	# time.strftime directives:
	# %m = month(01,12) %d = day(01,31) %H = hour(00,23) %M = minute(00,59)
	# type(d) = feedparser.FeedParserDict (dictionary storing RSS feed info)
	for interest in interest_info_dict:
		try:
			d = feedparser.parse(
				'https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q='+
			 	get_query(interest) + '&output=rss')
		except Exception:
			print("ERROR parsing (feedparser.parse) google news RSS.")
			log_file.write("ERROR parsing (feedparser.parse) google news RSS.\n")

		# rank articles by most recently published
		# for 0:interest_info_dict[interest][num_articles]
		# get num_articles recent articles
		# now = int(time.strftime("%m%d%H%M"))
		# most_recent = (now - (
		# 			  int(month_to_decimal_map[d['entries'][0]['published'][8:11]] +
		# 			  d['entries'][0]['published'][5:7] +
		# 			  d['entries'][0]['published'][17:19] +
		# 			  d['entries'][0]['published'][20:22])))
		# index = 0
		# for x in range(1,len(d['entries'])):
		# 	cur = (now - (
		# 		  int(month_to_decimal_map[d['entries'][x]['published'][8:11]] +
		# 		  d['entries'][x]['published'][5:7] +
		# 		  d['entries'][x]['published'][17:19] +
		# 		  d['entries'][x]['published'][20:22])))
		# 	if((cur < most_recent) and (cur > 0)):
		# 		most_recent = cur
		# 		index = x

		for i in range(len(interest_info_dict[interest])):
			interest_info_dict[interest][i]['link']   = d['entries'][i]['link']
			interest_info_dict[interest][i]['date']   = d['entries'][i]['published'][:-13]
			interest_info_dict[interest][i]['source'] = d['entries'][i]['title'].split("-")[-1]
			interest_info_dict[interest][i]['title']  = d['entries'][i]['title'][:-(len(interest_info_dict[interest][i]['source'])+2)]

	# Mail Service info
	message = MIMEMultipart()
	message['From'] = source
	message['To'] = dest
	message['Subject'] = 'Your Espress Newsletter'

	f1 = open('/home/ec2-user/espress/html/template1.html','r')
	f2 = open('/home/ec2-user/espress/html/template2.html','r')

	# build email by concatenating HTML and data from interest_info_dict
	html = f1.read()
	for interest in interest_info_dict:
		for i in range(len(interest_info_dict[interest])):
			html += "<tr><td style='padding: 20px;'>"
			html += "<div style='text-align:center; padding: 10px;'><b style='font-weight: 100; font-size: 24px; font-family: sans-serif;'>" + interest_info_dict[interest][i]['title'] + "</b></div>"
			html += "<p style='text-align: center; font-size: 11px; margin-top: 4px;'>Retrieved from " + interest_info_dict[interest][i]['source'] + " on " + interest_info_dict[interest][i]['date'] + ", based on your interest in <b>" + interest + "</b></p>"
			html += "<div style='text-align:right;'><a style='padding:6px; font-size: 16px; text-decoration: underline; margin-right: 30px;' href ='" + interest_info_dict[interest][i]['link'] + "'>Read Article</a></div>"
			html += "</td></tr>"
	html += f2.read()

	message.attach(MIMEText(html.encode('utf-8'), 'html', 'utf-8'))

	# login to email account
	try:
		smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
		smtp_server.starttls()
		smtp_server.login(source, '5638JabroniStreet**')
	except Exception:
		print("ERROR connecting to email server")
 		log_file.write("ERROR connecting to email server\n")

	# send email
	try:
	   smtp_server.sendmail(source, dest, message.as_string())
	   smtp_server.quit()
	   log_file.write("Successfully sent email -- " + time.strftime("%m-%d-%Y %H:%M") + "\n")
	except smtplib.SMTPException:
	   print("Error: unable to send email")
	   log_file.write("ERROR sending email to" + dest + " -- " + time.strftime("%m-%d-%Y %H:%M") + "\n")

db.close()
