print('Training speech partisanship model...')

import pickle as pk
import numpy as np
import pandas as pd
from tqdm import tqdm 
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
import random 

random.seed(1234)

df = pd.read_csv('../data/master_candidates_tweets_cleaned.csv')

df = df[['tweet_clean', 'user_username']]
df = df.dropna(subset = ['user_username']) # drop obs without username
candidates = list(set(df['user_username']))
di = {c:k for k,c in enumerate(candidates)}

df.columns = ['X', 'Y']
df['y'] = df['Y']
df = df.replace({'y':di})
df = df.dropna(subset = ['X']).reset_index() # drop obs without text

test = df.groupby('Y').size().reset_index()
smallest_sample = min(test[0])

# Balance the sample
df=df.groupby('y',as_index = False,group_keys=False).apply(lambda s: s.sample(smallest_sample,replace=False))

# Split dataset into training set (80%) and test set (20%)
X_train, X_test, y_train, y_test = train_test_split(df.X, df.y, test_size=0.2, random_state=109)

# Train the model 
vectorizer1 = CountVectorizer(tokenizer=lambda text: text.split(" "))
X_train = vectorizer1.fit_transform(X_train)

LR1 = LogisticRegression(random_state=0, verbose=1, max_iter=1000)
LR1.fit(X_train, y_train)

# Assess the model
X_test = vectorizer1.transform(X_test)
y_prediction = LR1.predict(X_test)

print("Accuracy: %s \n" % accuracy_score(y_test, y_prediction))
print("Precision: %s \n" % precision_score(y_test, y_prediction, average='macro'))
print("Recall: %s \n" % recall_score(y_test, y_prediction, average='macro'))
print("Confusion Matrix \n\n %s" %confusion_matrix(y_test, y_prediction))

print(" \\\\\n".join([" & ".join(map(str,line)) for line in confusion_matrix(y_test, y_prediction)]))

# Print most predictive tokens for each party
coefs = pd.DataFrame(LR1.coef_)
coefs = coefs.T
coefs.index = vectorizer1.get_feature_names()
coefs['token'] = coefs.index

temp = coefs[coefs['token'].str.contains('@|#') == False]

tab = {c:list(dict(temp[k].nlargest(50)).keys()) for k,c in enumerate(candidates)}
tab = pd.DataFrame(tab)

print('Most predictive words per party:')
print(tab)

tab.to_csv('../data/predictive_tokens.csv')

temp = coefs[coefs['token'].str.contains('#') == True]
tab = {c:list(dict(temp[k].nlargest(50)).keys()) for k,c in enumerate(candidates)}
tab = pd.DataFrame(tab)

print('Most predictive hashtags per party:')
print(tab)

tab.to_csv('../data/predictive_hashtags.csv')

# Save the model
political_speech_model = [vectorizer1.vocabulary_,LR1]
with open('../data/temp/political_speech_model.pk', 'wb') as f:
    pk.dump(political_speech_model, f)