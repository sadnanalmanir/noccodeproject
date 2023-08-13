#!/usr/bin/env python
# coding: utf-8

# In[9]:


from __future__ import division
import pandas as pd
import re, os, time
import string
from difflib import get_close_matches
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import *
import nltk
from numpy import random
from pyprojroot import here

nltk.download('stopwords')
nltk.download('punkt')
porter = PorterStemmer()

synonym = {'BABY SETTING': 'BABYSITTER'}
new_stop_words = ['owner']  # 'owner'

######################## correct spelling error#######
# from __future__ import division
# %pylab inline
import re
import math, os
import string
from collections import Counter

# https://github.com/nirajdevpandey/spelling-correction-nltk/blob/master/Spelling%2Bchecker%2B.ipynb

# Windows directory
# os.chdir(r'C:\Users\hbao\Downloads\NOC')

# Linux directory
# os.chdir(r'/home/sadnan/PycharmProjects/noccodeproject')
# TEXT = open('train.txt').read()
# TEXT = open('resources/nocjobtitle.txt').read()
# here() points to the project root directory
TEXT = open(here() / 'resources' / 'nocjobtitle.txt').read()

# set the title of the sheet to process
SHEET_TITLE = 'Service Advisor'


def tokens(text):
    "List all the word tokens (consecutive letters) in a text. Normalize to lowercase."
    return re.findall('[a-z]+', text.lower())


def sample(bag, n=10):
    "Sample a random n-word sentence from the model described by the bag of words."
    return ' '.join(random.choice(bag) for _ in range(n))


def correct(word):
    "Find the best spelling correction for this word."
    # Prefer edit distance 0, then 1, then 2; otherwise default to word itself.

    candidates = (known(edits0(word)) or
                  known(edits1(word)) or
                  known(edits2(word)) or
                  [word])
    return max(candidates, key=COUNTS.get)


def known(words):
    "Return the subset of words that are actually in the dictionary."
    return {w for w in words if w in COUNTS}


def edits0(word):
    "Return all strings that are zero edits away from word (i.e., just word itself)."
    return {word}


def edits2(word):
    "Return all strings that are two edits away from this word."
    return {e2 for e1 in edits1(word) for e2 in edits1(e1)}


def edits1(word):
    "Return all strings that are one edit away from this word."
    pairs = splits(word)
    deletes = [a + b[1:] for (a, b) in pairs if b]
    transposes = [a + b[1] + b[0] + b[2:] for (a, b) in pairs if len(b) > 1]
    replaces = [a + c + b[1:] for (a, b) in pairs for c in alphabet if b]
    inserts = [a + c + b for (a, b) in pairs for c in alphabet]
    return set(deletes + transposes + replaces + inserts)


def splits(word):
    "Return a list of all possible (first, rest) pairs that comprise word."
    return [(word[:i], word[i:])
            for i in range(len(word) + 1)]


alphabet = 'abcdefghijklmnopqrstuvwxyz'


def correct_text(text):
    "Correct all the words within a text, returning the corrected text."
    return re.sub('[a-zA-Z]+', correct_match, text)


def correct_match(match):
    "Spell-correct word in match, and preserve proper upper/lower/title case."
    word = match.group()
    return case_of(word)(correct(word.lower()))


def case_of(text):
    "Return the case-function appropriate for text: upper, lower, title, or just str."
    return (str.upper if text.isupper() else
            str.lower if text.islower() else
            str.title if text.istitle() else
            str)


WORDS = tokens(TEXT)
COUNTS = Counter(WORDS)


#################################################################

def exact_match(pattern, titles):
    result = []
    title_list = [title.strip(' ') for title in titles.split(';')]
    p = re.compile(r'\b' + pattern + r'\b')
    result = list(filter(p.fullmatch, title_list))  # exact match
    weight = 100
    # if not result: #for the minor spelling error, for example 'constunction' -> 'construction'
    #    result = get_close_matches(pattern, title_list,n=1,cutoff=0.9)
    #    weight = 95

    if result:
        result.insert(0, weight)
    return result


# for the minor spelling error, for example 'Software Programer' -> 'Software Programmer'
def minor_exact_match(pattern, titles):
    result = []
    title_list = [title.strip(' ') for title in titles.split(';')]
    p = re.compile(r'\b' + pattern + r'\b')
    # result = list(filter(p.fullmatch,title_list)) #exact match
    # for the minor spelling error, for example 'constunction' -> 'construction'
    result = get_close_matches(pattern, title_list, n=1, cutoff=0.9)
    weight = 95

    if result:
        result.insert(0, weight)
    return result


def like_match(pattern, titles):
    result = []
    title_list = [title.strip(' ') for title in titles.split(';')]
    p = re.compile(r'\b' + pattern + r'\b')
    result = list(filter(p.search, title_list))  # like match
    weight = 80
    if result:
        result.insert(0, weight)
    return result


def near_match_sameorder(pattern, titles):
    result = []
    title_list = [title.strip(' ') for title in titles.split(';')]
    # p = re.compile(r'\b'+pattern+r'\b')
    pattern1 = '.*' + pattern.replace(' ', '.*?')  # near match, key words in same order
    near_reg = re.compile(pattern1)
    result = list(filter(near_reg.search, title_list))
    weight = 70
    if result:
        result.insert(0, weight)
    return result


