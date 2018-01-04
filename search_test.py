import requests
import time
start = time.time()

api_key = ""
engine_id = ""

test = {'a1': u'Hippo Fitting', 'a3': u'High Fidelity', 'a2': u'Hilarious Fiction', 'question': u"The audio equipment term 'hi- fi is short for what? "}

def normalize(lst):
    min_lst = min(lst)
    max_lst = max(lst)
    diff = max(lst) - min_lst
    if diff == 0:
        return [1]*len(lst)
    out = []
    for i in lst:
        out.append((i - min_lst)/diff)
    return out


def count_hits(text):

    query = text['question']
    a1 = text['a1'].upper()
    a2 = text['a2'].upper()
    a3 = text['a3'].upper()
    url = ('https://www.googleapis.com/customsearch/v1?key='
        + api_key + '&cx=' + engine_id + '&q=' + query + '')
    a1_ct = 0
    a2_ct = 0
    a3_ct = 0
    print time.time() - start
    r = requests.get(url)
    print time.time() - start
    for hit in r.json()['items']:
        snippet = hit['snippet'].upper()
        a1_ct += snippet.count(a1)
        a2_ct += snippet.count(a2)
        a3_ct += snippet.count(a3)
    print time.time() - start

    print "A1 COUNT: " + str(a1_ct)
    print "A2 COUNT: " + str(a2_ct)
    print "A3 COUNT: " + str(a3_ct)

    cts = [a1_ct,a2_ct,a3_ct]
    max_cts = max(cts)
    if not (max_cts - max(cts.remove(max_cts)) <= 2):
        if a1_ct == max_cts:
            return text['a1']
        elif a2_ct == max_cts:
            return text['a2']
        else:
            return text['a3']

    a1_pg = 0
    a2_pg = 0
    a3_pg = 0
    print time.time() - start
    for i in range(5):
        url = r.json()['items'][i]['link']
        s = requests.get(url)
        page_upper = s.text.upper()
        a1_pg += page_upper.count(a1)
        a2_pg += page_upper.count(a2)
        a3_pg += page_upper.count(a3)

    print time.time() - start
    print "A1 PAGE: " + str(a1_pg)
    print "A2 PAGE: " + str(a2_pg)
    print "A3 PAGE: " + str(a3_pg)



    a_cts = normalize([a1_ct,a2_ct,a3_ct])
    a_pgs = normalize([a1_pg,a2_pg,a3_pg])

    a1_tot = 0.5*a_cts[0] + 0.5*a_pgs[0]
    a2_tot = 0.5*a_cts[1] + 0.5*a_pgs[1]
    a3_tot = 0.5*a_cts[2] + 0.5*a_pgs[2]
    print "A1 TOTAL: " + str(a1_tot)
    print "A2 TOTAL: " + str(a2_tot)
    print "A3 TOTAL: " + str(a3_tot)

    max_tot = max(a1_tot,a2_tot,a3_tot)
    if a1_tot == max_tot:
        return text['a1']
    elif a2_tot == max_tot:
        return text['a2']
    else:
        return text['a3']


count_hits(test)