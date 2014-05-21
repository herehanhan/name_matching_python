"""
The purpose of this api is to give the closet prospect name,
instead of returning all the "matches", which is the original
purpose in R version. So adaptions are made here.
please be aware of this when using.

all s1, s2 are the original string input
all l1, l2 are the bigrams, made from s1, s2
"""

import collections
import re

filename = "raw_input_prospect_name.csv"

def pre_clean(name):
    """
        @params name: company name
        @return name: pre-cleaned company names
    """
    name = name.lower()
    name = re.sub("&amp;", " and ", name)
    name = re.sub("&"," and ", name)
    name = re.sub("^www\.|\.com| inc$| incorporated$| llc$|\.org|\.net| later$|"
                  "ltd$| corp$| corporation$| co$| inc\.| llc\.| ltd\.| corp\.|"
                  "corporation\.| co\.| incorporated\.|-|/", " ", name)
    name = re.sub("[:,\.\)!\(\t%;!&\?-]+|^ +| +$|\]|\[|\*|\|", " ", name)
    name = re.sub("^ +", "", name)
    name = re.sub(" +", " ", name)
    name = re.sub(" $", "", name)
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


def find_bigram_word(input_list):
    """
        @params input_list: list of letters in the names of a single word
        @return list of bigrams
    """
    return zip(list(input_list),list(input_list)[1:])


def find_bigram_string(input_list):
    """
        @params input_list: list of letters in the names of a whole string
        @return list of complete bigrams of that string
    """
    bigram_list = []
    input_list = input_list.split()
    for word in input_list:
        bigram_list.extend(find_bigram_word(word))
    return bigram_list


def first_n_same_char(s1,s2):
    """
        @params s1, s2: two company name strings
        @return the number of shared letters from the beginning;
        e.g.  first_n_same_char("ankev", "ajielm") = 1
    """
    l=0
    for i in range(0,min(len(list(s1)),len(list(s2)))):
        if list(s1)[0:i] == list(s2)[0:i]:
            l=i
        else:
            break
    return (l)


def get_overlap_num(l1,l2):
    """
        @params l1, l2: two bigram lists of company names
        @return the number of overlap of the two lists
        This also resolves false positives like "bbbb" "bb"
    """
    return len(list((collections.Counter(l1) & collections.Counter(l2)).elements()))


def bigram_sim(s1, s2, penal_p=-0.2, p=0.4):
    """
        @params s1, s2: two company names
                penal_p: the penalty of the first letter is different
                p: (weighting) coefficient about how much to emphasize
                    on the starting letters.
        @return similarity of two companies
    """
    s1 = pre_clean(s1)
    s2 = pre_clean(s2)
    l1 = find_bigram_string(s1)
    l2 = find_bigram_string(s2)
    big_sim = float(2 * get_overlap_num(l1, l2)) / (len(l1) + len(l2))
    l = first_n_same_char(s1, s2)
    min_char = min(len(s1), len(s2))
    final_weight = (float(l) / min_char)*p if l != 0 else penal_p
    sim_metric = big_sim + final_weight * (1 - big_sim)
    return max(0.0, sim_metric)


def enhanced_criteria(s1, prospects, threshold=0.7):
    """
        @params s1: new input company name
                prospects: all the prospects name in DB, global variable
                threshold: only want to compare two company names when the shared letters
                           larger than this percentage of the shortest name.
        @return all the eligible "comparable" prospects with the new input

        remove the req in R version about for strings less than 8 letters only do
        exact match (disregarding white space). actually, all the complex reqs in the
        original versions are stripped down to only one: the shared letters
        has to be over threshold percent.
    """
    return [idx for (idx, prospect) in enumerate(prospects)
            if len(set(list(s1)) & set(list(prospect))) >= threshold * min(len(list(s1)) , len(list(prospect)))]


def get_bigram_sim(s1, clean_pro=CLEANED_PROSPECTS, threshold=0.7):
    """
        @params s1: new input company name
                clean_pro: all the company names after preclean we want to compare to
                threshold: same as enhanced_criteria
        @return a list of all the "eligible" company names and their similarity
                with the new input name, sorted by similarity
    """
    s1 = pre_clean(s1)
    sim = []
    prospects_new_idx = enhanced_criteria(s1, clean_pro, threshold)
    for prospect_idx in prospects_new_idx:
         sim.append([prospect_idx, bigram_sim(s1, CLEANED_PROSPECTS[prospect_idx])])
    return sorted(sim, key=lambda x:x[1], reverse=True)


def get_top_three(s1, prospects=prospects, clean_pro=CLEANED_PROSPECTS, threshold=0.7):
    """
        @params s1: new input company name
                prospects: all the company names before preclean we want to compare to
                clean_pro: all the company names after preclean we want to compare to
                threshold: same as enhanced_criteria
        @return top 3 company names with similarity
    """
    prospect_sim = get_bigram_sim(s1, clean_pro=clean_pro, threshold=threshold)
    return [[prospects[t[0]], t[1]] for t in prospect_sim[:3]]



