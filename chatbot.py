# -*- coding: utf-8 -*-

from openai import OpenAI
from sqlite3 import connect
import pandas as pd
from datetime import datetime
import numpy as np

from global_vars import INSTRUCTION_CHECK_FILE, FILTERING_FILE, ANALYSIS_FILE, CATEGORIES_PATH

"""

ChatBot class that contains the API for ChatGPT. Handles 3 types of messages :
    - instruction type identification : determine if 'analysis' or 'filtering'
    is required for the given prompt,
    - filtering : generate an SQL query that can filter the database, use the
    query to make a new dataframe that is saved to an Excel file,
    - analysis : generate an SQL query that can extract some insight, then
    pass the result back to ChatGPT to integrate the data into a sentence.

The class contains a history of filtering and analysis prompts that get passed
to ChatGPT. It remembers 5 previous prompts.

"""

class ChatBot :
    
    def __init__(self, api_key):
        self.client = OpenAI(
          api_key=api_key
        )
        
        # Load the instructions for all task types
        f = open(INSTRUCTION_CHECK_FILE, "r")
        self.instruction_check_prompt = f.read()
        f.close()
        
        f = open(FILTERING_FILE, "r")
        self.filtering_prompt = f.read()
        f.close()
        
        f = open(ANALYSIS_FILE, "r")
        self.analysis_prompt = f.read()
        f.close()
        
        self.instruction_type_history = []
        self.filtering_history = []
        self.analysis_history = []
    
    """
    def get_embedding(self, text, model="text-embedding-3-small") :
        text = text.replace("\n", " ")
        embedding = self.client.embeddings.create(input=[text], model=model).data[0].embedding
        return embedding
    
    def cosine_similarity(self, a, b) :
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
    def rag_search(self, instruction, embeddings) :
        instruction_embedding = chat.get_embedding(instruction)

        embeddings['similarity'] = embeddings['embedding'].apply(lambda x: chat.cosine_similarity(x, instruction_embedding))
        
        embeddings_filtered = embeddings[embeddings['similarity'] > 0.3]
        embeddings_filtered.drop('similarity', axis=1, inplace=True)
        embeddings_filtered.drop('embedding', axis=1, inplace=True)
        context = embeddings_filtered.to_string()
        
        return context
    """
    
    def check_instruction_type(self, instruction) :
        
        messages = []
        messages.append({"role": "user", "content": instruction})
        messages.insert(0, {"role": "system", "content" : self.instruction_check_prompt})
        
        completion = self.client.chat.completions.create(
          model="gpt-4o",
          store=False,
          messages=messages
        )
        
        answer = completion.choices[0].message.content
        
        return answer
    
    def filter_data(self, instruction, instruction_type) :
        self.filtering_history.append({"role": "user", "content": instruction})
        
        messages = self.filtering_history.copy()
        messages.insert(0, {"role": "system",
                            "content" : self.filtering_prompt})
        messages.insert(1, {"role": "user",
                            "content" : f'instruction type: {instruction_type}'})
        
        completion = self.client.chat.completions.create(
          model="gpt-4o-mini",
          store=False,
          messages=messages
        )
        
        answer = completion.choices[0].message.content
        self.filtering_history.append({"role": "assistant", "content": answer})
        
        if len(self.filtering_history) > 10 :
            self.filtering_history.pop(0)
            self.filtering_history.pop(0)
        
        return answer
    
    def analyze_data(self, instruction, context) :
        self.analysis_history.append({"role": "user", "content": instruction})
        
        messages = self.analysis_history.copy()
        messages.insert(0, {"role": "system", "content" : self.analysis_prompt})
        messages.insert(1, {"role": "user", "content" : f"Data: {context}" })
        
        completion = self.client.chat.completions.create(
          model="gpt-4o",
          store=False,
          messages=messages
        )
        
        answer = completion.choices[0].message.content
        self.analysis_history.append({"role": "assistant", "content": answer})
        
        if len(self.analysis_history) > 10 :
            self.analysis_history.pop(0)
            self.analysis_history.pop(0)
        
        return answer
    

if __name__ == '__main__' :
    
    # some test cases
    api_key = 'shhhhhhhhhhhh'
    chat = ChatBot(api_key)
    
    instructions = ['Number of telegram messages in the last year by each month',
                    'Telegram deposit issues in the previous year?',
                    'What about LiveChat?',
                    'Game issues via LiveChat in the year',
                    'when did game issue messages last spike'
        ]
    
    
    data = pd.read_csv(CATEGORIES_PATH, sep=',', index_col=0)

    conn = connect(':memory:')
    data.to_sql(name='messages', con=conn)
    
    for instruction in instructions :
        print(instruction)
        
        instruction_type = chat.check_instruction_type(instruction)
        
        print(instruction_type)
        
        if instruction_type == 'filtering' :
            sql_query = chat.filter_data(instruction, instruction_type)
            sql_query = sql_query[7:-3]
    
            data_filtered = pd.read_sql(sql_query, conn)
            if 'index' in data_filtered :
                data_filtered = data_filtered.set_index('index')
                
                now = datetime.now()
                
                data_filtered.to_excel(f'results/output_{now.strftime("%Y-%m-%d %H_%M_%S")}.xlsx')
            else :
                context = data_filtered.to_string()
                
                analysis = chat.analyze_data(instruction, context)
                print(analysis)
            
        elif instruction_type == 'analysis' :
            #context = chat.rag_search(instruction, embeddings)
            sql_query = chat.filter_data(instruction, instruction_type)
            sql_query = sql_query[7:-3]
    
            data_filtered = pd.read_sql(sql_query, conn)
            context = data_filtered.to_string()
            
            analysis = chat.analyze_data(instruction, context)
            print(analysis)
        else:
            print('instruction not recognized')
            