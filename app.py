import flask
from flask import request, jsonify
import pandas as pd
import numpy as np
from textblob import TextBlob
from collections import Counter
import sys
import nltk
import requests
from bs4 import BeautifulSoup
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
import operator
from summa import keywords
from summa.summarizer import summarize
from datetime import datetime, timedelta
from flask_cors import CORS


def readwords( filename ):
    f = open(filename,encoding="ISO-8859-1")
    words = [ line.rstrip() for line in f.readlines()]
    return words

positive = readwords('positive.txt')
negative = readwords('negative.txt')



tdf = pd.read_csv("OnlineNewsPopularity.csv")
pdf = tdf[[' timedelta', ' n_tokens_title', ' n_tokens_content',' num_imgs',' num_videos',' num_hrefs',' global_subjectivity',' global_sentiment_polarity',' global_rate_positive_words',' global_rate_negative_words',' title_subjectivity',' title_sentiment_polarity',' shares']].copy()
X = pdf.drop([' shares',' timedelta'],axis=1)
y = pdf[' shares']
lm = LinearRegression()
X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=0.33, random_state=42)
lm.fit(X_train,y_train)




app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

def structural_analysis(title,text,image_count,video_count,link_count):
	text = text.lower()
	title = title.lower()
	tokens_title = nltk.word_tokenize(title)
	tokens_content = nltk.word_tokenize(text)
	n_tokens_title = len(tokens_title)
	n_tokens_content = len(tokens_content)
	global_subjectivity = TextBlob(text).sentiment[1]
	global_sentiment_polarity = TextBlob(text).sentiment[0]
	title_subjectivity = TextBlob(title).sentiment[1]
	title_sentiment_polarity = TextBlob(title).sentiment[0]
	pos = 0
	neg = 0
	for key in tokens_content:
		key = key.rstrip('.,?!\n')
		if key in positive:
			pos += 1
		if key in negative:
			neg += 1
	global_rate_positive_words = pos/n_tokens_content
	global_rate_negative_words = pos/n_tokens_content
	num_imgs = image_count
	num_videos = video_count
	num_hrefs = link_count
	d = {' n_tokens_title':n_tokens_title, ' n_tokens_content':n_tokens_content, ' num_imgs':num_imgs, ' num_videos':num_videos,' num_hrefs':num_hrefs, ' global_subjectivity':global_subjectivity, ' global_sentiment_polarity':global_sentiment_polarity,' global_rate_positive_words':global_rate_positive_words, ' global_rate_negative_words':global_rate_negative_words,' title_subjectivity':title_subjectivity, ' title_sentiment_polarity':title_sentiment_polarity}
	ldf = pd.DataFrame(data=d,index=[0])
	return(lm.predict(ldf))

def trendanalysis(title,text,city):
	new_trends = []
	for i in range(0,5):
		date_N_days_ago = datetime.now() - timedelta(days=i)
		new_date = str(date_N_days_ago.year)+"-"+str(date_N_days_ago.month)+"-"+str(date_N_days_ago.day)

		page = requests.get("https://trendogate.com/placebydate/"+city+"/"+new_date)
		soup = BeautifulSoup(page.content, 'html.parser')
		trends = soup.find_all('li', attrs = {'class':'list-group-item'})
		for i in range(len(trends)):
			if ((((str(trends[i]).split())[-1]).split('<'))[0]) not in new_trends:
				new_trends.append(((((str(trends[i]).split())[-1]).split('<'))[0]))

	new_trends = new_trends[0:40]
	wordlist = []
	for i in new_trends:
		if(i=='#'):
			continue
		
		if(i[0]=='#'):
			wordlist.append(i[1:])
		else:
			wordlist.append(i)
	print(wordlist)
	text = text.lower()
	tokens = [t for t in text.split()]
	clean_tokens = tokens[:]
	sr = stopwords.words('english')
	for token in tokens:
	    if token in stopwords.words('english'):
	        clean_tokens.remove(token)
	    freq = nltk.FreqDist(clean_tokens)
	    sorted_list = sorted(
	        freq.items(), key=operator.itemgetter(1), reverse=True)
	list = []
	for listitem in sorted_list:
	    list.append(listitem[0])
	taglist = nltk.tag.pos_tag(list)
	finallist = []
	finallist.append(taglist[0][0])
	finallist.append(taglist[1][0])
	finallist.append(taglist[2][0])
	i=2
	while i<len(taglist) and len(finallist)<=7:
	    if taglist[i][1]=='NN':
	        finallist.append(taglist[i][0])
	    i=i+1
	
	temp = keywords.keywords(text).split("\n")

	tempvar = nltk.pos_tag(temp)
	
	if tempvar:
		for i in nltk.pos_tag(temp):
			if len(finallist)>11:
				break
			
			if i[1]=='NN' or i[1]=='NNS':
				if i[0] not in finallist:
					finallist.append(i[0])
	temps = summarize(text, ratio=0.1)
	if temps:
		another_temp = keywords.keywords(temps).split('\n')
		for i in nltk.pos_tag(another_temp):
			if len(finallist)>15:
				break

			if i[0] not in finallist and (i[1]=='NN' or i[1]=='NNS'):
				finallist.append(i[0])

          
	score = 0
	for i in finallist:
		for j in wordlist:
			if nltk.edit_distance(i,j) <=2:
				score = score+1
	tokens_title = nltk.word_tokenize(title)
	for i in tokens_title:
		for j in wordlist:
			if nltk.edit_distance(i,j) <=2:
				score = score+1
	print(score)
	return(score)

@app.route('/',methods=['GET','POST'])

def home():
	json_data = request.get_json()
	title = json_data["title"]
	text = json_data["text"]
	image_count = json_data["image_count"]
	video_count = json_data["video_count"]
	link_count = json_data["link_count"]
	city_c = json_data["location"]
	structural_a = structural_analysis(title,text,image_count,video_count,link_count)
	trend_a = trendanalysis(title,text,city_c)
	result = []
	result.append(trend_a)
	result.append(structural_a)
	print("API called")
	return(jsonify({"structural_a":structural_a[0],"trend_a":trend_a}))

if __name__ == "__main__":
    app.run(host='0.0.0.0',port='5000')
