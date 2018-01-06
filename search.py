import requests
import signal
import time
import datefinder
start = time.time()



class Timeout(Exception):
    pass

def handler(sig, frame):
    raise Timeout

keys = 5

with open('API_KEYS.csv','r') as f:
    for i, line in enumerate(f):
        if i == keys-1:
            api_key = line.split(',')[1].rstrip()

with open('ENGINE_IDS.csv','r') as g:
    for i, line in enumerate(g):
        if i == keys-1:
            engine_id = line.split(',')[1].rstrip()

def normalize(lst):
    min_lst = min(lst)
    max_lst = max(lst)
    diff = max(lst) - min_lst
    if diff == 0:
        return [1]*len(lst)
    out = []
    for i in lst:
        out.append(float(i - min_lst)/float(diff))
    return out

def best_answer(lst, neg):
    if neg:
        idx = lst.index(min(lst))
    else:
        idx = lst.index(max(lst))
    return 'a'+str(idx+1)

# doesn't work yet
def crawl_url(url):
    signal.signal(signal.SIGALRM, handler)  # register interest in SIGALRM events

    signal.alarm(2)  # timeout in 2 seconds
    try:
        r = requests.get(url)
        return r

    except Timeout:
        print('took too long', url)


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
    snippet_results = snippet_hits(text,neg)

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
        pg_hits = page_hits(text,snippet_results['results'])

    # combined hit score, with snippets 1/3 weight and pages 2/3 weight
    # aka words appearing in snippets counted 50% more
    a_sns = normalize(snippet_results['sn_hits'])
    a_pgs = normalize(pg_hits)
    a_tots = [sn+2.*pg for sn,pg in zip(a_sns,a_pgs)]
    print "TOTAL SCORE: " + str(a_tots)
    print "NEGATIVE: " + str(neg)
    return text[best_answer(a_tots,neg)]

def snippet_hits(text, neg):
    query = text['keywords']
    
    a1 = text['a1'].upper()
    a2 = text['a2'].upper()
    a3 = text['a3'].upper()

    url = ('https://www.googleapis.com/customsearch/v1?key='
        + api_key + '&cx=' + engine_id + '&q=' + query)
    print url

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

def page_hits(text, results):
    pg_hits = [0,0,0]
    for i in range(5):
        try:
            url = results[i]['link']
            s = requests.get(url)
            page_upper = s.text.upper()
            pg_hits[0] += float(page_upper.count(text['a1'].upper()))*(1./float(i+1))
            pg_hits[1] += float(page_upper.count(text['a2'].upper()))*(1./float(i+1))
            pg_hits[2] += float(page_upper.count(text['a3'].upper()))*(1./float(i+1))
        except:
            pass

    print "PAGE HITS: " + str(pg_hits)
    return pg_hits

def total_results(text):
    q1 = text['question'] + ' ' + text['a1']
    q2 = text['question'] + ' ' + text['a2']
    q3 = text['question'] + ' ' + text['a3']
    url = ('https://www.googleapis.com/customsearch/v1?key='
        + api_key + '&cx=' + engine_id + '&q=')
    
    r1 = requests.get(url + q1)
    r2 = requests.get(url + q2)
    r3 = requests.get(url + q3)

    results1 = r1.json()['searchInformation']['totalResults']
    results2 = r2.json()['searchInformation']['totalResults']
    results3 = r3.json()['searchInformation']['totalResults']

    print "TOTAL HITS: " + str([results1,results2,results3])
    return [results1,results2,results3]
    

test = {'keywords': u'What U.S. town music venue allows Americans watch live, in-person concerts Canada? ', 'a1': u'Derby Line', 'a3': u'Niagara Falls', 'a2': u'Portal', 'question': u'What U.S. town has a music venue which allows Americans to watch live, in-person concerts from Canada? '}

