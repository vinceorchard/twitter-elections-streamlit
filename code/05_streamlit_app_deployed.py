########################
#Importing packages
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import re
from tqdm import tqdm
import requests
from io import StringIO



# Functions

def theTweet(tweet_url):
    api = "https://publish.twitter.com/oembed?url={}".format(tweet_url)
    response = requests.get(api)
    res = response.json()['html']
    return res


####I) We load our data
#Importing datasets
df_master = pd.read_csv('data/master_candidates_tweets.csv', dtype={'id': 'str', 'author_id': 'str', 'tweet_count' : 'float', 'followers_count':'float'}, index_col = 0)

#df_master = requests.get(
 #           "https://www.dropbox.com/s/j1fhoyb3e74tt75/master_candidates_tweets.csv?dl=1" #A modifier à chaque mise à jour ?
  #      )
#df_master = pd.read_csv(StringIO(df_master.text), dtype={'id': 'str', 'author_id': 'str'}, index_col = 0)


df_candidates = pd.read_csv('data/candidates_account_list.csv', index_col=0).set_index('twitter_id')

df_nb_tweets_week = pd.read_csv('data/df_nb_tweets_week.csv', index_col=0)

####

##

######################
#Page title
st.title('Que disent les candidats à l\'élection présidentielle sur Twitter ?')

##User chooses the candidates he wants to compare
st.header('Comparez l\'activités des candidats sur Twitter')
df_candidates = df_candidates.set_index('name')
liste_candidats = list(df_candidates.index)
filtre_candidats = st.multiselect('Choisissez les candidats', liste_candidats)

######################
#Statistcs on user account
st.subheader('Statistiques clés sur les comptes des candidats')
#pd.options.display.float_format = '{:<,.0f}'.format
st.table(df_candidates[['followers_count', 'tweet_count', 'created_at', 'description']].loc[filtre_candidats].style.format(
    subset = ['followers_count', 'tweet_count'], formatter= '{:<,}'))
#To do: Ajouter un disclaimer avec l'heure du last update de la base de données


######################
#Nombre de tweets
st.subheader('Nombre de tweets par semaine')

if filtre_candidats == []:
    ' '
    pass
else:
    st.line_chart(df_nb_tweets_week[filtre_candidats])


######################
#Display last tweets
st.header('Explorez les tweets postés par un candidat')

candidat = st.selectbox("Choisissez un candidat :", liste_candidats)


######
st.subheader('Aperçu du fil Twitter de ' + candidat)
candidat_screen_name = df_candidates['screen_name'].loc[candidat]

res = theTweet('https://twitter.com/' + candidat_screen_name)
components.html(res, height= 500, width = 700, scrolling = True)

######
st.subheader('Filtrer les tweets de ' + candidat)
#filtre_mot =

df_temp = df_master[(df_master['name']==candidat) & (df_master['is_RT']==0)]


#Consulter les 5 derniers tweets contenant le mot: XXXX
'Filtrer les tweets contenant le(s) mot(s)'
word = st.text_input("Entrez un ou des mots:", )
'- Si vous ne souhaitez pas filtrez par mot laissez ce champs vide'
'- Pour trouver les tweets contenant au moins mot, séparez les mots par le charactère \"|\"'
'(e.g: Europe|économie retourne les tweets contenant les mots \"Europe\" ou \"économie\")'

if " " in word:
    base = r'^{}'
    expr = '(?=.*{})'
    words = word.split(" ")
    df_temp = df_temp[df_temp['text'].str.contains(str(base.format(''.join(expr.format(w) for w in words))))]
else:
    df_temp = df_temp[df_temp['text'].str.contains(word)]

trie = st.selectbox('Trier les tweets par', ['date', 'popularité'])

####
if trie =='date':
    '5 derniers tweets de ' + candidat + ' contenant le(s) mot(s) ' + word
    df_temp2 = df_temp.sort_values(by='created_at', ascending=False).reset_index().drop(
        columns='index')
    #df_temp.iloc[0][0]
    set_of_tweets = list(df_temp2.iloc[0:5]['id'].values)
    try:
        res = theTweet("https://twitter.com/" + candidat_screen_name + "/status/" + set_of_tweets[0])
        components.html(res, height=500, width=700, scrolling=True)
    except:
        "Aucun tweets correspondant"
    try:
        res_1 = theTweet("https://twitter.com/" + candidat_screen_name + "/status/" + set_of_tweets[1])
        components.html(res_1, height=500, width=700, scrolling=True)
    except:
        pass
        #''
    try:
        res_2 = theTweet("https://twitter.com/" + candidat_screen_name + "/status/" + set_of_tweets[2])
        components.html(res_2, height=500, width=700, scrolling=True)
    except:
        pass
        #""
    try:
        res_3 = theTweet("https://twitter.com/" + candidat_screen_name + "/status/" + set_of_tweets[3])
        components.html(res_3, height=500, width=700, scrolling=True)
    except:
        pass
        #""
    try:
        res_4 = theTweet("https://twitter.com/" + candidat_screen_name + "/status/" + set_of_tweets[4])
        components.html(res_4, height=500, width=700, scrolling=True)
    except:
        pass
        #""
else:
    '5 tweets les plus populaires de ' + candidat + 'contenant le(s) mot(s) ' + word
    df_temp2 = df_temp.sort_values(by='retweet_count', ascending=False).reset_index().drop(
        columns='index')
    # df_temp.iloc[0][0]
    set_of_tweets = list(df_temp2.iloc[0:5]['id'].values)
    try:
        res = theTweet("https://twitter.com/" + candidat_screen_name + "/status/" + set_of_tweets[0])
        components.html(res, height=500, width=700, scrolling=True)
    except:
        "Aucun tweets correspondant"
    try:
        res_1 = theTweet("https://twitter.com/" + candidat_screen_name + "/status/" + set_of_tweets[1])
        components.html(res_1, height=500, width=700, scrolling=True)
    except:
        pass
        #''
    try:
        res_2 = theTweet("https://twitter.com/" + candidat_screen_name + "/status/" + set_of_tweets[2])
        components.html(res_2, height=500, width=700, scrolling=True)
    except:
        pass
        #""
    try:
        res_3 = theTweet("https://twitter.com/" + candidat_screen_name + "/status/" + set_of_tweets[3])
        components.html(res_3, height=500, width=700, scrolling=True)
    except:
        pass
        #""
    try:
        res_4 = theTweet("https://twitter.com/" + candidat_screen_name + "/status/" + set_of_tweets[4])
        components.html(res_4, height=500, width=700, scrolling=True)
    except:
        pass
        #""


###########################
#Wordcloud
st.header('Comparer les mots et hashtags caractérisant chaque candidats')

#df_master['name'].drop_duplicates()
liste_candidats_2 = list(df_candidates['nom'].values)
filtre_candidats2 = st.multiselect('Choisissez les candidats', liste_candidats_2)

screen_name_name = {}
for name in filtre_candidats2:
    screen_name_name[name] = df_candidates['screen_name'][df_candidates['nom']==name].iloc[0]

st.subheader('Mots charactérisant le plus chaque candidats')

pd.DataFrame([eval("st.image('graphs/wordcloud_tokens_" + screen_name_name[candidat] + ".png\', caption=" + '\'' + candidat + '\'' + ")").embedding for
 candidat in filtre_candidats2])

##
st.subheader('Hashtags charactérisant le plus chaque candidats')
pd.DataFrame([eval("st.image('graphs/wordcloud_hashtags_" + screen_name_name[candidat] + ".png\', caption=" + '\'' + candidat + '\'' + ")").embedding for
 candidat in filtre_candidats2])





