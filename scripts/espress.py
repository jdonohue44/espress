import MySQLdb
import feedparser
import requests
import json
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def create_dict(interests):
	dict = {}
	for i in interests:
		dict[i] = {}
	return dict

def get_users_from_DB():
	# db = MySQLdb.connect(host="jd-db-instance.csuhsua8cx8a.us-east-1.rds.amazonaws.com",
	#                      user="jdonohue44",
	#                      passwd="dubaiguy$$",
	#                      db="Dubai")
	# cur = db.cursor()
	# cur.execute("SELECT * FROM USERS")
	# return cur.fetchall
	return [[1, "Jared", "jared.donohue@gmail.com"]]

def get_user_interests(uid):
		# cur.execute("""
		# SELECT INTERESTS.Interest FROM USER_INTERESTS
		# INNER JOIN USERS ON USERS.ID = USER_INTERESTS.User_ID
		# INNER JOIN INTERESTS ON INTERESTS.ID = USER_INTERESTS.Interest_ID
		# where USERS.ID = %s;
		# """, (uid,))
		# return cur.fetchall()
		return ("")

users = get_users_from_DB()

for user in users:
	uid  = user[0]
	name = user[1]
	dest = user[2]
	# interests = []
	# interest_rows = get_user_interests(uid)
	interests = ["March Madness"]

	# get the interest name (interest[0])
	# for interest in interest_rows:
	# 	interests.append(interest[0])

	# create interest information dictionary --> {'interest':{'query':'','title':'','link':'','date':''}}
	interest_info_dict = create_dict(interests)

	# Put Queries into interest information dictionary
	for i in interest_info_dict:
		query = ''
		words = i.lower().split()
		for num in range(0,len(words)-1):
			query += words[num] + "+"
		query += words[len(words)-1]
		interest_info_dict[i]['query'] = query

	# Put news info into interest information dictionary
	for i in interest_info_dict:
		d = feedparser.parse('https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q='+ interest_info_dict[i]['query'] + '&output=rss')
		# interest_info_dict[i]['link']   = d['entries'][1]['link']
		# interest_info_dict[i]['date']   = d['entries'][1]['published'][:-13]
		# interest_info_dict[i]['source'] = d['entries'][1]['title'].split("-")[-1]
		# interest_info_dict[i]['title']  = d['entries'][1]['title'][:-(len(iid[i]['source'])+2)]
		day = int(d['entries'][0]['published'][5:7])
		time_hour = int(d['entries'][0]['published'][-12:-10])
		time_min = int(d['entries'][0]['published'][-9:-7])

		print(len(d['entries']))

	# Mail Service
	# message = MIMEMultipart()
	# message['From'] = 'espressmorningnews@gmail.com'
	# message['To'] = dest
	# message['Subject'] = 'Your Espress Newsletter'
	#
	# f1 = open('/home/ec2-user/espress/html/template1.html','r')
	# f2 = open('/home/ec2-user/espress/html/template2.html','r')
	# log_file = open('/home/ec2-user/espress/logs.log','a')
	#
	# html = f1.read()
	# for i in iid:
	# 	html += "<tr><td style='padding: 20px;'>"
	# 	html += "<div style='text-align:center; padding: 10px;'><b style='font-weight: 100; font-size: 24px; font-family: sans-serif;'>" + iid[i]['title'] + "</b></div>"
	# 	html += "<p style='text-align: center; font-size: 11px; margin-top: 4px;'>Retrieved from " + iid[i]['source'] + " on " + iid[i]['date'] + ", based on your interest in <b>" + i + "</b></p>"
	# 	html += "<div style='text-align:right;'><a style='padding:6px; font-size: 16px; text-decoration: underline; margin-right: 30px;' href ='" + iid[i]['link'] + "'>Read Article</a></div>"
	# 	html += "</td></tr>"
	# html += f2.read()
	#
	# message.attach(MIMEText(html.encode('utf-8'), 'html', 'utf-8'))
	#
	# smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
	# smtp_server.starttls()
	# smtp_server.login(source, '5638JabroniStreet**')
	#
	# try:
	#    smtp_server.sendmail(source, dest, message.as_string())
	#    smtp_server.quit()
	#    log_file.write("Successfully sent email -- " + time.strftime("%m-%d-%Y %H:%M") + "\n")
	# except smtplib.SMTPException:
	#    print("Error: unable to send email")
	#    log_file.write("ERROR sending email to" + dest + " -- " + time.strftime("%m-%d-%Y %H:%M") + "\n")

# db.close()
