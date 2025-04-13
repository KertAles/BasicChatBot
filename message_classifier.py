# -*- coding: utf-8 -*-

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import jellyfish
from datetime import datetime
import pandas as pd

from global_vars import MESSAGES_PATH, CATEGORIES_PATH

"""

Script used to classify the messages into categories(overlap possible) by
finding keywords in the messages. 4 fixed categories were identified +
an undefined category for 'useless' messages.

"""

if __name__ == '__main__' :
    data = pd.read_csv(MESSAGES_PATH, sep=',')
    # remove quotes around messages
    data['message'] = data['message'].apply(lambda x: x[1:-1])
    data['timestamp'] = data['timestamp'].apply(lambda x:
                                                datetime.strptime(x, '%m/%d/%Y').
                                                date().strftime("%Y-%m-%d"))
    
    # chosen keywords
    category_keywords = {'game_issue' : ['game', 'jackpot', 'play'],
            'money_issue' : ['money', 'cash', 'deposit', 'bitcoin', 'bonu', 'fund'],
            'spin_issue' : ['free', 'spin', 'freespin'],
            'account_issue' : ['account', 'login', 'email', 'access']
            }
    
    # words in a message are stemmed, filtered and a jaro similarity
    # is calculated to account for typos.
    stemmer = nltk.stem.PorterStemmer()
    for index, row in data.iterrows():
        words = [stemmer.stem(word) for word in row['message'].split(' ') 
                                     if word not in (stopwords.words('english'))
                                     and len(word) > 1
                                     and not word.isnumeric()]
        relevant_categories = []
        for category in category_keywords :
            for word in words :
                word_similarities = [jellyfish.jaro_similarity(word, keyword)
                                     for keyword in category_keywords[category]]
                
                if max(word_similarities) > 0.8 :
                    relevant_categories.append(category)
                    continue
        
        relevant_categories = list(set(relevant_categories))
        if len(relevant_categories) == 0 :
            relevant_categories.append('undefined')
            
        data.at[index, 'categories'] = ' '.join(relevant_categories)
        
        
    #data.drop('message', axis=1, inplace=True)
    data.to_csv(CATEGORIES_PATH)


