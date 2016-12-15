def create_dict(artists):
	dict = {}
	for artist in artists:
		dict[artist] = {}
	return dict

import feedparser
import requests
import json
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Feed/Parse Variables
artists = ['The Growlers', 'Martin Scorsese', 'Wes Anderson', 'Richard Linklater']
stock_abrevs = ['MSFT','FB','AMZN']
google_news_rss_url = 'https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q='
google_finance_feed = 'http://www.google.com/finance/info?q=NASDAQ:'

#Mail Variables
source =  'espressmorningnews@gmail.com'
mailing_list = ['jared.donohue@gmail.com']

# aid = artist information dictionary --> {'artist':{'query':'','title':'','link':'','date':''}}
aid = create_dict(artists)

# Put Queries into Artist dictionary
for a in aid:
	query = ''
	words = a.lower().split()
	for num in range(0,len(words)-1):
		query += words[num] + "+"
	query += words[len(words)-1]
	aid[a]['query'] = query

# Put news info into Artist dictionary
for a in aid:
	d = feedparser.parse(google_news_rss_url + aid[a]['query'] + '&output=rss')
	aid[a]['title'] = d['entries'][1]['title'][:70]
	aid[a]['link']  = d['entries'][1]['link']
	aid[a]['date']  = d['entries'][1]['published']

#
# for stock in stock_abrevs:
# 	r = requests.get(google_finance_feed + stock)
# 	json_response = json.loads(r.text[4:])
# 	curr_price = json_response[0]['l_cur']
# 	print(stock + ': ' + curr_price)
#
#
# Mail Service
message = MIMEMultipart()
message['From'] = source
message['To'] = ", ".join(mailing_list)
message['Subject'] = 'Good Morning from Espress, Today is ' + time.strftime("%d/%m/%Y")

f1 = open('../html/template1.html','r')
f2 = open('../html/template2.html','r')
html = f1.read()
for a in aid:
	html += "<a href ='" + aid[a]['link'] + "'</a>" + aid[a]['title'] + "<br /><br />"
html += f2.read()

message.attach(MIMEText(html, 'html'))

smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
smtp_server.starttls()
smtp_server.login(source, '5638JabroniStreet**')

try:
   smtp_server.sendmail(source, mailing_list, message.as_string())
   smtp_server.quit()
   print("Successfully sent email")
except smtplib.SMTPException:
   print("Error: unable to send email")
