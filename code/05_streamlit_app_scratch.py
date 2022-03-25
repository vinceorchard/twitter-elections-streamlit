########################
#Importing packages
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import re
from tqdm import tqdm
import requests
import math
from datetime import datetime


from io import StringIO
import matplotlib.pyplot as plt


#############################
####Part II: Preparation#####
#############################

##########################################
# I) General layout of the page

#A) Main settings
st.set_page_config(layout="wide",
                   page_title="Que disent les candidats à la présidentielle sur Twitter ?",
                   page_icon="🗳️🇫🇷")

##########################################
# II) Define function to display tweets

def theTweet(tweet_url):
    api = "https://publish.twitter.com/oembed?url={}".format(tweet_url)
    response = requests.get(api)
    res = response.json()['html']
    return res

##########################################
# II) Define colors for candidats graph

color_dict = {'Nathalie Arthaud' : "maroon",
 'Nicolas Dupont-Aignan' : "mediumpurple",
 'Anne Hidalgo' : "pink",
 'Yannick Jadot' : "green",
 'Jean Lassalle' : "yellow",
 'Marine Le Pen' : "darkblue",
 'Emmanuel Macron' : "orange",
 'Jean-Luc Melenchon' : "red",
 'Valerie Pecresse' : "dodgerblue",
 'Fabien Roussel' : "crimson",
 'Eric Zemmour' : "rebeccapurple",
              'Philippe Poutou': 'darkred'}

##########################################
#III) Loading data
df_master = pd.read_csv('data/master_candidates_tweets_platform.csv', dtype={'id': 'str', 'author_id': 'str', 'tweet_count' : 'int', 'followers_count':'int'}, index_col = 0, lineterminator = '\n')
#df_master = requests.get("https://www.dropbox.com/s/y6qwge76wuvyv0e/master_candidates_tweets_platform.csv?dl=1")
#df_master = pd.read_csv(StringIO(df_master.text), dtype={'id': 'str', 'author_id': 'str', 'tweet_count' : 'int', 'followers_count':'int'}, index_col = 0, lineterminator = '\n')

df_candidates = pd.read_csv('data/candidates_account_list.csv', index_col=0).set_index('twitter_id')
df_nb_tweets_week = pd.read_csv('data/df_nb_tweets_week.csv', index_col=0)
df_candidates = df_candidates.set_index('name')
liste_candidats = list(df_candidates.index)

date_last_tweet = datetime.strptime(max(df_master['created_at']), "%Y-%m-%dT%H:%M:%S.000Z")

##############################
####Part II: Page content#####
##############################
col1, col2, col3 = st.columns([1, 5, 1])
with col2:

    st.title('Que disent les candidats à l\'élection présidentielle sur Twitter ?')

    st.header('Suivre l\'activité d\' un candidat sur Twitter')

    candidat = st.selectbox('Choisissez un candidat: ', liste_candidats) #User chooses the candidates he wants to compare

col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
with col2:
    ''
    ''
    ''
    pd.DataFrame([eval("st.image(\'"+df_candidates['profile_image_url'].loc[candidat].replace('_normal', '') + "\' , width=200 , caption = \'"+candidat+"\')").embedding], columns = ['Photo de profil'])

with col3:
    st.metric('nom d\'utilisateur', '@' + df_candidates['screen_name'].loc[candidat])
    st.metric('Nombre de followers', '{:<,}'.format(df_candidates['followers_count'].loc[candidat]).replace(",", " "))
    st.metric( 'Nombre de status', '{:<,}'.format(df_candidates['tweet_count'].loc[candidat]).replace(",", " "))
    st.metric('Date de création du compte', datetime.strptime(df_candidates['created_at'].loc[candidat],'%Y-%m-%d').strftime('%d/%m/%Y'))


    #pd.DataFrame([df_candidates['profile_image_url'].loc[candidat].replace('_normal', '')])

    #st.image(df_candidates['profile_image_url'].loc[candidat].replace('_normal', ''), width=150, caption= candidat

    candidat_screen_name = df_candidates['screen_name'].loc[candidat]


######################
#Nombre de tweets
col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    st.subheader('Nombre de tweets par semaine')

col1, col2, col3 = st.columns([1, 1.8, 1])
ymax = math.ceil(max(df_nb_tweets_week.stack())/10)*10

with col2:
    fig = df_nb_tweets_week[candidat].iloc[0:-1].plot.line(color=color_dict, ylim = (0, ymax)).figure
    plt.legend(loc='center right', bbox_to_anchor = (-0.1, 0.5))
    st.pyplot(fig)

col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    st.subheader('Aperçu du fil d\'actualité de ' + candidat)

col1, col2, col3 = st.columns([1, 1.8, 1])
with col2:
    res = theTweet('https://twitter.com/' + candidat_screen_name)
    components.html(res, height=600, width=600, scrolling=True)