def near_match_differentorder(pattern, titles):  # near match, key words in different order,not technicoly
    result = []
    title_list = [title.strip(' ') for title in titles.split(';')]
    pattern_list = pattern.split(' ')
    near_title_list = title_list[:]
    near_flag = False
    for i in range(len(pattern_list)):
        near_match = re.compile(pattern_list[i])
        near_title_list = list(filter(near_match.search, near_title_list))
        near_flag = True
    if near_title_list and near_flag:
        result = near_title_list
        weight = 65
    if result:
        result.insert(0, weight)
    return result


def any_match(pattern, titles):
    result = []
    title_list = [title.strip(' ') for title in titles.split(';')]
    pattern_list = pattern.split(' ')
    any_flag = True
    for i in range(len(pattern_list)):
        if not re.search(pattern_list[i], titles):
            any_flag = False
            break
    if any_flag:
        any_match = re.compile(pattern_list[0])
        result = list(filter(any_match.search, title_list))
        weight = 60
    if result:
        result.insert(0, weight)
    return result


# only match one noun
def weak_match(pattern, titles):
    result = []
    title_list = [title.strip(' ') for title in titles.split(';')]
    pattern_list = pattern.split(' ')
    for i in range(len(pattern_list)):
        if re.search(pattern_list[i], titles):
            weak_match = re.compile(pattern_list[i])
            result = list(filter(weak_match.search, title_list))
            weight = 20
    if result:
        result.insert(0, weight)
    return result


def search_description(pattern, titles, unit_title, lead_statment, requiremnt, duty):
    result = []
    title_list = [title.strip(' ') for title in titles.split(';')]
    pattern_des = '.*' + pattern.replace(' ', '.*?')  # search by description
    des_reg = re.compile(pattern_des)

    if des_reg.search(unit_title):
        result = title_list[0:2]
        weight = 30
    elif des_reg.search(lead_statment):
        result = title_list[0:2]
        weight = 30
    elif des_reg.search(requiremnt):
        result = title_list[0:2]
        weight = 30
    elif des_reg.search(duty):
        result = title_list[0:2]
        weight = 30

    if result:
        result.insert(0, weight)
    return result


# match industry key words in the results, return result with most matched
def match_results_industry_count(results, industry):
    result_industry = []
    matched_number_dict = {}  # matched numbers in each sub list
    pattern = '.*' + industry.replace(' ', '.*?')
    p = re.compile(r'\b' + industry + r'\b')
    words_num = len(industry.split())
    # p = re.compile(industry)
    # result = list(filter(p.search,industry)) # like match
    for i in range(len(results)):
        if results[i][0] == max(results)[0]:
            # print(match_result[i][1:len(match_result[1])-1])
            result = list(filter(p.search, results[i][1:len(results[i]) - 1]))
            if result:
                if words_num > 1:  # if more than one industry words, count the matched number
                    matched_number_dict[i] = len(p.findall(' '.join(results[i][1:len(results[i]) - 1])))
                else:
                    result_industry.append(results[i])
    if result and words_num > 1:
        max_value = max(matched_number_dict.values())
        for key, value in matched_number_dict.items():
            if value == max_value:
                result_industry.append(results[key])
    return result_industry


'''
def match_results_industry(results, industry):
    result_industry = []
    matched_number_dict = {}  # matched numbers in each sub list
    pattern = '.*'+industry.replace(' ','.*?')
    p = re.compile(r'\b'+industry+r'\b')
    words_num = len(industry.split())
    #p = re.compile(industry)
    #result = list(filter(p.search,industry)) # like match
    for i in range(len(results)):        
        if results[i][0] == max(results)[0]:
            #print(match_result[i][1:len(match_result[1])-1])
            result = list(filter(p.search,results[i][1:len(results[i])-1]))
            if result:
                result_industry.append(results[i])

    return result_industry
'''


def match_results_industry(results, industry):
    result_industry = []
    matched_number_dict = {}  # matched numbers in each sub list
    industries = []
    pattern = '.*' + industry.replace(' ', '.*?')
    p = re.compile(r'\b' + industry + r'\b')
    words_num = len(industry.split())
    # p = re.compile(industry)
    # result = list(filter(p.search,industry)) # like match
    for i in range(len(results)):
        if results[i][0] == max(results)[0]:
            # print(match_result[i][1:len(match_result[1])-1])
            result = list(filter(p.search, results[i][1:len(results[i]) - 1]))
            if result:
                result_industry.append(results[i])
    split_list = ['-', '/', ',', '\(', ]
    # split industry and filter by each word, find the most match number of all industry words
    if not result_industry and any(split_str in industry for split_str in split_list):
        if '/' in industry:
            industries = industry.split('/')
        elif '-' in industry:
            industries = industry.split('-')
        elif ',' in industry:
            industries = industry.split(',')
        elif '(' in industry:
            industries = industry.split('(')
        for k in range(len(industries)):
            # initialize the dictionary for adding later
            p1 = re.compile(r'\b' + industries[k] + r'\b')
            for j in range(len(results)):
                if results[j][0] == max(results)[0]:
                    result = list(filter(p1.search, results[j][1:len(results[j]) - 1]))
                    if result:
                        if j not in matched_number_dict.keys():
                            matched_number_dict[j] = 0
                        matched_number_dict[j] = matched_number_dict[j] + len(
                            p1.findall(' '.join(results[j][1:len(results[j]) - 1])))
        if matched_number_dict:
            max_value = max(matched_number_dict.values())
            for key, value in matched_number_dict.items():
                if value == max_value:
                    result_industry.append(results[key])
    return result_industry


