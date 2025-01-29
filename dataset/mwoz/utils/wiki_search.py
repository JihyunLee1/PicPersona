# importing the module
import wikipedia
# sentence tokenizer
from nltk.tokenize import sent_tokenize

def search_wiki(query):
    try:
        text = wikipedia.page(query).summary
        sentences = sent_tokenize(text)
        return sentences
    except:
        return None
