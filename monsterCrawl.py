# -*- coding: utf-8 -*-
__author__ = 'Yiyou'

import sys
import urllib2
import pandas as pd
from bs4 import BeautifulSoup
import re

reload(sys)
sys.setdefaultencoding('utf-8')

#return the search query at desire with user ip& search positions predefined
# note: fromage = 60 means search within 2 months,
def getURL(query, page):
    url='http://www.monster.com/jobs/search/Full-Time_8?q='
    default = '&sort=dt.rv.di&page='
    url = url+query+default+str(page)
    return url

def openUrl(url):
    print(url)
    request = urllib2.Request(url, headers={'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'})
    try:
        html = urllib2.urlopen(request).read() # Connect to the job posting
        return(html)
    except urllib2.URLError,e:
        if hasattr(e,"reason"):
            print "Failed to reach the server"
            print "The reason:",e.reason
            return None
        elif hasattr(e,"code"):
            print "The server couldn't fulfill the request"
            print "Error code:",e.code
            print "Return content:",e.read()
            return None
        else:
            return None  #其他异常的处理

#crawl the requirements from single job page
def webCrawl(url):
    html = openUrl(url)
    if html == None:
        return

    soup = BeautifulSoup(html, 'lxml')
    try:
        skills = soup.find('div', class_="jobview-section").getText()
        skills = re.sub("[^a-zA-Z0-9():/.-]"," ", skills)
        return(skills)
    except:
        try:
            for script in soup(["script", "style"]):
                script.extract() # Remove these two elements from the BS4 object

            skills = soup.getText().decode('utf-8', 'ignore').encode('ascii', 'ignore') # Need this as some websites aren't formatted
            return(skills)
        except:
            return None

#for each of the job, save a record to database, return job database for this page
def getJobsfromPage(url):
    pageJobsDB = pd.DataFrame()

    html = openUrl(url)
    if html == None:
        return

    soup = BeautifulSoup(html, 'lxml')              #create a soup object for the html
    jobs = soup.findAll('div', class_ = 'js_result_container  clearfix')                    #find all job postings on the page
    for job in jobs:                                #for each posting extract position, company, location, date, requirements information (requirement using webCrawl function) then form a dict
        position = dict()
        try:
            title = job.find('div', class_ = 'jobTitle')
            link= title.find('a', href = True)['href']
            position['url']  = link
            position['position'] = title.find('span', itemprop="title").getText()
            position['companies'] = job.find('div', class_ = 'company').find('span',  itemprop="name").getText()
            position['location'] = job.find('div', class_ = 'location').find('a').attrs['title']
            #position['location'] = location.find('span', itemprop="addressLocality").getText()
            #print(position)
            #position['state'] = location.find('span', itemprop="addressRegion").getText()
            position['date'] = job.find('div', class_ = 'postedDate').find('time').getText()
            position['skills'] = webCrawl(link)
            pageJobsDB = pageJobsDB.append(position, ignore_index= True)                         #save the job to the page database
        except:
            pass

    return(pageJobsDB)

#for a specific query, add all search page jobs to one job database. save and return
def searchthrough(query):
    queryDB = pd.DataFrame()
    pages = range(1,20)
    for i in pages:
        pageurl = getURL(query, i)
        print(pageurl)
        pageJobsDB = getJobsfromPage(pageurl)
        queryDB = queryDB.append(pageJobsDB)

    queryDB['query'] = query
    fileName = query+'.csv'
    queryDB.to_csv(fileName)
    return(queryDB)

if __name__ == '__main__':
    keywords = ( "data-scientist",  "big-data","data-engineer","data-analyst","business-analyst","marketing-analyst", "analytics", "machine-learning", "machine-learner")
    #getJobsfromPage('http://www.monster.com/jobs/search/Full-Time_8?q=data-scientist&sort=dt.rv.di&page=1').to_csv('test.csv')

    positionDB = pd.DataFrame()
    for i in keywords:
        positionDB = positionDB.append(searchthrough(i))

    positionDB.to_csv('monster_data_with_skills.csv')
