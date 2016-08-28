# -*- coding: utf-8 -*-
__author__ = 'Yiyou'

import sys
import urllib2
import pandas as pd
from bs4 import BeautifulSoup
import twitter
import re

reload(sys)
sys.setdefaultencoding('utf-8')



def getTweets():
    ACCESS_TOKEN = '752829119381975040-s7U85hJAagmHGBUIL86cwjOiN6M7KZs'
    ACCESS_SECRET = 'PYPZvvUr6W3xId2wxYF02l5flUQNFIgcd8xTFYEvQ3lVm'
    CONSUMER_KEY = '8tKmzUBgTPDxC6tIe0Qe8NHGU'
    CONSUMER_SECRET = '1ujD4BmylnY9JatWqz2wxQOeUzVLEqMZ5O9TmiZPuePz68fkZc'
    api = twitter.Api(consumer_key= CONSUMER_KEY,
                      consumer_secret= CONSUMER_SECRET,
                      access_token_key= ACCESS_TOKEN,
                      access_token_secret= ACCESS_SECRET)
    statuses = api.GetUserTimeline(screen_name='KaggleCareers', count = 200 )
    return(statuses)

def cleanTweets(tweet):
    text = tweet.text.decode('utf-8','ignore').encode('utf-8')
    text = re.sub("[^a-zA-Z0-9():/.-]"," ", text)
    pattern1 = re.compile(r'-')
    pattern2 = re.compile(r'http.*')
    url= re.findall(pattern2, re.split(pattern1, text)[1])
    if url:
        return(url)[0]
    else:
        return

def webCrawl(url):
    job = dict()
    job['url'] = url

    try:
        html = urllib2.urlopen(url).read() # Connect to the job posting
    except:
        return

    soup = BeautifulSoup(html, 'lxml')

    title= soup.find('div', class_= 'title')
    job['url'] = url
    job['position'] = title.h1.getText()
    job['company'] = title.h2.getText()
    job['location'] = title.h3.getText()

    content = soup.find('div', class_ = 'jobs-board-post-content')
    job['date'] = content.find('p', class_ = 'submission-date').find('span').attrs['title']
    jd = ""
    requirements = content.findAll('ul')
    for i in requirements:
        jd += i.getText() + " "
    job['skills'] = jd
    print(job)
    return(job)


if __name__ == '__main__':
    positionDB = pd.DataFrame()
    url = 'https://www.kaggle.com/jobs/17230/winton-capital-management-data-engineer-san-francisco'

    tweets = getTweets()

    for i in tweets:
        url = cleanTweets(i)
        job = webCrawl(url)
        positionDB = positionDB.append(job, ignore_index=True)
    print(positionDB)

    positionDB.to_csv('kaggle_data_with_skills.csv')



