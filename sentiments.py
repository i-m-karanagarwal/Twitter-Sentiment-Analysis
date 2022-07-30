from flask import Blueprint, render_template, request
import matplotlib.pyplot as plt
import os

import tweepy
import csv
import re
from textblob import TextBlob
import matplotlib

matplotlib.use('agg')

# register this file as a blueprint
second = Blueprint("second", __name__, static_folder="static", template_folder="template")


# render page when url is called
@second.route("/sentiment_analyzer")
def sentiment_analyzer():
    return render_template("sentiment_analyzer.html")


# class with main logic
class SentimentAnalysis:

    def __init__(self):
        self.tweets = []
        self.tweetText = []

    # This function first connects to the Tweepy API using API keys
    def DownloadData(self, keyword, tweets):

        # authenticating
        consumerKey = 'iwqLddCEkr20K30ZfItCxrkd4'
        consumerSecret = '4uqoUSw06OcrqjfHv6t2pQTXpNAvdlBFDcW9DLiuqUp5Vw8xE7'
        accessToken = '1546953795384770561-k1TQaRkS9atXgOmPHHXq3OX9gBEmS5'
        accessTokenSecret = 'mzYEKWuHwofUR638IzlMIMzKRApcpwc4BULQHUiZxNbTk'
        auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
        auth.set_access_token(accessToken, accessTokenSecret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        tweets = int(tweets)

        # searching for tweets
        self.tweets = tweepy.Cursor(
            api.search_tweets, q=keyword, lang="en").items(tweets)

        # Open/create a file to append data to
        csvFile = open('result.csv', 'a')

        # Use csv writer
        csvWriter = csv.writer(csvFile)

        # creating some variables to store info
        polarity = 0
        positive = 0
        wpositive = 0
        spositive = 0
        negative = 0
        wnegative = 0
        snegative = 0
        neutral = 0

        # iterating through tweets fetched
        for tweet in self.tweets:

            self.tweetText.append(self.cleanTweet(tweet.text).encode('utf-8'))

            analysis = TextBlob(tweet.text)

            # adding up polarities to find the average later
            polarity += analysis.sentiment.polarity

            # adding reaction of how people are reacting to find average later
            if (analysis.sentiment.polarity == 0):
                neutral += 1
            elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3):
                wpositive += 1
            elif (analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6):
                positive += 1
            elif (analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1):
                spositive += 1
            elif (analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity <= 0):
                wnegative += 1
            elif (analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3):
                negative += 1
            elif (analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6):
                snegative += 1

        # Write to csv and close csv file
        csvWriter.writerow(self.tweetText)
        csvFile.close()

        # finding average of how people are reacting
        positive = self.percentage(positive, tweets)
        wpositive = self.percentage(wpositive, tweets)
        spositive = self.percentage(spositive, tweets)
        negative = self.percentage(negative, tweets)
        wnegative = self.percentage(wnegative, tweets)
        snegative = self.percentage(snegative, tweets)
        neutral = self.percentage(neutral, tweets)

        # finding average reaction
        polarity = polarity / tweets

        if (polarity == 0):
            htmlpolarity = "Neutral"

        elif (polarity > 0 and polarity <= 0.3):
            htmlpolarity = "Weakly Positive"
        # print("Weakly Positive")
        elif (polarity > 0.3 and polarity <= 0.6):
            htmlpolarity = "Positive"
        elif (polarity > 0.6 and polarity <= 1):
            htmlpolarity = "Strongly Positive"
        elif (polarity > -0.3 and polarity <= 0):
            htmlpolarity = "Weakly Negative"
        elif (polarity > -0.6 and polarity <= -0.3):
            htmlpolarity = "Negative"
        elif (polarity > -1 and polarity <= -0.6):
            htmlpolarity = "strongly Negative"

        self.plotPieChart(positive, wpositive, spositive, negative,
                          wnegative, snegative, neutral, keyword, tweets)
        print(polarity, htmlpolarity)
        return polarity, htmlpolarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets

    def cleanTweet(self, tweet):
        # Remove Links, Special Characters etc from tweet
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())

    # function to calculate percentage
    def percentage(self, part, whole):
        temp = 100 * float(part) / float(whole)
        return format(temp, '.2f')

    # function which sets and plots the pie chart. The chart is saved in an img file every time the project is run.
    # The previous image is overwritten. This image is called in the html page.

    def plotPieChart(self, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets):
        fig = plt.figure()
        labels = ['Positive [' + str(positive) + '%]', 'Weakly Positive [' + str(wpositive) + '%]',
                  'Strongly Positive [' + str(spositive) +
                  '%]', 'Neutral [' + str(neutral) + '%]',
                  'Negative [' + str(negative) +
                  '%]', 'Weakly Negative [' + str(wnegative) + '%]',
                  'Strongly Negative [' + str(snegative) + '%]']
        sizes = [positive, wpositive, spositive,
                 neutral, negative, wnegative, snegative]
        colors = ['yellowgreen', 'lightgreen', 'darkgreen',
                  'gold', 'red', 'lightsalmon', 'darkred']
        patches, texts = plt.pie(sizes, colors=colors, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.axis('equal')
        plt.tight_layout()
        strFile = r"static/plot1.png"
        if os.path.isfile(strFile):
            os.remove(strFile) 
        plt.savefig(strFile)


@second.route('/sentiment_logic', methods=['POST', 'GET'])
def sentiment_logic():
    # get user input of keyword to search and number of tweets from html form.
    keyword = request.form.get('keyword')
    tweets = request.form.get('tweets')
    sa = SentimentAnalysis()

    polarity, htmlpolarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword1, tweet1 = sa.DownloadData(
        keyword, tweets)
    return render_template('sentiment_analyzer.html', polarity=polarity, htmlpolarity=htmlpolarity, positive=positive,wpositive=wpositive, spositive=spositive,negative=negative, wnegative=wnegative, snegative=snegative, neutral=neutral,keyword=keyword1, tweets=tweet1)


@second.route('/visualize')
def visualize():
    return render_template('piechart.html')