# match results' group title by job title key words
def match_results_group_title(results, job_title):
    result_industry = []
    pattern = '.*' + job_title.replace(' ', '.*?')
    p = re.compile(r'\b' + job_title + r'\b')
    for i in range(len(results)):
        if results[i][0] == max(results)[0]:
            # print(match_result[i][1:len(match_result[1])-1])
            result = p.search(df.loc[df['Noc_code'] == results[i][-1], 'group_title'].iloc[0].lower())
            if result:
                result_industry.append(results[i])
    if result_industry:
        return result_industry
    else:
        return results


# match results' description by industry key words
def match_results_leadstatement(results, industry):
    result_industry = []
    pattern = '.*' + industry.replace(' ', '.*?')
    p = re.compile(r'\b' + industry + r'\b')
    # p = re.compile(industry)
    # result = list(filter(p.search,industry)) # like match
    for i in range(len(results)):
        if results[i][0] == max(results)[0]:
            # print(match_result[i][1:len(match_result[1])-1])
            result = p.search(df.loc[df['Noc_code'] == results[i][-1], 'lead_statement'].iloc[0].lower())
            if result:
                result_industry.append(results[i])
            else:
                result = p.search(df.loc[df['Noc_code'] == results[i][-1], 'main_duties'].iloc[0].lower())
                if result:
                    result_industry.append(results[i])
                else:
                    result = p.search(df.loc[df['Noc_code'] == results[i][-1], 'Emp_req'].iloc[0].lower())
                    if result:
                        result_industry.append(results[i])
    if result_industry:
        return result_industry
    else:
        return results


# match split title results' description by industry key words
def match_split_result_desc(results, industry):
    pattern = '.*' + industry.replace(' ', '.*?')
    p = re.compile(r'\b' + industry + r'\b')
    # p = re.compile(industry)
    # result = list(filter(p.search,industry)) # like match
    result = p.search(df.loc[df['Noc_code'] == results[-1], 'lead_statement'].iloc[0].lower())
    if not result:
        result = p.search(df.loc[df['Noc_code'] == results[-1], 'main_duties'].iloc[0].lower())
    if not result:
        result = p.search(df.loc[df['Noc_code'] == results[-1], 'Emp_req'].iloc[0].lower())
    return result


def get_position(a, b):
    a1 = ''
    a2 = ''
    a3 = ''
    a4 = ''
    f = False
    if a[0] == b[0]:
        a1 = a[0]
        f = True
    if a[1] == b[1] and f:
        a2 = a[1]
        f = True
    else:
        f = False
    if a[2] == b[2] and f:
        a3 = a[2]
        f = True
    else:
        f = False
    if a[3] == b[3] and f:
        a4 = a[3]
    else:
        f = False
    return a1, a2, a3, a4


def removestopwords(sentence):
    stop_words = stopwords.words('english')
    # stop_words.extend(new_stop_words) #add new stop words
    stop_words = set(stop_words)
    token_words = word_tokenize(sentence.lower())

    after_sentence = []
    for word in token_words:
        if word not in stop_words:
            after_sentence.append(word)
            after_sentence.append(" ")
    return "".join(after_sentence)


def stemsentence(sentence):
    token_words = word_tokenize(sentence)
    token_words
    stem_sentence = []
    for word in token_words:
        stem_sentence.append(porter.stem(word))
        stem_sentence.append(" ")
    return "".join(stem_sentence).strip(' ')


