import requests
import time
start = time.time()

keys = 3

with open('API_KEYS.csv','r') as f:
    for i, line in enumerate(f):
        if i == keys-1:
            api_key = line.split(',')[1][:-2]

with open('ENGINE_IDS.csv','r') as g:
    for i, line in enumerate(g):
        if i == keys-1:
            engine_id = line.split(',')[1][:-2]

test = {'keywords': u'What U.S. town music venue allows Americans watch live, in-person concerts Canada? ', 'a1': u'Derby Line', 'a3': u'Niagara Falls', 'a2': u'Portal', 'question': u'What U.S. town has a music venue which allows Americans to watch live, in-person concerts from Canada? '}

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

def count_hits(text):
    query = text['question']
    a1 = text['a1'].upper()
    a2 = text['a2'].upper()
    a3 = text['a3'].upper()
    query = "hello"
    url = ('https://www.googleapis.com/customsearch/v1?key='
        + api_key + '&cx=' + engine_id + '&q=' + query + '')
    print url
    a1_ct = 0
    a2_ct = 0
    a3_ct = 0
    neg = 'NOT' in query

    r = requests.get(url)
    print r.json()
    for hit in r.json()['items']:
        snippet = hit['snippet'].upper()
        a1_ct += snippet.count(a1)
        a2_ct += snippet.count(a2)
        a3_ct += snippet.count(a3)

    cts = [a1_ct,a2_ct,a3_ct]
    print(cts)
    max_cts = max(cts)
    cts.remove(max_cts)
    if not (max_cts - max(cts) <= 2):
        return text[best_answer([a1_ct,a2_ct,a3_ct], neg)]

    a1_pg = 0
    a2_pg = 0
    a3_pg = 0

    for i in range(5):
        url = r.json()['items'][i]['link']
        s = requests.get(url)
        page_upper = s.text.upper()
        a1_pg += page_upper.count(a1)
        a2_pg += page_upper.count(a2)
        a3_pg += page_upper.count(a3)

    cts_pgs = [a1_pg, a2_pg, a3_pg]
    print(cts_pgs)

    a_cts = normalize([a1_ct,a2_ct,a3_ct])
    a_pgs = normalize([a1_pg,a2_pg,a3_pg])

    a1_tot = a_pgs[0]
    a2_tot = a_pgs[1]
    a3_tot = a_pgs[2]
    # print [a1_pg,a2_pg,a3_pg]
    # print [a1_tot,a2_tot,a3_tot]

    return text[best_answer([a1_tot,a2_tot,a3_tot],neg)]

print count_hits(test)