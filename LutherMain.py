
# coding: utf-8

# In[159]:

import urllib 
from bs4 import BeautifulSoup  
import logging  
from urllib.request import urlopen
import requests
import re
import pandas as pd
from collections import defaultdict
import pickle
import numpy as np
import pandas as pd
import dateutil.parser
import pickle


# In[166]:

def main():
    #create a list of page links to the yearly charts. Number of charts set in get_pages()
    movie_page = []
    for url in get_pages():
        #get soup result from every chart in order to find all of the movie links
        soup_result = get_soup(url)
        #loop through every link on chart pages and add them too a larger list of all movie links
        for link in generate_links(soup_result):
            movie_page.append(link)
    #Retrieve all necessary info from each page link and save it as a list of dictionaries.
    amd = getAllMovieData(movie_page)
    #save dictionary in a pickle
    with open('MovieDict.pickle', 'wb') as handle:
        pickle.dump(amd, handle)


# In[8]:

def get_soup(url):
    try:
        response = requests.get(url)
        page = response.text
        soup = BeautifulSoup(page, 'lxml')

    except requests.ConnectionError:
        print("failed to connect")

    return soup


# In[9]:

def get_pages ():
    
    url_list =[]
    for year in range(0,10):
        for page in range(1,3):
            url = 'http://www.boxofficemojo.com/yearly/chart/?page=' + str(page) +'&view=releasedate&view2=domestic&yr=200' + str(year) + '&p=.htm'
            url_list.append(url)
    for year in range(10,16):
        for page in range(1,3):
            url = 'http://www.boxofficemojo.com/yearly/chart/?page=' + str(page) +'&view=releasedate&view2=domestic&yr=20' + str(year) + '&p=.htm'
            url_list.append(url)

    
    return url_list


# In[10]:

def generate_links(soup):

    my_list = []
    for link in soup.find("body").find_all('a', href=True):
        if link['href'].startswith('/movies/?id='):
            my_list.append('http://www.boxofficemojo.com' + link['href'])
        elif link['href'] == '' or link['href'].startswith('#'):
            continue
    link_list = (my_list[1:])
    return(link_list)


# In[31]:

def get_actor_listlinks(movie_page):
    actorlist = []
    for url in movie_page[:10]:
        temp_list = []
        obj = get_soup(url).find(text=re.compile('Actor'))
        for link in obj.findNext('td').find_all('a', href=True):
            temp_list.append('http://www.boxofficemojo.com' + link['href'])
        actorlist.append(temp_list)
    return(actorlist)


# In[140]:

def get_actor_list(soup):
    actornames = []
    actorElapsedTimes = []
    actordict = defaultdict(list)
    obj = soup.find(text=re.compile('Actor'))
    if not obj: 
        return None
    else:
        for link in obj.findNext('td').find_all('a'):
            actornames.append(link.text)
            actornames.append(get_actor_date_diff(link['href']))
    
#     obj = soup.find(text=re.compile('Actor'))
#     for link in obj.findNext('td').find_all('a'):
#         actorElapsedTimes.append(link['href'])  
    actordict = dict(actornames[i:i+2] for i in range(0, len(actornames), 2))
    return(actordict)


# In[112]:

def get_actor_date_diff(href):
    temp_list = []
    days_passed = []
    href = 'http://www.boxofficemojo.com/'+ href
    for link in get_soup(href).find_all('a', href=True):
        if link['href'].startswith('/schedule/?view=bydate&release=theatrical&date='):
            temp_list.append(to_date(link.text))
    if len(temp_list) > 2:  
        days_passed.append(temp_list[1] - temp_list[0])
        return(days_passed)
    else:
        return None


# In[153]:


def to_date(datestring):
    date = dateutil.parser.parse(datestring)
    return date

def money_to_int(moneystring):
    moneystring = moneystring.replace(' (Estimate)', '')
    moneystring = moneystring.replace('$', '').replace(',', '')
    return int(moneystring)

def runtime_to_minutes(runtimestring):
    runtime = runtimestring.split()
    try:
        minutes = int(runtime[0])*60 + int(runtime[2])
        return minutes
    except:
        return None

def get_movie_value(soup, field_name):
    '''Grab a value from boxofficemojo HTML
    
    Takes a string attribute of a movie on the page and
    returns the string in the next sibling object
    (the value for that attribute)
    or None if nothing is found.
    '''
    obj = soup.find(text=re.compile(field_name))
    if not obj: 
        return None
    in_box_content = obj.find_parents(class_='mp_box_content')
    if in_box_content:
        return getBoxContent(obj)
    else:
        return getHeadTableContent(obj)
    

def getHeadTableContent(obj):
    next_sibling = obj.findNextSibling()
    parent_sibling = obj.find_parent().findNextSibling()
    if next_sibling:
        return next_sibling.text 
    elif parent_sibling:
        return parent_sibling.text
    else:
        return None
    
def getBoxContent(obj):
    
    other = obj.find_parent('td').find_next_sibling('td')
    
    if not other:
        return None
    else:
        return other.get_text(strip=True)
    
def getSingleMovieData(url):
    #create a blank dictionary that will be used to track the movie data
    movie_data = {}
    
    #get the raw movie HTML and create a BeautifulSoup object with the text
    soup = get_soup(url)
    
    movie_data['url'] = url
    
    #get the movie director and add it to `movie_data` dictionary
    movie_data['director'] = get_movie_value(soup, 'Director')

    #get the movie title
    title_string = soup.find('title').text
    title = title_string.split('(')[0].strip()
    movie_data['title'] = title
    
    #get the release date
    raw_release_date = get_movie_value(soup,'Release Date')
    movie_data['release_date'] = to_date(raw_release_date)
    
    #get the domestic total gross
    raw_domestic_total_gross = get_movie_value(soup,'Domestic Total')
    movie_data['domestic_total_gross'] = money_to_int(raw_domestic_total_gross)
    
    #get the MPAA rating
    movie_data['rating'] = get_movie_value(soup,'MPAA Rating')
    
    raw_runtime = get_movie_value(soup,'Runtime')
    movie_data['runtime'] = runtime_to_minutes(raw_runtime)
    
    movie_data['actors'] = get_actor_list(soup)
    
    # actordict = get_actor_list(soup)
    # movie_data['avg time passed']  =  actordict
    
    return movie_data


# In[143]:

def getAllMovieData(movie_pages):
    data = []
    count = 0
    for i in movie_pages:
        movie_data = getSingleMovieData(i)
        data.append(movie_data)
        count += 1
        print(count)
    return data    


# In[ ]:

main()