def get_sub_df(df_orig, flag):
    df_sub = pd.DataFrame(
        columns=['Participant ID', 'Current Job Title', 'NOC code', 'Current Industry', 'origin job title', 'origin industry'])
    if flag == CORRECT:
        for i in range(len(df_orig)):
            industry = df_orig.loc[df_orig.index[i], 'Current Industry']
            job_title = df_orig.loc[df_orig.index[i], 'Current Job Title']
            job_title_check = df_orig.loc[df_orig.index[i], 'correct job title']
            if job_title.strip(' '):
                df_sub = df_sub.append({'Current Job Title': job_title_check,
                                        'NOC code': df_orig.loc[df_orig.index[i], 'NOC code'],
                                        'Current Industry': industry, 'origin job title': job_title,
                                        'origin industry': industry}, ignore_index=True)
    # remove stop words and store the origin title and industry
    if flag == REMOVE_ST:
        for i in range(len(df_orig)):
            industry = df_orig.loc[df_orig.index[i], 'Current Industry']
            job_title = df_orig.loc[df_orig.index[i], 'Current Job Title']
            if job_title.strip(' '):
                df_sub = df_sub.append({'Current Job Title': removestopwords(job_title),
                                        'NOC code': df_orig.loc[df_orig.index[i], 'NOC code'],
                                        'Current Industry': industry, 'origin job title': job_title,
                                        'origin industry': industry}, ignore_index=True)
    # exchange the job title and industry, store the origin title and industry
    if flag == BY_INDUSTRY:
        for i in range(len(df_orig)):
            industry = df_orig.loc[df_orig.index[i], 'Current Industry']
            job_title = df_orig.loc[df_orig.index[i], 'Current Job Title']

            # industry_check = correct_text(industry)
            if industry.strip(' ') and job_title.strip(' '):  # already searched industry when title is empty

                df_sub = df_sub.append({'Current Job Title': industry,
                                        'NOC code': df_orig.loc[df_orig.index[i], 'NOC code'],
                                        'Current Industry': job_title, 'origin job title': job_title,
                                        'origin industry': industry}, ignore_index=True)
    # extract nouns from titles
    if flag == NOUN:
        for i in range(len(df_orig)):
            industry = df_orig.loc[df_orig.index[i], 'Current Industry']
            job_title = df_orig.loc[df_orig.index[i], 'Current Job Title']
            text = word_tokenize(job_title)
            # print(nltk.pos_tag(text) )
            job_title_noun = [word for (word, pos) in nltk.pos_tag(text) if pos[:2] == 'NN']
            if job_title.strip(' '):
                df_sub = df_sub.append({'Current Job Title': ' '.join(job_title_noun),
                                        'NOC code': df_orig.loc[df_orig.index[i], 'NOC code'],
                                        'Current Industry': industry, 'origin job title': job_title,
                                        'origin industry': industry}, ignore_index=True)
                # stemming the job title and store the origin title and industry
    if flag == STEM_WORD:
        for i in range(len(df_orig)):
            industry = df_orig.loc[df_orig.index[i], 'Current Industry']
            job_title = df_orig.loc[df_orig.index[i], 'Current Job Title']
            # .strip(' ').strip('-').strip('\\').strip('/').strip(',')
            # job_title_check = df_orig.loc[df_orig.index[i],'correct job title']
            if job_title.strip(' '):
                df_sub = df_sub.append({'Current Job Title': stemsentence(job_title),
                                        'NOC code': df_orig.loc[df_orig.index[i], 'NOC code'],
                                        'Current Industry': industry, 'origin job title': job_title,
                                        'origin industry': industry}, ignore_index=True)

    return df_sub


def search_skilltype(results, keywords):
    result_skilltypes = []

    # pattern = '.*'+industry.replace(' ','.*?')
    p = re.compile(keywords)
    # breakpoint()
    for i in range(len(results)):
        if results[i][0] == max(results)[0]:
            result = p.search(df_skilltype.loc[df_skilltype['skilltype_code'] == int(str(results[i][-1]).zfill(4)[0:1]),
                                               'skilltype_title'].iloc[0].lower())

        if result:
            result_skilltypes.append(results[i])
        '''
        else:
            result = p.search(df_skilltype.loc[df_skilltype['skilltype_code']==int(str(results[i][-1]).zfill(4)[0:1]),
                                         'skilltype_desc'].iloc[0].lower())
        if result:
            result_skilltypes.append(results[i])
        '''
    if result_skilltypes:
        return result_skilltypes
    else:
        return results


def search_majorgroup(results, keywords):
    result_majorgroup = []

    # pattern = '.*'+industry.replace(' ','.*?')
    p = re.compile(keywords)

    for i in range(len(results)):
        if results[i][0] == max(results)[0]:
            result = p.search(df_mag.loc[df_mag['majorgroup_code'] == '\'' + str(results[i][-1]).zfill(4)[0:2],
                                         'majorgroup_title'].iloc[0].lower())
        if result:
            result_majorgroup.append(results[i])

    if result_majorgroup:
        return result_majorgroup
    else:
        return results


def search_minorgroup(results, keywords):
    result_minorgroup = []

    # pattern = '.*'+industry.replace(' ','.*?')
    p = re.compile(keywords)
    try:
        for i in range(len(results)):
            if results[i][0] == max(results)[0]:
                result = p.search(df_mig.loc[df_mig['minorgroup_code'] == '\'' + str(results[i][-1]).zfill(4)[0:3],
                                             'minorgroup_title'].iloc[0].lower())
            if result:
                result_minorgroup.append(results[i])
    except:
        None

    if result_minorgroup:
        return result_minorgroup
    else:
        return results


