import requests
import signal
import time
import datefinder
start = time.time()



class Timeout(Exception):
    pass

def handler(sig, frame):
    raise Timeout

keys = 8

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

def count_hits(text):
    query = text['question']
    
    a1 = text['a1'].upper()
    a2 = text['a2'].upper()
    a3 = text['a3'].upper()

    url = ('https://www.googleapis.com/customsearch/v1?key='
        + api_key + '&cx=' + engine_id + '&q=')

    # hits in snippets
    a1_sn = 0
    a2_sn = 0
    a3_sn = 0

    # checking for question type
    neg = 'NOT' in query
    if not ('\"' in query):
        neg = neg or ('never' in query)
        keywords = text['keywords'].replace('never', '').replace('NOT', '')
        url += keywords
    else:
        url += query

    if neg:
        print "negative!"

    # count hits in snippets, weighted by 1/(result num)
    r = requests.get(url)
    for i, hit in enumerate(r.json()['items']):
        snippet = hit['snippet'].upper()
        a1_sn += float(snippet.count(a1))*(1./float(i+1))
        a2_sn += float(snippet.count(a2))*(1./float(i+1))
        a3_sn += float(snippet.count(a3))*(1./float(i+1))

    # check if snippets are different enough to stop,
    # or if too close to call
    sns = [a1_sn,a2_sn,a3_sn]
    print(sns)
    if neg:
        func = min
    else:
        func = max
    best_sns = func(sns)
    sns.remove(best_sns)
    print [a1_sn,a2_sn,a3_sn]
    if not (abs(best_sns - func(sns)) <= 1.5):
        return text[best_answer([a1_sn,a2_sn,a3_sn], neg)]

    # hits in pages
    a1_pg = 0
    a2_pg = 0
    a3_pg = 0

    # count hits in pages, weighted by 1/(result num)
    for i in range(5):
        try:
            url = r.json()['items'][i]['link']
            s = requests.get(url)
            page_upper = s.text.upper()
            a1_pg += float(page_upper.count(a1))*(1./float(i+1))
            a2_pg += float(page_upper.count(a2))*(1./float(i+1))
            a3_pg += float(page_upper.count(a3))*(1./float(i+1))
        except:
            pass

    # combined hit score, with snippets 1/3 weight and pages 2/3 weight
    # aka words appearing in snippets counted 50% more
    a_sns = normalize([a1_sn,a2_sn,a3_sn])
    a_pgs = normalize([a1_pg,a2_pg,a3_pg])
    a_tots = [sn+2.*pg for sn,pg in zip(a_sns,a_pgs)]
    return text[best_answer(a_tots,neg)]

# def find_date(text):
#     query1 = text['keywords'] + ' ' + text['a1']
#     query2 = text['keywords'] + ' ' + text['a2']
#     query3 = text['keywords'] + ' ' + text['a3']
#     def count_dates(query):
#         url = url = ('https://www.googleapis.com/customsearch/v1?key='
#         + api_key + '&cx=' + engine_id + '&q='+query+'')


test = {'keywords': u'What U.S. town music venue allows Americans watch live, in-person concerts Canada? ', 'a1': u'Derby Line', 'a3': u'Niagara Falls', 'a2': u'Portal', 'question': u'What U.S. town has a music venue which allows Americans to watch live, in-person concerts from Canada? '}
