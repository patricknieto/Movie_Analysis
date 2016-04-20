
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
import urllib3
import certifi



# In[166]:

def main():

    #http = urllib3.PoolManager( cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    #pool = urllib3.connection_from_url('http://www.boxofficemojo.com')
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


def get_soup(url):
    try:
        r = requests.get( url)
        page = r.text
        soup = BeautifulSoup(page, 'lxml')

    except requests.ConnectionError:
        print("failed to connect")

    return soup

def generate_links(soup):

    my_list = []
    for link in soup.find("body").find_all('a', href=True):
        if link['href'].startswith('/movies/?id='):
            my_list.append('http://www.boxofficemojo.com' + link['href'])
        elif link['href'] == '' or link['href'].startswith('#'):
            continue
    link_list = (my_list[1:])
    return(link_list)


def getAllMovieData(movie_pages):
    data = []
    count = 0
    for i in movie_pages[:500]:
        movie_data = getSingleMovieData(i)
        data.append(movie_data)
        count += 1
        print('Movies:' + str(count))
        #print('Requests' + str(pool.num_requests))
    return data    


# In[140]:

def get_actor_list(soup):
    #actornames = []
    actorElapsedTimes = []
    actordict = {}
    obj = soup.find(text=re.compile('Actor'))
    if not obj: 
        return None
    else:
        for link in obj.findNext('td').find_all('a'):
            name = link.text.replace('*','')
            actordict[name] = get_date_diff(link['href']), get_gender(name), get_bday(name)
            print(name)
            #actornames.append(get_date_diff(link['href']))
    
#     obj = soup.find(text=re.compile('Actor'))
#     for link in obj.findNext('td').find_all('a'):
#         actorElapsedTimes.append(link['href'])  
    #actordict = dict(actornames[i:i+2] for i in range(0, len(actornames), 2))
    #print(actordict)
    return(actordict)



def get_director_list(soup):
    #directornames = []
    directorElapsedTimes = []
    directordict = {}
    obj = soup.find(text=re.compile('Director:'))
    if not obj: 
        return None
    else:
        for link in obj.findNext('td').find_all('a'):
            name = link.text.replace('*', '')
            directordict[name] = get_date_diff(link['href']), get_gender(name), get_bday(name)
            print(name)
            #directornames.append(get_director_date_diff(link['href']))
    return directordict

    #directordict
#     obj = soup.find(text=re.compile('Actor'))
#     for link in obj.findNext('td').find_all('a'):
#         actorElapsedTimes.append(link['href'])  
    #directordict = dict(directornames[i:i+2] for i in range(0, len(directornames), 2))
    #print(directordict)




def get_date_diff(href):
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

def get_bday(name):
    if name:
        name.replace(' ','+')
        url = ('http://en.wikipedia.org/w/index.php?search='+name+'&title=Special%3ASearch&go=Go')
        #pool = urllib3.connection_from_url('http://en.wikipedia.org')
        soup = get_soup(url)
        for item in soup.find_all(class_="bday"):
            print(to_date(item.text))
            return to_date(item.text)
    else:
        return None

def get_gender(name):
    if name:
        name.replace(' ','+')
        url = ('http://en.wikipedia.org/w/index.php?search='+name+'&title=Special%3ASearch&go=Go')
        soup = get_soup(url)
        obj = soup.find_all(class_="role")
        if not obj: 
            return None
        else:
            for role in obj:
                if 'Actor' in role.text:
                    return '0'
                elif 'Actress' in role.text:
                    return '1'



def to_date(datestring):
    date = dateutil.parser.parse(datestring)
    return date

def money_to_int(moneystring):
    moneystring = moneystring.replace(' (Estimate)', '')
    moneystring = moneystring.replace('$', '').replace(',', '')
    return int(moneystring)

def production_to_int(moneystring):
    try:
        if '.' in moneystring:
            moneystring = moneystring.replace('.','').replace(' million', '00000')
            moneystring = moneystring.replace('$', '')
        else:
            moneystring = moneystring.replace(' million', '000000')
            moneystring = moneystring.replace('$', '')
        print(int(moneystring))
        return int(moneystring)

    except:
        return None

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
    
def getSingleMovieData(url,):
    #create a blank dictionary that will be used to track the movie data
    movie_data = {}
    
    #get the raw movie HTML and create a BeautifulSoup object with the text
    soup = get_soup(url)
    
    movie_data['url'] = url
    
    #get the movie director and add it to `movie_data` dictionary
    #movie_data['director'] = get_movie_value(soup, 'Director')

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

    raw_production = get_movie_value(soup,'Production')
    movie_data['production'] = production_to_int(raw_production)
    
    movie_data['actors'] = get_actor_list(soup)
    
    movie_data['directors'] = get_director_list(soup)
    # movie_data['avg time passed']  =  actordict
    

    return movie_data


# In[143]:



# In[ ]:

main()