# match_type: 1 -> exact_match; 2 -> minor_exact_match
def get_noc_code(df_excel, df_re, match_type=1, run_note=None):
    for i in range(len(df_excel)):
        count = 0
        match_result = []
        match_by_industry = []
        match_lead_by_industry = []
        match_by_group_title = []
        match_by_skill_type = []
        match_by_major_group = []
        match_by_minor_group = []
        matched_titles = []  # for analysing the results with same weight
        matched_codes = []
        type_code = []  # skill type code
        major_code = []  # major group code
        minor_code = []  # minor group code
        noc_code_known = ''
        split_title_result = []  # after spliting title,only match title not industry
        split_title_idx = []

        participant_id = df_excel.loc[df_excel.index[i], 'Participant ID'] # adding Parcipitant ID column
        current_job_title = df_excel.loc[df_excel.index[i], 'Current Job Title']
        provided_job_title = current_job_title  # in order to be the same as input
        current_job_titles = ''  # split title
        current_noc_code = df_excel.loc[df_excel.index[i], 'NOC code']
        current_industry = df_excel.loc[df_excel.index[i], 'Current Industry']
        try:
            if run_note == SPLIT_TITLE or run_note == SPLIT_INDUSTRY:

                if '/' in current_job_title:
                    current_job_titles = current_job_title.split('/')
                elif '-' in current_job_title:
                    current_job_titles = current_job_title.split('-')
                elif ',' in current_job_title:
                    current_job_titles = current_job_title.split(',')
                elif '(' in current_job_title:
                    current_job_titles = current_job_title.split('(')
                for k in range(len(current_job_titles)):
                    for j in range(len(df)):
                        lead_stm = df.loc[df.index[j], 'lead_statement'].lower()
                        man_duty = df.loc[df.index[j], 'main_duties'].lower()
                        emp_req = df.loc[df.index[j], 'Emp_req'].lower()
                        unit_title = df.loc[df.index[j], 'group_title'].lower()
                        noc_code_source = df.loc[df.index[j], 'Noc_code']
                        if current_job_titles[k].strip(' '):
                            if match_type == 2:  # minor spelling error match
                                result = minor_exact_match(
                                    correct_text(current_job_titles[k]).strip(' ').replace(')', '').lower(),
                                    df.loc[df.index[j], 'job_title'].lower())
                            elif match_type == 3:  # like match
                                result = like_match(
                                    correct_text(current_job_titles[k]).strip(' ').replace(')', '').lower(),
                                    df.loc[df.index[j], 'job_title'].lower())
                            else:
                                result = exact_match(
                                    correct_text(current_job_titles[k]).strip(' ').replace(')', '').lower(),
                                    df.loc[df.index[j], 'job_title'].lower())

                        if result:
                            result.append(noc_code_source)
                            if match_split_result_desc(result,
                                                       current_industry.lower()):  # industry is also in description
                                match_result.append(result)
                                current_job_title = current_job_titles[k]  # search key values
                                # print('match_type',match_type,current_job_title,result)
                                break
                            else:
                                split_title_result.append(result)
                                split_title_idx.append(k)

                    if match_result:
                        break  #
                    elif split_title_result:
                        match_result.append(split_title_result[0])
                        current_job_title = current_job_titles[split_title_idx[0]]  # search key values
            else:

                for j in range(len(df)):
                    lead_stm = df.loc[df.index[j], 'lead_statement'].lower()
                    man_duty = df.loc[df.index[j], 'main_duties'].lower()
                    emp_req = df.loc[df.index[j], 'Emp_req'].lower()
                    unit_title = df.loc[df.index[j], 'group_title'].lower()
                    noc_code_source = df.loc[df.index[j], 'Noc_code']
                    if current_job_title.strip(' ') or current_industry.strip(
                            ' '):  # neither job title nor industry are null
                        if not current_job_title.strip(' '):
                            current_job_title = current_industry
                        if match_type == 2:  # minor spelling error match
                            result = minor_exact_match(current_job_title.strip(' ').lower(),
                                                       df.loc[df.index[j], 'job_title'].lower())
                        elif match_type == 3:  # like match
                            result = like_match(current_job_title.strip(' ').lower(),
                                                df.loc[df.index[j], 'job_title'].lower())
                        elif match_type == 4:  # near match in same order
                            result = near_match_sameorder(current_job_title.strip(' ').lower(),
                                                          df.loc[df.index[j], 'job_title'].lower())
                        elif match_type == 5:  # near match in different order
                            result = near_match_differentorder(current_job_title.strip(' ').lower(),
                                                               df.loc[df.index[j], 'job_title'].lower())
                        elif match_type == 6:  # any match
                            result = any_match(current_job_title.strip(' ').lower(),
                                               df.loc[df.index[j], 'job_title'].lower())
                        elif match_type == 7:  # search descriptions
                            result = search_description(current_job_title.strip(' ').lower(),
                                                        df.loc[df.index[j], 'job_title'].lower(), unit_title, lead_stm,
                                                        emp_req, man_duty)
                        elif match_type == 8:  # weak match
                            result = weak_match(current_job_title.strip(' ').lower(),
                                                df.loc[df.index[j], 'job_title'].lower())
                        else:
                            result = exact_match(current_job_title.strip(' ').lower(),
                                                 df.loc[df.index[j], 'job_title'].lower())

                    if result:
                        result.append(noc_code_source)
                        match_result.append(result)
        except Exception as e:
            match_result = []
            # print('error in match',i,current_job_title, str(e))
            None

        try:
            if run_note:
                current_noc_code = current_noc_code.strip('\'')  # added ' to the code after first time running
            if current_noc_code.strip(' '):
                noc_code_known = str(current_noc_code).zfill(4)
            else:
                noc_code_known = current_noc_code.strip(' ')

            if match_result or type_code:
                if len(match_result) > 1:  # filter result
                    # print('skill')
                    # breakpoint()
                    match_by_skill_type = search_skilltype(match_result, current_job_title.strip(' ').lower())
                    if match_by_skill_type:
                        match_result = match_by_skill_type
                    # print('skill-1')
                    match_by_major_group = search_majorgroup(match_result, current_job_title.strip(' ').lower())
                    if match_by_major_group:
                        match_result = match_by_major_group
                    # print('skill-2')
                    match_by_minor_group = search_minorgroup(match_result, current_job_title.strip(' ').lower())
                    if match_by_minor_group:
                        match_result = match_by_minor_group

                    match_by_group_title = match_results_group_title(match_result, current_job_title.strip(' ').lower())
                    if match_by_group_title:
                        match_result = match_by_group_title
                    if len(match_result) > 1 and current_industry.strip(' '):
                        match_by_industry = match_results_industry(match_result,
                                                                   current_industry.lower())  # match by industry
                        if match_by_industry:
                            match_result = match_by_industry
                    if len(match_result) > 1 and current_industry.strip(' '):
                        match_lead_by_industry = match_results_leadstatement(match_result,
                                                                             current_industry.lower())  # match lead statements by industry
                        if match_lead_by_industry:
                            match_result = match_lead_by_industry

                if match_result:
                    max_match_result = max(match_result, key=len)  # get the max weight

                    noc_code = str(max_match_result[-1]).zfill(4)
                    # print('code_list',i,code_list[i])

                    # if run_note==MINOR_MATCH:
                    #    breakpoint()
                    # print('noc_code_known',noc_code_known)
                    fp = ''
                    sp = ''
                    tp = ''
                    frp = ''
                    if noc_code_known:
                        fp, sp, tp, frp = get_position(noc_code, noc_code_known)

                    for k in range(len(match_result)):
                        # breakpoint()
                        if max(match_result)[0] == match_result[k][0]:
                            count = count + 1
                            matched_titles.append(match_result[k])
                            matched_codes.append(match_result[k][-1])

                    match_result_title = max_match_result[1]
                    match_result_weight = max_match_result[0]
                else:

                    match_result_title = ''
                    match_result_weight = ''

                if not run_note:
                    df_re = df_re.append(
                        {'Participant ID': participant_id,
                         'Current Job Title': provided_job_title, 
                         'NOC code by program': '\'' + noc_code,
                         'noc_title': match_result_title, 
                         'weight': match_result_weight,
                         'NOC code': '\'' + noc_code_known,
                         'Current Industry': current_industry, 'first position': fp, 'second position': sp,
                         'third position': tp, 'fourth position': frp, 'note': '',
                         'matched Noc codes': ['\'' + str(c).zfill(4) for c in matched_codes],
                         'searched key words': current_job_title
                         },
                        ignore_index=True)  # 'matched titles':matched_titles

                else:
                    if run_note == MINOR_MATCH or run_note == SPLIT_TITLE or run_note == ORIGINAL:
                        origin_job_title = provided_job_title
                        origin_industry = current_industry

                    else:
                        origin_job_title = df_excel.loc[df_excel.index[i], 'origin job title']
                        origin_industry = df_excel.loc[df_excel.index[i], 'origin industry']

                    df_re.loc[(df_re['Current Job Title'] == origin_job_title) & (
                                df_re['Current Industry'] == origin_industry),
                              ['NOC code by program', 'noc_title', 'weight', 'NOC code',
                               'first position', 'second position', 'third position', 'fourth position',
                               'note', 'matched Noc codes', 'searched key words']] = ['\'' + noc_code,
                                                                                      match_result_title,
                                                                                      match_result_weight,
                                                                                      '\'' + current_noc_code, fp, sp,
                                                                                      tp, frp, run_note,
                                                                                      ['\'' + str(c).zfill(4) for c in
                                                                                       matched_codes],
                                                                                      current_job_title]  # ,'matched titles' ,str(matched_titles)

            else:
                if not run_note:
                    df_re = df_re.append({'Participant ID': participant_id,
                                          'Current Job Title': provided_job_title, 
                                          'NOC code by program': '',
                                          'noc_title': '', 'weight': '',
                                          'NOC code': '\'' + noc_code_known,
                                          'Current Industry': current_industry, 'first position': '',
                                          'second position': '',
                                          'third position': '', 'fourth position': '', 'note': '',
                                          'matched Noc codes': '', 'searched key words': ''
                                          },
                                         ignore_index=True)  # 'matched titles':''



        except Exception as e:
            # print('error:',i, current_job_title,str(e))
            None

    return df_re


