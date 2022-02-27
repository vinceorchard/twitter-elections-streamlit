########################
#Importing packages
import streamlit as st
import pandas as pd
from tqdm import tqdm

#Importing datasets
df_master = pd.read_csv('data/master_candidates_tweets.csv')
df_candidates = pd.read_csv('data/candidates_account_list.csv', index_col=0).set_index('twitter_id')


#I) Data preparation
#
df_master = df_master.merge(df_candidates[['name']], how='left', left_on='author_id', right_index=True)

#A) Number of tweets per week
df_master['created_at'] = pd.to_datetime(df_master['created_at'])
df_master['created_at_week'] = df_master['created_at'].round('7D')
df_nb_tweets_week = pd.DataFrame([], index=df_master['created_at_week'].drop_duplicates())
for id in tqdm(list(df_candidates.index)):
    df_nb_tweets_week = df_nb_tweets_week.merge(pd.Series(df_master['created_at_week'][df_master['author_id'] == float(id)].value_counts(), name=id),
                                      how='left', right_index=True, left_index=True)
df_nb_tweets_week = df_nb_tweets_week.rename(columns = {df_candidates.index[i] : df_candidates['name'].iloc[i] for i in range(len(df_candidates))})

######################
#Page title
st.title('Que disent les candidats à la présidentielle sur Twitter ?')

##User chooses the candidates he wants to compare
st.header('L\'activité de quels candidats souhaitez-vous analyser ?')
df_candidates = df_candidates.set_index('name')
liste_candidats = list(df_candidates.index)
filtre_candidats = st.multiselect('Choisissez les candidats', liste_candidats)


######################
#Statistcs on user account
st.subheader('Statistiques clés sur les comptes des candidats')
st.table(df_candidates[['followers_count', 'tweet_count', 'created_at', 'description']].loc[filtre_candidats])
#To do: Ajouter un disclaimer avec l'heure du last update de la base de données



######################
#Nombre de tweets
st.subheader('Nombre de tweets par semaine')

if filtre_candidats == []:
    ' '
    pass
else:
    st.line_chart(df_nb_tweets_week[filtre_candidats][df_nb_tweets_week.index > '2021-09-21'])

######################
#Display last tweets
st.subheader('Aperçu des tweets des candidats')
candidat = st.selectbox("Choisissez un candidats :", liste_candidats)

df_temp = df_master[df_master['name']==candidat]

'5 tweets les plus récents'
st.table(df_temp.sort_values(by='created_at', ascending=False)[0:5][['text', 'created_at']].reset_index().drop(columns = 'index'))

#Most retweeted
'5 tweets les plus populaires (en nombre de retweets)'
st.table(df_temp.sort_values(by='retweet_count', ascending=False)[0:5][['text', 'created_at', 'retweet_count']].reset_index().drop(columns = 'index'))


#Consulter les 5 derniers tweets contenant le mot: XXXX
word = st.text_input("Entrez un mot:", )
'5 derniers tweets contenant le mot ' + word
st.table(df_temp[df_temp['text'].str.contains(str(word))].sort_values(by='created_at', ascending=False)[0:5][['text', 'created_at']].reset_index().drop(columns = 'index'))