import pandas as pd
import subprocess
from datetime import datetime



################################################
#Getting name of most recent dataset
date_files = []
for line in subprocess.Popen(['ls', 'data/historique' ], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout:
    date_files.append(str(line)[2:15])

date_files_datetimeformat = [] #
for i in range(len(date_files)-1):
    date_files_datetimeformat.append(datetime.strptime(date_files[i], "%Y%m%d_%H%M"))

update_date = date_files[date_files_datetimeformat.index(max(date_files_datetimeformat))]


################################################
#Loading latest dataset
df_update = pd.read_json('data/historique/' + update_date + '_tweets_updating_dataset.json', lines=True)


#Ranking candidates by alphabetic order
df_candidates = pd.read_csv('data/input/twitter_candidats_presidentielles.csv', index_col = 0)
df_candidates['nom'] = df_candidates['name'].str.extractall('(?<= )([\w -]*)')[0].values
df_candidates = df_candidates[df_candidates['sample']==1].drop(columns = ['sample']).sort_values(by = ['nom']).reset_index(drop=True)

################################################
keys_main = ['created_at', 'description', 'location', 'profile_image_url']

keys_public_metrics = ['followers_count', 'following_count', 'tweet_count']

description_account = {}
for id in df_candidates['twitter_id']:
    temp = df_update[df_update['author_id']==float(id)].drop_duplicates(keep='first' , subset=['author_id']).iloc[0]['author']
    description_account[id] = [temp[a] if a in temp.keys() else None for a in keys_main] + [temp['public_metrics'][a] if a in temp['public_metrics'].keys() else None  for a in keys_public_metrics]

df_description_account = pd.DataFrame.from_dict(description_account, orient='index', columns = keys_main + keys_public_metrics)

df_candidates = df_candidates.merge(df_description_account, left_on = 'twitter_id', right_index=True)
df_candidates['created_at'] = pd.to_datetime(df_candidates['created_at']).dt.strftime("%Y-%m-%d")

df_candidates.to_csv('data/candidates_account_list.csv')