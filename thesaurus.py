from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import *
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import words
from word_forms.word_forms import get_word_forms
import time

lemmatizer = WordNetLemmatizer()


def preprocess_wordnet():
    start = time.time()
    thesaurus = {}
    synsets = {}
    for item in wordnet.all_synsets():
        name = item._name
        synsets[name] = set(item._lemma_names)
        for word in synsets[name]:
            try:
                thesaurus[word].append(name)
            except KeyError:
                thesaurus[word] = [name]
    print "TIME: " + str(time.time()-start)
    #start = time.time()
    # i = 0
    # for word in thesaurus:
    #     if i < 5:
    #         print word
    #         for meaning in thesaurus[word]:
    #             print meaning
    #             print synsets[meaning]
    #         print "************"
    #     else:
    #         break
    #     i+=1
    # print "5 LOOKUPS: " + str(time.time()-start)
    return (thesaurus,synsets)

def preprocess_roots():
    start = time.time()
    dictionary = {}
    roots = {}
    i=0
    pos = ['n','v','a','s','r']
    for item in wordnet.all_synsets():
        for word in set(item._lemma_names):
            lemmas = set()
            for part in pos:
                lemmas |= set([lemmatizer.lemmatize(word,pos=part)])
            try:
                dictionary[word] |= lemmas
            except KeyError:
                dictionary[word] = lemmas
            for lemma in lemmas:
                try:
                    roots[lemma] |= set([word])
                except KeyError:
                    roots[lemma] = set([word])
    print "TIME: " + str(time.time()-start)
    return (dictionary, roots)

#stemmer = PorterStemmer()
stemmer = SnowballStemmer('english')

def preprocess_stems():
    start = time.time()
    dictionary = {}
    stems = {}
    for item in wordnet.all_synsets():
        for word in set(item._lemma_names):
            lemmas = set([stemmer.stem(word)])
            try:
                dictionary[word] |= lemmas
            except KeyError:
                dictionary[word] = lemmas
            for lemma in lemmas:
                try:
                    stems[lemma] |= set([word])
                except KeyError:
                    stems[lemma] = set([word])
    print "TIME: " + str(time.time()-start)
    return (dictionary, stems)

wordlist = words.words()

def preprocess_word_forms():
    start = time.time()
    dictionary = {}
    eqclasses = {}
    for word in wordlist:
        wordset = set()
        forms = get_word_forms(word)
        for pos in forms:
            wordset |= forms[pos]
        for wordform in wordset: 
            try:
                dictionary[wordform] |= wordset
            except KeyError:
                dictionary[wordform] = wordset
    for word in dictionary:
        frzset = frozenset(dictionary[word])
        wordhash = hash(frzset)
        goodkey = False
        while not goodkey:
            try:
                if frzset.issubset(eqclasses[wordhash]) or frzset.issuperset(eqclasses[wordhash]):
                    eqclasses[wordhash] |= frzset
                    goodkey = True
                else:
                    wordhash += 1
            except KeyError:
                eqclasses[wordhash] = frzset
                goodkey = True
        dictionary[word] = wordhash
    print "TIME: "+ str(time.time()-start)
    return (dictionary, eqclasses)




def lookup_roots(word, dictionary, roots):
    out = roots[dictionary[word]]
    print out
    return out


# a = preprocess_word_forms()
# start = time.time()
# lookup_roots('happy',a[0],a[1])
# lookup_roots('run',a[0],a[1])
# lookup_roots('ran',a[0],a[1])
# lookup_roots('running',a[0],a[1])
# print 'LOOKUP 4:' + str(time.time()-start)
# with open('thesaurus.txt','w') as f:
#     f.write(str(a))

# preprocess_word_forms()