df = pd.read_csv(here() / 'resources' / 'noc_data_get_byws_dealing_slash.csv', encoding="ISO-8859-1")
file = here() / 'data' / 'NOC-spreadsheet.xlsx'
MINOR_MATCH = 'minor match'
SPLIT_TITLE = 'split title'
CORRECT = 'correct spelling error'
REMOVE_ST = 'remove stop words'
BY_INDUSTRY = 'by industry'
NOUN = 'extract nouns'
STEM_WORD = 'stemming word'
SPLIT_INDUSTRY = 'split industry'
ORIGINAL = 'original title'
WEAK = 'matched by one noun'
# title_data = pd.ExcelFile(file)

# print(title_data.sheet_names)
start = time.time()

df_skilltype = pd.read_csv(here() / 'resources' / 'NOC_skilltype.csv')
df_mag = pd.read_csv(here() / 'resources' / 'NOC_majorgroup.csv')
df_mig = pd.read_csv(here() / 'resources' / 'NOC_minorgroup.csv')

df_excel = pd.read_excel(file, sheet_name=SHEET_TITLE, header=0,
                         converters={'NOC code': str, 'Current Job Title': str, 'Current Industry': str},
                         na_filter=False)  # ,na_filter = False
df_re = pd.DataFrame(columns=['Current Job Title', 'NOC code by program', 'noc_title', 'weight', 'NOC code',
                              'Current Industry', 'first position', 'second position', 'third position',
                              'fourth position',
                              'note', 'matched Noc codes', 'searched key words'])  # ,'matched titles'