col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    st.subheader('Explorer les tweets de ' + candidat)
    df_temp = df_master[(df_master['name'] == candidat) & (df_master['is_RT'] == 0)]

    # Consulter les 5 derniers tweets contenant le mot: XXXX
    'Filtrer les tweets contenant le(s) mot(s)'
    word = st.text_input("Entrez un ou des mots:", )
    '- Si vous ne souhaitez pas filtrer par mot laissez ce champ vide'
    '- Pour trouver les tweets contenant au moins un mot parmi un ensemble de mots, séparez les mots par le charactère \"|\"'
    '(e.g: Europe|économie retourne les tweets contenant les mots \"Europe\" ou \"économie\")'

    if "" in word:
        base = r'^{}'
        expr = '(?=.*{})'
        words = word.split(" ")
        df_temp2 = df_temp[df_temp['text'].str.contains(str(base.format(''.join(expr.format(w) for w in words))))]
    else:
        df_temp2 = df_temp[df_temp['text'].str.contains(word)]

    trie = st.selectbox('Trier les tweets par', ['date', 'popularité'])

    ####
    if trie == 'date':
        'Derniers tweets de ' + candidat + ' contenant le(s) mot(s): ' + word.replace(" ", " et ").replace("|",
                                                                                                             " ou ")
        'Le résultat de la recherche est limité à 20 tweets maximum.'
        if word=="":
            "Aucun filtre par mots n'a été renseigné. Par défault, sont affichés ci-dessous l'ensemble des tweets de " + candidat + " présents dans notre base de données triés par date."
    else:
        'Tweets les plus populaires (en nombre de like) de ' + candidat + ' contenant le(s) mot(s): ' + word.replace(" ", " et ").replace(
            "|", " ou ") + '. '
        'Le résultat de la recherche est limité à 20 tweets maximum.'
        if word == "":
            "Aucun filtre par mots n'a été renseigné. Par défault, sont affichés ci-dessous l'ensemble des tweets de " + candidat + " présents dans notre base de données triés par popularité."

col1, col2, col3 = st.columns([1, 1.8, 1])
with col2:
    if trie == 'date':
        df_temp2 = df_temp2.sort_values(by='created_at', ascending=False).reset_index().drop(columns='index')
        set_of_tweets = list(df_temp2['id'].iloc[0:20].values)
        if len(set_of_tweets) != 0:
            list_url = ["https://twitter.com/" + candidat_screen_name + "/status/" + id for id in set_of_tweets]
            res1 = ''
            for url in list_url:
                try:
                    obj = theTweet(url)
                    res1 = res1 + ' ' + obj
                except:
                    pass
            components.html(res1, height=600, width=600, scrolling=True)

        else:
            "Aucun tweets correspondant"

    else:
        df_temp2 = df_temp2.sort_values(by='like_count', ascending=False).reset_index().drop(columns='index')
        set_of_tweets = list(df_temp2['id'].iloc[0:20].values)

        if len(set_of_tweets) != 0:
            list_url = ["https://twitter.com/" + candidat_screen_name + "/status/" + id for id in set_of_tweets]
            res1 = ''
            for url in list_url:
                try:
                    obj = theTweet(url)
                    res1 = res1 + ' ' + obj
                except:
                    pass
            components.html(res1, height=600, width=600, scrolling=True)
        else:
            "Aucun tweets correspondant"


col1, col2, col3 = st.columns([1, 5, 1])

with col2:
    'Notre base de données contient l\'ensemble des tweets des candidats depuis le 01/10/2021'
    'Notre base de données a été mise à jour pour la dernière fois le ' + date_last_tweet.strftime("%x") + ' à ' + date_last_tweet.strftime("%H:%M")

    '- Notre base de données recense ' + str(len(df_temp2)) + ' tweets de ' + candidat + ' contenant le(s) mot(s): ' + word.replace(" ", " et ").replace("|",
                                                                                                             " ou ")
    '- ' + str(len(df_temp2)/len(df_temp)*100)[0:3] + '% des tweets de ' + candidat + ' recensés dans notre base de données contiennent le(s) mot(s): '+ word.replace(" ", " et ").replace("|",
                                                                                                             " ou ")
    '- Dans les tweets recensés dans notre base de données, les candidats à la présidentielle mentionnent en moyenne dans ' + str(len(df_master[df_master['text'].str.contains(word)])/len(df_master)*100)[0:3] + \
    '% de leurs tweets le(s) mot(s): '+ word.replace(" ", " et ").replace("|", " ou ")

    ###########################
    # Wordcloud
    st.subheader('Mots et hashtags charactéristiques de ' + candidat)

col1, col2, col3, col4 = st.columns([1, 5, 5, 1])
screen_name = df_candidates['screen_name'].loc[candidat]

with col2:
    st.image("graphs/wordcloud_tokens_" + screen_name + ".png", caption= "Mots les plus charactéristiques de "+ candidat)

with col3:
    st.image("graphs/wordcloud_hashtags_" + screen_name + ".png", caption="Hashtags les plus charactéristiques de "+ candidat)

col1, col2, col3 = st.columns([1, 5, 1])

with col2:
    st.subheader('Topics model pour ' + candidat)

    st.subheader('Narratives utilisées par ' + candidat)
