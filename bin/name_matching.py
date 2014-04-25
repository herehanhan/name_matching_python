""" The purpose of this api is to give the closet prospect name,
instead of returning all the "matches", which is the original
purpose in R version. So adaptions are made here.
please be aware of this when using.
"""

import collections
import re

##### all s1, s2 are the original string input
##### all l1, l2 are the bigrams, from s1, s2

filename = "raw_input_prospect_name.csv"

def pre_clean(name):
    """
        @params name
        @return
    """
    name = name.lower()
    name = re.sub("&amp;", " and ", name)
    name = re.sub("&"," and ", name)
    name = re.sub("^www\.|\.com| inc$| incorporated$| llc$|\.org|\.net| later$|"
                  "ltd$| corp$| corporation$| co$| inc\.| llc\.| ltd\.| corp\.|"
                  "corporation\.| co\.| incorporated\.|-|/"," ",name)
    name = re.sub("[:,\.\)!\(\t%;!&\?-]+|^ +| +$|\]|\[|\*|\|"," ",name)
    name = re.sub("^ +","",name)
    name = re.sub(" +"," ",name)
    name = re.sub(" $","",name)
    return name


prospects = []
CLEANED_PROSPECTS = []

with open(filename) as fin:
    for line in fin.xreadlines():
        prospects.append(line.strip())

CLEANED_PROSPECTS = [pre_clean(x) for x in prospects]

# class prospect(object):
#    def __init__(self, name):
#		self.name = name
#		self.preClean = preClean(name)



#with open(filename,"rb") as f:
#    for line in f.xrean
#    reader = csv.reader(f)
#    for row in reader:
#        prospects.extend(row)

#def find_bigram_word(input_list):
#    bigram_list = []
#    for i in range(len(input_list)-1):
#        bigram_list.append((list(input_list)[i],list(input_list)[i+1]))
#    return bigram_list

def find_bigram_word(input_list):
    return zip(list(input_list),list(input_list)[1:])

def find_bigram_string(input_list):
    bigram_list = []
    input_list = input_list.split()
    for word in input_list:
        bigram_list.extend(find_bigram_word(word))
    return bigram_list

#### the number of shared first letters
def first_n_same_char(s1,s2):
    l=0
    for i in range(0,min(len(list(s1)),len(list(s2)))):
        if list(s1)[0:i] == list(s2)[0:i]:
            l=i
        else:
            break
    return (l)

##### the difference between overlap() and intersect() is overlap excludes false positive like "bbbb" "bb"

### it should be:
def get_overlap_num(l1,l2):
    return len(list((collections.Counter(l1) & collections.Counter(l2)).elements()))

def bigram_sim(s1, s2, penal_p=-0.2, p=0.4):
    s1 = pre_clean(s1)
    s2 = pre_clean(s2)
    l1 = find_bigram_string(s1)
    l2 = find_bigram_string(s2)
    #simMetric = []
    big_sim = float(2 * get_overlap_num(l1, l2)) / (len(l1) + len(l2))
    l = first_n_same_char(s1, s2)
    min_char = min(len(s1), len(s2))
    final_weight = (float(l) / min_char)*p if l != 0 else penal_p
    sim_metric = big_sim + final_weight * (1 - big_sim)
    return max(0.0, sim_metric)



#### remove the req in R version about for strings less than 8 letters only do
#### exact match (disregarding white space).
#### actually, all the complex reqs in the original versions are stripped down to
#### only one: the shared letters has to be over threshold percent.
#### return a list of new names that satisfies this criteria
def enhanced_criteria(s1, prospects, threshold=0.7):
    return [idx for (idx, prospect) in enumerate(prospects)
            if len(set(list(s1)) & set(list(prospect))) >= threshold * min(len(list(s1)) , len(list(prospect)))]


##### return full list that satisfies the criteria that shared letters has to be larger than some threshold
def get_bigram_sim(s1, clean_pro=CLEANED_PROSPECTS, threshold=0.7):
    s1 = pre_clean(s1)
    sim = []
    prospects_new_idx = enhanced_criteria(s1, clean_pro, threshold)
    for prospect_idx in prospects_new_idx:
#        sim[prospect] = bigram_sim(s1,prospect)
         sim.append([prospect_idx, bigram_sim(s1, CLEANED_PROSPECTS[prospect_idx])])
    return sorted(sim, key=lambda x:x[1], reverse=True)


##### return only top 3
def get_top_three(s1, prospects=prospects, clean_pro=CLEANED_PROSPECTS, threshold=0.7):
    prospect_sim = get_bigram_sim(s1, clean_pro=clean_pro, threshold=threshold)
    return [[prospects[t[0]], t[1]] for t in prospect_sim[:3]]