# extract nouns from title
import nltk, re, pprint
from nltk import word_tokenize

nltk.download('averaged_perceptron_tagger')

# first search by original title
df_re = get_noc_code(df_excel=df_excel, df_re=df_re)
print('1 search finish')
df_minor_match = df_re.loc[df_re['NOC code by program'] == '']
df_re = get_noc_code(df_excel=df_minor_match, df_re=df_re, match_type=2, run_note=MINOR_MATCH)
print('2 search finish')
for i in range(1, 8):
    if i > 2:  # original title match begin from like match
        df_empty = df_re.loc[df_re['NOC code by program'] == '']
        df_re = get_noc_code(df_excel=df_empty, df_re=df_re, match_type=i, run_note=ORIGINAL)

    # second search, split tilte, exact match
    df_empty = df_re.loc[df_re['NOC code by program'] == '']
    df_split_title = df_empty.loc[df_empty['Current Job Title'].str.contains('-|/|,|\(', regex=True)]
    df_re = get_noc_code(df_excel=df_split_title, df_re=df_re, match_type=i, run_note=SPLIT_TITLE)

    # print('second search finish')
    # search by industry
    # df_empty = get_sub_df(df_re.loc[df_re['NOC code by program']==''],BY_INDUSTRY)
    # df_re=get_noc_code(df_excel=df_empty,df_re=df_re,match_type=i,run_note=BY_INDUSTRY)
    # print('3 search finish ')

    # search by nouns
    # df_empty = get_sub_df(df_re[df_re['NOC code by program']==''],NOUN)
    # df_re=get_noc_code(df_excel=df_empty,df_re=df_re,match_type=i,run_note=NOUN)

    # remove stop word
    df_empty = get_sub_df(df_re.loc[df_re['NOC code by program'] == ''], REMOVE_ST)
    df_re = get_noc_code(df_excel=df_empty, df_re=df_re, match_type=i, run_note=REMOVE_ST)
    # print('seven search finish ')

    # stemming word
    df_empty = get_sub_df(df_re.loc[df_re['NOC code by program'] == ''], STEM_WORD)
    df_re = get_noc_code(df_excel=df_empty, df_re=df_re, match_type=i, run_note=STEM_WORD)

    # search by nouns
    df_empty = get_sub_df(df_re[df_re['NOC code by program'] == ''], NOUN)
    df_re = get_noc_code(df_excel=df_empty, df_re=df_re, match_type=i, run_note=NOUN)

    print(i, 'round finish ')

# last search industry
for i in range(1, 8):
    # search by industry
    df_empty = get_sub_df(df_re.loc[df_re['NOC code by program'] == ''], BY_INDUSTRY)
    df_re = get_noc_code(df_excel=df_empty, df_re=df_re, match_type=i, run_note=BY_INDUSTRY)

    # search by spliting industry
    df_empty = df_re.loc[df_re['NOC code by program'] == '']
    df_need_split_industry = df_empty.loc[df_empty['Current Industry'].str.contains('-|/|,|\(', regex=True)]
    df_split_industry = get_sub_df(df_need_split_industry, BY_INDUSTRY)
    df_re = get_noc_code(df_excel=df_split_industry, df_re=df_re, match_type=i, run_note=SPLIT_INDUSTRY)

# weak match
df_empty = get_sub_df(df_re[df_re['NOC code by program'] == ''], NOUN)
df_re = get_noc_code(df_excel=df_empty, df_re=df_re, match_type=8, run_note=WEAK)

# correct spelling error
for i in range(len(df_re)):
    if df_re.loc[df_re.index[i], 'NOC code by program'] == '':
        job = str(df_re.loc[df_re.index[i], 'Current Job Title'])
        indus = str(df_re.loc[df_re.index[i], 'Current Industry'])
        df_re.loc[df_re.index[i], 'correct job title'] = correct_text(job)
        df_re.loc[df_re.index[i], 'correct industry'] = correct_text(indus)

