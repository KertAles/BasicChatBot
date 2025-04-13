# BasicChatBot

## Setup

Required packages :
```
pip install openai
pip install nltk
pip install pandas
pip install jellyfish
```

## Usage

Data is already processed, so running message_classifier.py is not required.

Just run the GUI found in chat_gui.py and enter an OpenAI API key when required. To send a message type in the input box at the bottom and press enter.


## Evaluation
- How did you classify feedback (Describe your methodology: rule-based, machine learning, hybrid. Discuss advantages, drawbacks, and how you would handle new, previously unseen issues, such as a new wallet blocking deposits).

Split the sentences into words, stemmed the words, removed stopwords, and analysed the top 100 words. Determined some keywords based on that analysis. Sentences were classified into a category if they contained a word that was similar to a keywords(calculated using the Jaro similarity - accounting for typos). This method is simple and quick, but it fails to capture words that are similar in meaning - an improvement would be to use word embeddings instead and look at cosine distances. As it stands, it can't handle unseen issues without manually adding new keywords. Maybe an implementation of a system that determines if a message has any meaning or not, and based on this information it can still be sent to a person to be resolved, would aleviate this problem.

- How does your chatbot manage conversational context?

Before every prompt, a 'system' message is sent that describes the task the LLM has to perform. Instruction type identification and analysis have simple descriptions, while filtering instructions contain a description of the dataframe : the columns, their meaning, and in the case of message categories their allowed values.

- What are the main limitations? (e.g., vague feedback, multi-category overlaps, conversational memory constraints.)

There's no way for the user to verify if the provided analysis is correct, since the results of some statistical operation aren't saved, just sent to ChatGPT again for reformatting into a sentence.
It can't identify message categories outside of the predefined ones.

- How could the system be improved?

Classification: Using word embeddings to classify messages, to capture different words that are similar in meaning to the already-defined keywords. Expand this to sentence embeddings and try to find clusters that represent game/spin... issues
Chatbot: Utilisation of the 'tool' function in the API, instead of relying solely on the description of a problem. A GUI that opens the filtered data instead of saving it to an Excel file - this way statistical analysis could be displayed as well.

- Explain how the chatbot tracks and utilizes past queries to refine current requests.

The chatbot keeps a list of previous prompts/answers. To mitigate the usage of tokens, the earlier prompts get removed after 5 prompt/answer exchanges. Once a prompt is made, the history gets sent along with the newest prompt.

- If the entire conversation were provided (not just a single response, but a full exchange with a support agent), would you approach this task differently? (Explain how.)

I'm not sure that I understand this question.

- How would you measure and validate the correctness of message classifications?

Get a subset of messages, manually classify them, depending on the priorities choose the correct metric. If identifying as many important messages as possible was a priority, I would look to optimize recall for each class. F-1 is also a decent middle option.
