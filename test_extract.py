# -*- coding: utf-8 -*-
__author__ = 'Yiyou'

import sys
import urllib2
import pandas as pd
from bs4 import BeautifulSoup
import re
import numpy as np

reload(sys)
sys.setdefaultencoding('utf-8')


def webCrawl(url):
    try:
        html = urllib2.urlopen(url).read() # Connect to the job posting
    except:
        return

    soup = BeautifulSoup(html, 'lxml')

    for script in soup(["script", "style"]):
        script.extract() # Remove these two elements from the BS4 object


    text = soup.getText().decode('utf-8','ignore').encode('utf-8').lower()
    return(text)


def search(skill, text):
    if skill in text:
        return(1)
    else: return 0

def parseSkills(text):
    text = text.lower()
    jd_skills = dict()
    skills = ['python', 'java', 'programming',  'matlab', 'sql', 'sas', 'unix', 'shell', 'ruby', 'perl', 'scala', 'javascript', 'tableau', 'spss', 'd3', 'machine learning', 'visualization', 'algorithm', 'predictive modelling', 'data mining', 'optimization', 'database', 'classification', 'statistical', 'natural language', 'project management', 'hypotheses', 'web',  'distributed', 'communication', 'marketing', 'big data', 'spark', 'hadoop', 'hive', 'nosql', 'mapreduce', 'zookeeper', 'pig', 'mahout', 'hbase', 'cloud', 'computer science', 'engineering', 'phd', 'bachelor', 'quantitative', 'mathematics', 'physics', 'statistics', 'math', 'bioinformatics', 'master', 'software engineering', 'econometrics', 'b2b', 'ms']
    for skill in skills:
        jd_skills[skill] = skill in text

    jd_skills['a_b_testing'] = re.search(re.compile(r'a.b.testing'), text) != None
    jd_skills['r'] = re.search(re.compile(r'\Wr\W'), text) != None
    jd_skills['c'] = re.search(re.compile(r'\Wc\W'), text) != None
    years = re.match(re.compile(r'(\d) years'), text)
    if years:
        jd_skills['experience'] = int(years.group().split()[0])
    else: jd_skills['experience'] = None
    return(jd_skills)

def createNew(source):
    fileIn = 'result\\'+source + '_data_with_skills.csv'
    data = pd.DataFrame.from_csv(fileIn)
    dataNew = pd.DataFrame()

    data.reset_index(level=0, inplace=True)
    for i in range(1,len(data.index)):
        print(i)
        if(isinstance(data['skills'][i], str)):
            new = data.iloc[i].to_dict().copy()
            new.pop('skills', None)
            new.update(parseSkills(data['skills'][i]))
            print(new)
            dataNew = dataNew.append(new, ignore_index= True)
    dataNew['source'] = source
    fileOut = 'result\\'+source + '_data_parsed_skills.csv'
    dataNew.to_csv(fileOut)

if __name__ == '__main__':
    createNew('kaggle')
    createNew('indeed')
    createNew('monster')

    jobinfo = ['position', 'company', 'location', 'date', 'source', 'url', 'query' ]
    programmingskills = ['python', 'java', 'c', 'r', 'programming',  'matlab', 'sql', 'sas', 'unix', 'shell', 'ruby', 'perl', 'scala', 'javascript', 'tableau', 'spss', 'd3']
    knowledge = ['machine learning', 'visualization', 'algorithm', 'predictive modelling', 'data mining', 'optimization', 'database', 'classification', 'statistical', 'natural language', 'project management', 'hypotheses', 'web',  'distributed', 'communication', 'marketing', 'big data', 'spark', 'hadoop', 'hive', 'nosql', 'mapreduce', 'zookeeper', 'pig', 'mahout', 'hbase', 'cloud']
    experience = ['experience','computer science', 'engineering', 'phd', 'bachelor', 'quantitative', 'mathematics', 'physics', 'statistics', 'math', 'bioinformatics', 'master', 'software engineering', 'econometrics', 'b2b', 'ms']
    column = list()
    column.extend(jobinfo)
    column.extend(experience)
    column.extend(programmingskills)
    column.extend(knowledge)

    indeed = pd.DataFrame.from_csv('result\indeed_data_parsed_skills.csv')
    indeed['position'] = indeed.jobtitle
    indeed['location'] = indeed.city.str.cat(indeed.state, sep = ',')
    indeed_orderd = indeed[column]


    monster = pd.DataFrame.from_csv('result\monster_data_parsed_skills.csv')
    monster['company'] = monster['companies']
    monster_orderd = monster[column]


    kaggle = pd.DataFrame.from_csv('result\kaggle_data_parsed_skills.csv')
    kaggle['query'] = ""
    kaggle['url'] = ""
    kaggle_orderd = kaggle[column]


    positionDB_combined = pd.DataFrame()
    positionDB_combined = positionDB_combined.append(indeed_orderd)
    positionDB_combined = positionDB_combined.append(monster_orderd)
    positionDB_combined = positionDB_combined.append(kaggle_orderd)

    positionDB_combined.to_csv('result\parsed_skills_all.csv')