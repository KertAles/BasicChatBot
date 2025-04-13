# -*- coding: utf-8 -*-

"""

ChatBot GUI. Constructs a rudimentary GUI and passes the messages to the 
ChatBot that handles the communication with ChatGPT.

"""


import pandas as pd
from sqlite3 import connect
from datetime import datetime
import tkinter as tk

from chatbot import ChatBot
from global_vars import CATEGORIES_PATH

class App(tk.Frame):
    def __init__(self, master, width=400, height=750):
        super().__init__(master, width=width, height=height)
        
        self.key_acquired = False
        self.api_key = ''
        
        # define everything needed for the GUI
        self.width = width
        
        self.entry_field = tk.Entry()
        self.entry_field.pack(side=tk.BOTTOM, fill=tk.X)
        self.contents = tk.StringVar()
        self.contents.set('')
        self.entry_field["textvariable"] = self.contents
        self.entry_field.bind('<Return>', self.enter_pressed)
        
        self.pack()
        self.pack_propagate(False)
        
        
        # define everything needed for the chatbot
        
        self.data = pd.read_csv(CATEGORIES_PATH, sep=',', index_col=0)
        self.conn = connect(':memory:')
        self.data.to_sql(name='messages', con=self.conn)
        
        self.format_log_entry(text='Enter an OpenAI API key.',
                              source='ChatBot')


    def format_log_entry(self, text, source) :
        background_color = 'light salmon' if source=='User' else 'turquoise'
        label = tk.Label(self,
                         text=f'{source}: {text}',
                         anchor="w",
                         justify="left",
                         wraplength=self.width,
                         width=self.width,
                         background=background_color)
        label.pack()
        

    def enter_pressed(self, event):
        instruction = self.entry_field.get()
        self.contents.set('')
        
        if not self.key_acquired :
            self.api_key = instruction
            self.chatbot = ChatBot(self.api_key)
            self.key_acquired = True
            
            self.format_log_entry(text='Key acquired.',
                                  source='ChatBot')
        else :
            self.format_log_entry(text=instruction, source='User')
    
            instruction_type = self.chatbot.check_instruction_type(instruction)
            
            if instruction_type == 'filtering' :
                sql_query = self.chatbot.filter_data(instruction, instruction_type)
                sql_query = sql_query[7:-3]
    
                data_filtered = pd.read_sql(sql_query, self.conn)
                
                if 'index' in data_filtered :
                    data_filtered = data_filtered.set_index('index')
                    now = datetime.now()
                    data_filtered.to_excel(f'results/output_{now.strftime("%Y-%m-%d %H_%M_%S")}.xlsx')
                    
                    filter_message = f'The result of the query was saved to: results/output_{now.strftime("%Y-%m-%d %H_%M_%S")}.xlsx'
                    self.format_log_entry(text=filter_message, source='ChatBot')
                else :
                    context = data_filtered.to_string()
                    
                    analysis = self.chatbot.analyze_data(instruction, context)
                    self.format_log_entry(text=analysis, source='ChatBot')
                    
            elif instruction_type == 'analysis' :
                #context = chat.rag_search(instruction, embeddings)
                sql_query = self.chatbot.filter_data(instruction, instruction_type)
                sql_query = sql_query[7:-3]
    
                data_filtered = pd.read_sql(sql_query, self.conn)
                context = data_filtered.to_string()
                
                analysis = self.chatbot.analyze_data(instruction, context)
                self.format_log_entry(text=analysis, source='ChatBot')
            else:
                self.format_log_entry(text='Instruction not recognized.',
                                      source='ChatBot')
            
            return "break"


if __name__ == '__main__' :
    root = tk.Tk()
    myapp = App(root)
    myapp.mainloop()