# correcting spelling error
for i in range(3, 7):
    df_empty = get_sub_df(df_re.loc[df_re['NOC code by program'] == ''], CORRECT)
    df_re = get_noc_code(df_excel=df_empty, df_re=df_re, match_type=i, run_note=CORRECT)

df_re.to_csv(here() / 'title_noc_result_byprogram.csv', sep=',')

end = time.time()
print('time', (end - start) / 60)


# In[ ]:


def match_results_industry(results, industry):
    result_industry = []
    matched_number_dict = {}  # matched numbers in each sub list
    industries = []
    pattern = '.*' + industry.replace(' ', '.*?')
    p = re.compile(r'\b' + industry + r'\b')
    words_num = len(industry.split())
    # p = re.compile(industry)
    # result = list(filter(p.search,industry)) # like match
    for i in range(len(results)):
        if results[i][0] == max(results)[0]:
            # print(match_result[i][1:len(match_result[1])-1])
            result = list(filter(p.search, results[i][1:len(results[i]) - 1]))
            if result:
                result_industry.append(results[i])
    split_list = ['-', '/', ',', '\(', ]
    # split industry and filter by each word, find the most match number of all industry words
    if not result_industry and any(split_str in industry for split_str in split_list):
        if '/' in industry:
            industries = industry.split('/')
        elif '-' in industry:
            industries = industry.split('-')
        elif ',' in industry:
            industries = industry.split(',')
        elif '(' in industry:
            industries = industry.split('(')
        for k in range(len(industries)):
            # initialize the dictionary for adding later
            p1 = re.compile(r'\b' + industries[k] + r'\b')
            for j in range(len(results)):
                if results[j][0] == max(results)[0]:
                    result = list(filter(p1.search, results[j][1:len(results[j]) - 1]))
                    if result:
                        if j not in matched_number_dict.keys():
                            matched_number_dict[j] = 0
                        matched_number_dict[j] = matched_number_dict[j] + len(
                            p1.findall(' '.join(results[j][1:len(results[j]) - 1])))
        if matched_number_dict:
            max_value = max(matched_number_dict.values())
            for key, value in matched_number_dict.items():
                if value == max_value:
                    result_industry.append(results[key])
    return result_industry


# In[ ]:


import re
import math, os
import string
from collections import Counter

# https://github.com/nirajdevpandey/spelling-correction-nltk/blob/master/Spelling%2Bchecker%2B.ipynb

# Windows directory
# os.chdir(r'C:\Users\hbao\Downloads\NOC')

# Linux directory
# os.chdir(r'/home/sadnan/PycharmProjects/noccodeproject')

# TEXT = open('train.txt').read()
# TEXT = open('resources/nocjobtitle.txt').read()
TEXT = open(here() / 'resources' / 'nocjobtitle.txt').read()

def tokens(text):
    "List all the word tokens (consecutive letters) in a text. Normalize to lowercase."
    return re.findall('[a-z]+', text.lower())


def sample(bag, n=10):
    "Sample a random n-word sentence from the model described by the bag of words."
    return ' '.join(random.choice(bag) for _ in range(n))


def correct(word):
    "Find the best spelling correction for this word."
    # Prefer edit distance 0, then 1, then 2; otherwise default to word itself.

    candidates = (known(edits0(word)) or
                  known(edits1(word)) or
                  known(edits2(word)) or
                  [word])
    return max(candidates, key=COUNTS.get)


def known(words):
    "Return the subset of words that are actually in the dictionary."
    return {w for w in words if w in COUNTS}


def edits0(word):
    "Return all strings that are zero edits away from word (i.e., just word itself)."
    return {word}


def edits2(word):
    "Return all strings that are two edits away from this word."
    return {e2 for e1 in edits1(word) for e2 in edits1(e1)}


def edits1(word):
    "Return all strings that are one edit away from this word."
    pairs = splits(word)
    deletes = [a + b[1:] for (a, b) in pairs if b]
    transposes = [a + b[1] + b[0] + b[2:] for (a, b) in pairs if len(b) > 1]
    replaces = [a + c + b[1:] for (a, b) in pairs for c in alphabet if b]
    inserts = [a + c + b for (a, b) in pairs for c in alphabet]
    return set(deletes + transposes + replaces + inserts)


def splits(word):
    "Return a list of all possible (first, rest) pairs that comprise word."
    return [(word[:i], word[i:])
            for i in range(len(word) + 1)]


alphabet = 'abcdefghijklmnopqrstuvwxyz'


def correct_text(text):
    "Correct all the words within a text, returning the corrected text."
    return re.sub('[a-zA-Z]+', correct_match, text)


def correct_match(match):
    "Spell-correct word in match, and preserve proper upper/lower/title case."
    word = match.group()
    return case_of(word)(correct(word.lower()))


def case_of(text):
    "Return the case-function appropriate for text: upper, lower, title, or just str."
    return (str.upper if text.isupper() else
            str.lower if text.islower() else
            str.title if text.istitle() else
            str)


WORDS = tokens(TEXT)
COUNTS = Counter(WORDS)

# In[8]:


correct_text('BED AND BREAKFEST')