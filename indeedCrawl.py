# -*- coding: utf-8 -*-
__author__ = 'Yiyou'

import sys
import urllib2
import xml.etree.ElementTree as ET
import pandas as pd
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

#return the search query at desire with user ip& search positions predefined
# note: fromage = 60 means search within 2 months,
def requesturl(query, ip):
    query = "\"" + query + "\""
    publisher = "http://api.indeed.com/ads/apisearch?publisher=9207766499679789" #Publisher ID. Your publisher ID is "9207766499679789". This is assigned when you register as a publisher.
    version = "&v=2" #Which version of the API you wish to use. All publishers should be using version 2.
    querylang = "&q="+query
    default = "&l=&sort=&radius=&st=&jt=fulltime&start=&limit=100000&fromage=183&highlight=0&filter=&latlong=1&co=us&chnl=&userip="
    ipAdd = ip
    default_continue = "&useragent=&v=2"
    url = publisher+ version+ querylang+default+ipAdd+default_continue
    return url

#request & return the xml file
def indeedrequest(query, ip):
    url = requesturl(query, ip)
    response = urllib2.urlopen(url)
    content = response.read()
    return(content)

#parse xml file& store in the list
def parseXMLtoDF(query, ip):
    content = indeedrequest(query, ip)
    root = ET.fromstring(content)
    position_nodes = root.iter('result')
    positionDB  = pd.DataFrame()
    for position_node in position_nodes:
        position = position_node.getchildren()
        row = dict()
        for jd in position:
            row[jd.tag] = jd.text
        positionDB = positionDB.append(row, ignore_index=True)
    positionDB['query'] = query
    return(positionDB)

#crawl the requirements
def webCrawl(url):
    try:
        html = urllib2.urlopen(url).read() # Connect to the job posting
    except:
        return

    soup = BeautifulSoup(html, 'lxml')
    skills = soup.find('span', id = 'job_summary').getText()
    return(skills)

if __name__ == '__main__':
    ip = "45.56.94.21"
    keywords = ( "data+scientist",  "big+data","data+engineer","data+analyst","business+analyst","marketing+analyst", "analytics", "machine+learning", "machine+learner")
    positionALL = list()
    for i in keywords:
        positionDB = parseXMLtoDF(i, ip)
        positionALL.append(positionDB)
    indeed_data = pd.concat(positionALL)

    skills = list()
    urls = indeed_data['url']
    for i in urls:
        skill = webCrawl(i)
        skills.append(skill)

    indeed_data['skills'] = skills
    indeed_data.to_csv('indeed_data_with_skills.csv')


