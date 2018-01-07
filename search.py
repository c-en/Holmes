import requests

import signal
import time
import datefinder
from bs4 import BeautifulSoup
start = time.time()



# class Timeout(Exception):
#     pass

# def handler(sig, frame):
#     raise Timeout
class TimedOutExc(Exception):
  pass

def deadline(timeout, *args):
  def decorate(f):
    def handler(signum, frame):
      raise TimedOutExc()

    def new_f(*args):

      signal.signal(signal.SIGALRM, handler)
      signal.alarm(timeout)
      return f(*args)
      signal.alarm(0)

    new_f.__name__ = f.__name__
    return new_f
  return decorate


keys = 11

with open('API_KEYS.csv','r') as f:
    for i, line in enumerate(f):
        if i == keys-1:
            api_key = line.split(',')[1].rstrip()

with open('ENGINE_IDS.csv','r') as g:
    for i, line in enumerate(g):
        if i == keys-1:
            engine_id = line.split(',')[1].rstrip()

def normalize(lst):
    max_lst = max(lst)
    if max_lst == 0:
        return lst
    for i in range(len(lst)):
        lst[i] = lst[i]/max_lst
    return lst


def best_answer(lst, neg):
    if neg:
        idx = lst.index(min(lst))
    else:
        idx = lst.index(max(lst))
    return 'a'+str(idx+1)

# doesn't work yet
@deadline(1)
def crawl_url(url):
    r = requests.get(url)
    return r
    # try:
    #     signal.signal(signal.SIGALRM, handler)  # register interest in SIGALRM events
    #     signal.alarm(1)  # timeout in 2 seconds
    #     r = requests.get(url)
    #     return r
    # except Timeout:
    #     print "took too long"
    #     print url


def process(text):
    print "***********************************************"
    query = text['question']
    url = ('https://www.googleapis.com/customsearch/v1?key='
        + api_key + '&cx=' + engine_id + '&q=')
    # checking for question type
    neg = 'NOT' in query
    #if not ('\"' in query):
    neg = neg or ('never' in query)
    #    keywords = text['keywords'].replace('never', '').replace('NOT', '')
    #    url += keywords
    #else:
    #    url += query

    # snippet_hits counts hits in the titles and snippets of the google search
    snippet_results = google_hits(text)

    # check if snippets are too close to call
    if neg:
        func = min
    else:
        func = max
    sn_hits = list(snippet_results['sn_hits'])
    best_sns = func(sn_hits)
    sn_hits.remove(best_sns)
    if not (abs(best_sns - func(sn_hits)) <= 1.5):
        print "NO PAGE HITS"
        pg_hits = [0,0,0]
    else:
        pg_hits = google_pages(text,snippet_results['soup'])

    # combined hit score, with snippets 1/3 weight and pages 2/3 weight
    # aka words appearing in snippets counted 50% more
    a_sns = normalize(snippet_results['sn_hits'])
    a_pgs = normalize(pg_hits)
    print a_sns
    print a_pgs
    a_tots = [sn+pg for sn,pg in zip(a_sns,a_pgs)]
    print "TOTAL SCORE: " + str(a_tots)
    print "NEGATIVE: " + str(neg)
    return text[best_answer(a_tots,neg)]


def snippet_hits(text):
    query = text['keywords']
    
    a1 = text['a1'].upper()
    a2 = text['a2'].upper()
    a3 = text['a3'].upper()

    url = ('https://www.googleapis.com/customsearch/v1?key='
        + api_key + '&cx=' + engine_id + '&q=' + query)

    # hits in snippets
    sn_hits = [0,0,0]

    # count hits in snippets, weighted by 1/(result num)
    r = requests.get(url)
    for i, hit in enumerate(r.json()['items']):
        snippet = hit['snippet'].upper() + ' ' + hit['title'].upper()
        sn_hits[0] += float(snippet.count(a1))*(1./float(i+1))
        sn_hits[1] += float(snippet.count(a2))*(1./float(i+1))
        sn_hits[2] += float(snippet.count(a3))*(1./float(i+1))

    print "SNIPPET HITS: " + str(sn_hits)
    return {'sn_hits':sn_hits, 'results':r.json()['items']}

def google_hits(text):
    query = text['question']

    a1 = text['a1'].upper()
    a2 = text['a2'].upper()
    a3 = text['a3'].upper()

    url = 'https://www.google.com/search?q=' + query

    r = requests.get(url)
    c = r.content
    soup = BeautifulSoup(c)

    sn_hits = [0,0,0]
    # counts hits in snippets AND titles (class 'g' gets both)
    for i, snippet in enumerate(soup.find_all(class_='g')):
        snip = snippet.text.upper()
        sn_hits[0] += float(snip.count(a1))*(1./float(i+1))
        sn_hits[1] += float(snip.count(a2))*(1./float(i+1))
        sn_hits[2] += float(snip.count(a3))*(1./float(i+1))

    print "SNIPPET HITS: " + str(sn_hits)
    return {'sn_hits':sn_hits, 'soup':soup}


    #for link in soup.find_all('a'):
    #    print str(link.get('href')) + '\n'
    #print soup.h3.a['href'][7:]
    
    
def google_pages(text, soup):
    pg_hits = [0,0,0]
    h3 = soup.find_all('h3')
    for i, link in enumerate(h3):
        try:
            url = str(link).split('&')[0].split('"')[-1].split('q=')[-1]
            s = requests.get(url)
            #s = crawl_url(url)
            page_upper = s.text.upper()
            pg_hits[0] += float(page_upper.count(text['a1'].upper()))*(1./float(i+1))
            pg_hits[1] += float(page_upper.count(text['a2'].upper()))*(1./float(i+1))
            pg_hits[2] += float(page_upper.count(text['a3'].upper()))*(1./float(i+1))
        except:
            pass

    print "PAGE HITS: " + str(pg_hits)
    return pg_hits


def page_hits(text, results):
    pg_hits = [0,0,0]
    for i in range(5):
        try:
            url = results[i]['link']
            #s = requests.get(url)
            s = crawl_url(url)
            page_upper = s.text.upper()
            pg_hits[0] += float(page_upper.count(text['a1'].upper()))*(1./float(i+1))
            pg_hits[1] += float(page_upper.count(text['a2'].upper()))*(1./float(i+1))
            pg_hits[2] += float(page_upper.count(text['a3'].upper()))*(1./float(i+1))
        except:
            pass

    print "PAGE HITS: " + str(pg_hits)
    return pg_hits

def total_results(text):
    q1 = text['question'] + ' "' + text['a1']+'"'
    q2 = text['question'] + ' "' + text['a2']+'"'
    q3 = text['question'] + ' "' + text['a3']+'"'
    url = ('https://www.googleapis.com/customsearch/v1?key='
        + api_key + '&cx=' + engine_id + '&q=')
    
    r1 = requests.get(url + q1)
    r2 = requests.get(url + q2)
    r3 = requests.get(url + q3)

    results1 = int(r1.json()['searchInformation']['totalResults'])
    results2 = int(r2.json()['searchInformation']['totalResults'])
    results3 = int(r3.json()['searchInformation']['totalResults'])

    print "TOTAL HITS: " + str([results1,results2,results3])
    return [results1,results2,results3]
    

test = {'keywords': u'What U.S. town music venue allows Americans watch live, in-person concerts Canada? ', 'a1': u'Derby Line', 'a3': u'Niagara Falls', 'a2': u'Portal', 'question': u'What U.S. town has a music venue which allows Americans to watch live, in-person concerts from Canada? '}
