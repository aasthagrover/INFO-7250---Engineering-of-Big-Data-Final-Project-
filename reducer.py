#!/usr/bin/env python

from operator import itemgetter
import sys
import numpy as np
import pandas as pd
import nltk
import yaml
from numpy import average

global yaml

class Splitter(object):
    def __init__(self):
        self.nltk_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
        self.nltk_tokenizer = nltk.tokenize.TreebankWordTokenizer()

    def split(self, text):
        sentences = self.nltk_splitter.tokenize(text)
        tokenized_sentences = [self.nltk_tokenizer.tokenize(sent) for sent in sentences]
        return tokenized_sentences


class POSTagger(object):
    def __init__(self):
        pass
        
    def pos_tag(self, sentences):
        pos = [nltk.pos_tag(sentence) for sentence in sentences]
        #adapt format
        pos = [[(word, word, [postag]) for (word, postag) in sentence] for sentence in pos]
        return pos

def value_of(sentiment):
        if sentiment == 'positive': return 1
        if sentiment == 'negative': return -1
        return 0

def sentiment_score(review):    
        return sum ([value_of(tag) for sentence in dict_tagged_sentences for token in sentence for tag in token[2]])


class DictionaryTagger(object):
    def __init__(self, dictionary_paths):
        files = [open(path, 'r') for path in dictionary_paths]
        dictionaries = [yaml.load(dict_file) for dict_file in files]
        map(lambda x: x.close(), files)
        self.dictionary = {}
        self.max_key_size = 0
        for curr_dict in dictionaries:
            for key in curr_dict:
                if key in self.dictionary:
                    self.dictionary[key].extend(curr_dict[key])
                else:
                    self.dictionary[key] = curr_dict[key]
                    self.max_key_size = max(self.max_key_size, len(key))

    def tag(self, postagged_sentences):
        return [self.tag_sentence(sentence) for sentence in postagged_sentences]

    def tag_sentence(self, sentence, tag_with_lemmas=False):
        tag_sentence = []
        N = len(sentence)
        if self.max_key_size == 0:
            self.max_key_size = N
        i = 0
        while (i < N):
            j = min(i + self.max_key_size, N) #avoid overflow
            tagged = False
            while (j > i):
                expression_form = ' '.join([word[0] for word in sentence[i:j]]).lower()
                expression_lemma = ' '.join([word[1] for word in sentence[i:j]]).lower()
                if tag_with_lemmas:
                    literal = expression_lemma
                else:
                    literal = expression_form
                if literal in self.dictionary:
                    #self.logger.debug("found: %s" % literal)
                    is_single_token = j - i == 1
                    original_position = i
                    i = j
                    taggings = [tag for tag in self.dictionary[literal]]
                    tagged_expression = (expression_form, expression_lemma, taggings)
                    if is_single_token: #if the tagged literal is a single token, conserve its previous taggings:
                        original_token_tagging = sentence[original_position][2]
                        tagged_expression[2].extend(original_token_tagging)
                    tag_sentence.append(tagged_expression)
                    tagged = True
                else:
                    j = j - 1
            if not tagged:
                tag_sentence.append(sentence[i])
                i += 1
        return tag_sentence

current_businessID = None
current_reviewCount = 0
current_rating=0
total_rating=0
average_rating=0
businessID = None
review= None

dicttagger = DictionaryTagger([ 'C:/Users/Neha/Documents/IS Sem 3/Engineering Big Data-7250/Yelp/positive.yml', 'C:/Users/Neha/Documents/IS Sem 3/Engineering Big Data-7250/Yelp//negative.yml'])

# input comes from STDIN
for line in sys.stdin:
    # remove leading and trailing whitespace
    line = line.strip()

    # parse the input we got from mapper.py
    businessID,review= line.split('\t')
    current_rating=0
    average_rating=0.0
    
    splitter = Splitter()
    postagger = POSTagger()
    
    splitted_sentences = splitter.split(review)
    
    #print(splitted_sentences)
    
    pos_tagged_sentences = postagger.pos_tag(splitted_sentences)
    
    #print(pos_tagged_sentences)
    

    dict_tagged_sentences = dicttagger.tag(pos_tagged_sentences)

    #print(dict_tagged_sentences)

    
    current_rating=sentiment_score(dict_tagged_sentences)  
      

    # this IF-switch only works because Hadoop sorts map output
    # by key (here: word) before it is passed to the reducer
    if current_businessID == businessID:
        current_reviewCount += 1
        total_rating=total_rating+current_rating
    else:
        if current_businessID:
            # write result to STDOUT
            average_rating=total_rating/current_reviewCount
            print ('%s\t%s' % (current_businessID, average_rating))
        current_reviewCount = 1
        total_rating=0
        average_rating=0.0
        current_businessID = businessID

# do not forget to output the last word if needed!
if current_businessID == businessID:
    average_rating=total_rating/current_reviewCount
    print ('%s\t%s' % (current_businessID, average_rating))