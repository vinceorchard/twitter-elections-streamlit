from typing import Dict, List, Optional, Tuple, Union, Any
import re
import pandas as pd
import pickle as pk
from tqdm import tqdm
import spacy
from spacy.cli import download as spacy_download
from spacymoji import Emoji
import unicodedata
import csv
from collections import Counter

stopfile=open("../data/misc/stopwords_no_accents.txt","r",encoding="utf-8")
stoptext=stopfile.read()
stopfile.close()
stopwords=list(set(stoptext.split("\n")))

class text_processor:
    
    def __init__(
        self,
        spacy_model: str,
        remove_punctuation: bool = True,
        remove_digits: bool = True,
        stop_words: List[str] = [],
        lowercase: bool = True,
        lemmatize: bool = True,
        pos_tags_to_keep: Optional[List[str]] = None,
        remove_emojis: bool = True,
        keep_hashtags: bool = True,
        keep_ats: bool = True,
        remove_chars: Optional[List[str]] = None,
        remove_accents: Optional[bool] = True
    ):
        
        if not spacy.util.is_package(spacy_model):
            spacy_download(spacy_model)
            
        self.spacy_model = spacy_model
        self._nlp = spacy.load(spacy_model, disable = ['ner', 'parser'])
        self._nlp.add_pipe('sentencizer')
        self.remove_punctuation = remove_punctuation
        self.remove_digits = remove_digits
        self.stop_words = stop_words
        self.lowercase = lowercase
        self.lemmatize = lemmatize
        self.pos_tags_to_keep = pos_tags_to_keep
        
        self.remove_emojis = remove_emojis
        if self.remove_emojis:
            self._nlp.add_pipe('emoji', first=True)

        re_token_match = spacy.tokenizer._get_regex_pattern(self._nlp.Defaults.token_match)

        self.keep_hashtags = keep_hashtags
        if self.keep_hashtags:
            re_token_match = f"({re_token_match}|#\\w+)"
            
        self.keep_ats = keep_ats
        if self.keep_ats:
            re_token_match = f"({re_token_match}|@\\w+)"
        
        self._nlp.tokenizer.token_match = re.compile(re_token_match).match
    
        self.remove_chars = remove_chars
        self.remove_accents = remove_accents
    

    def clean_text(
        self, 
        s
    ) -> List[str]:

        """

        Clean a string of text.

        """
            
        if self.remove_emojis:
            s = [t for t in s if t._.is_emoji == False]
            
        if self.remove_punctuation:
            s = [t for t in s if t.is_punct == False]
        
        if self.remove_digits:
            s = [t for t in s if t.is_digit == False]
        
        if self.pos_tags_to_keep is not None:
            temp = []
            for t in s: 
                if '@' in t.text or '#' in t.text: # #s and @s as special cases
                    temp.append(t)
                    continue
                if t.pos_ in self.pos_tags_to_keep:
                    temp.append(t)
                    
        if self.lowercase and not self.lemmatize:
            s = [t.lower_ for t in s]
            
        if self.lowercase and self.lemmatize:
            s = [t.lemma_.lower() for t in s]

        if not self.lowercase and not self.lemmatize:
            s = [t.text for t in s]
        
        if self.remove_chars is not None:
            for char in self.remove_chars:
                s = [t.replace(char, ' ') for t in s]
        
        s = [t for t in s if t not in self.stop_words]

        s = [t.strip() for t in s if t not in self.stop_words]

        s = " ".join(s)
                
        if self.remove_accents:
            s = unicodedata.normalize('NFD',s).encode('ascii','ignore').decode("utf-8")
            
        s = s.strip()
            
        return s
    
    
    def process_docs(
        self,
        docs: List[str],
        batch_size: int = 10000,
        n_process: int = -1,
        output_path: str = './processed_docs.csv',
        progress_bar: bool = True
    ):
        
        """
        
        SpaCy pipeline with multiprocessing.
        We write the output to a text file for gains of speed 
        (appending to lists can be time-consuming in python as the list becomes longer).
        
        """
        
        spacy_docs = self._nlp.pipe(docs, batch_size=batch_size, n_process=n_process)
        
        if progress_bar:
            spacy_docs = tqdm(spacy_docs, total=len(docs))
        
        with open(output_path,'w',newline='') as csvfile:
            fieldnames = ['tweet_id', 'tweet_clean']
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames)
            for k,doc in enumerate(spacy_docs):
                cleaned_tweet = self.clean_text(doc)
                writer.writerow([k,cleaned_tweet])
                    

def drop_weblinks(s):
    output=""
    elements=s.split(" ")
    for elt in elements:
        if not(("http" in elt) or (".com" in elt) or (".fr" in elt) or ("www." in elt)):
            output=output+elt+" "
    if output=="":
        return ""
    return output[:-1]

    
p = text_processor(
    spacy_model = "fr_core_news_lg",
    remove_punctuation = True,
    remove_digits = False,
    stop_words = stopwords,
    lowercase = True,
    lemmatize = True,
    pos_tags_to_keep = ['VERB', 'NOUN', 'PNOUN', 'ADJ', 'NUM'],
    remove_emojis = True,
    keep_hashtags = True,
    keep_ats = True,
    remove_chars = ["\"",'-',"^",".","?","!",";","(",")",",",":","\'",
                    "+","&","|","/","{","}","~","_","`","[","]",">","<",
                   "=","*","%","$","\x07","\x08","\x12","\x14"],
    remove_accents = True
)

print('Cleaning tweets...')

df = pd.read_csv('../data/master_candidates_tweets.csv')

df['tweet_id'] = df.index
list_of_dicts = df.to_dict('records')

docs = []
for k,d in enumerate(list_of_dicts):
    d['text'] = drop_weblinks(d['text'])
    docs.append(d['text'])
    
p.process_docs(
    docs, 
    batch_size = 1000, 
    n_process=-1, 
    output_path = '../data/temp/processed_docs.csv', 
    progress_bar = True
)

new_df = pd.read_csv('../data/temp/processed_docs.csv')
df = df.merge(new_df, on = 'tweet_id')

df.to_csv('../data/master_candidates_tweets_cleaned.csv', index = False)