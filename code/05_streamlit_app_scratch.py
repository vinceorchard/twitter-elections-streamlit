########################
#Importing packages
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import re
from tqdm import tqdm
import requests


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

#B) Defining margins
col1, col2, col3 = st.columns([1, 5, 1])



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
 'Francois Asselineau': "plum",
 'Nicolas Dupont-Aignan' : "mediumpurple",
 'Anne Hidalgo' : "salmon",
 'Yannick Jadot' : "green",
 'Anasse Kazib' : "black",
 'Jean Lassalle' : "orange",
 'Marine Le Pen' : "darkblue",
 'Emmanuel Macron' : "darkorange",
 'Jean-Luc Melenchon' : "red",
 'Valerie Pecresse' : "dodgerblue",
 'Fabien Roussel' : "crimson",
 'Christiane Taubira' : "black",
 'Hélène Thouy' : "black",
 'Eric Zemmour' : "rebeccapurple"}

##########################################
#III) Loading data
df_master = pd.read_csv('data/master_candidates_tweets.csv', dtype={'id': 'str', 'author_id': 'str', 'tweet_count' : 'float', 'followers_count':'float'}, index_col = 0)
#df_master = requests.get('https://www.dropbox.com/s/y6qwge76wuvyv0e/master_candidates_tweets.csv?dl=1')
#df_master = pd.read_csv(StringIO(df_master.text), dtype={'id': 'str', 'author_id': 'str', 'tweet_count' : 'float', 'followers_count':'float'}, index_col = 0)

df_candidates = pd.read_csv('data/candidates_account_list.csv', index_col=0).set_index('twitter_id')
df_nb_tweets_week = pd.read_csv('data/df_nb_tweets_week.csv', index_col=0)
df_candidates = df_candidates.set_index('name')
liste_candidats = list(df_candidates.index)



##############################
####Part II: Page content#####
##############################

with col2:


    st.title('Que disent les candidats à l\'élection présidentielle sur Twitter ?')

    #I)

    st.header('Comparez l\'activités des candidats sur Twitter')

    filtre_candidats = st.multiselect('Choisissez les candidats', liste_candidats) #User chooses the candidates he wants to compare

    ######################
    #Statistcs on user account
    #st.subheader('Statistiques clés sur les comptes des candidats')
    #pd.options.display.float_format = '{:<,.0f}'.format
    #st.table(df_candidates[['followers_count', 'tweet_count', 'created_at', 'description']].loc[filtre_candidats].style.format(
     #   subset = ['followers_count', 'tweet_count'], formatter= '{:<,}'))
    #To do: Ajouter un disclaimer avec l'heure du last update de la base de données




######################
#Nombre de tweets
    st.subheader('Nombre de tweets par semaine')

col1, col2, col3 = st.columns([1, 1.8, 1])

with col2:


    if filtre_candidats == []:
        ' '
        pass
    else:
        fig = df_nb_tweets_week[filtre_candidats].plot.line(color=color_dict).figure
        plt.legend(loc='center right', bbox_to_anchor = (-0.1, 0.5))
        st.pyplot(fig)

        #df_nb_tweets_week[filtre_candidats].plot.line(color=color_dict)

col1, col2, col3 = st.columns([1, 5, 1])

with col2:

    ######################
    # Display last tweets
    st.header('Explorez les tweets postés par un candidat')

    candidat = st.selectbox("Choisissez un candidat :", liste_candidats)

    ######
    st.subheader('Aperçu du fil Twitter de ' + candidat)
    candidat_screen_name = df_candidates['screen_name'].loc[candidat]

candidat_screen_name = "n_arthaud"
candidat = 'Nathalie Arthaud'

res = theTweet('https://twitter.com/' + candidat_screen_name)

col1, col2, col3 = st.columns([1, 1.8, 1])

with col2:
    components.html(res, height=600, width=550, scrolling=True)

col1, col2, col3 = st.columns([1, 5, 1])

with col2:

    ######
    st.subheader('Filtrer les tweets de ' + candidat)
    # filtre_mot =
    df_temp = df_master[(df_master['name'] == candidat) & (df_master['is_RT'] == 0)]

    # Consulter les 5 derniers tweets contenant le mot: XXXX
    'Filtrer les tweets contenant le(s) mot(s)'
    word = st.text_input("Entrez un ou des mots:", )
    '- Si vous ne souhaitez pas filtrer par mot laissez ce champ vide'
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
    if trie == 'date':
        '5 derniers tweets de ' + candidat + ' contenant le(s) mot(s): ' + word.replace(" ", " et ").replace("|", " ou ")
    else:
        '5 tweets les plus populaires de ' + candidat + ' contenant le(s) mot(s): ' + word.replace(" ", " et ").replace("|", " ou ")

col1, col2, col3 = st.columns([1, 1.8, 1])

with col2:

    if trie == 'date':
        df_temp2 = df_temp.sort_values(by='created_at', ascending=False).reset_index().drop(
            columns='index')
        set_of_tweets = list(df_temp2.iloc[0:5]['id'].values)

        if len(set_of_tweets) != 0:
            res_test = ' '.join([theTweet("https://twitter.com/" + candidat_screen_name + "/status/" + id) for id in set_of_tweets])
            components.html(res_test, height=600, width=550, scrolling=True)
        else:
            "Aucun tweets correspondant"

    else:
        df_temp2 = df_temp.sort_values(by='retweet_count', ascending=False).reset_index().drop(
            columns='index')
        # df_temp.iloc[0][0]
        set_of_tweets = list(df_temp2.iloc[0:5]['id'].values)
        if len(set_of_tweets) != 0:
            res_test = ' '.join([theTweet("https://twitter.com/" + candidat_screen_name + "/status/" + id) for id in set_of_tweets])

            components.html(res_test, height=600, width=550, scrolling=True)
        else:
            "Aucun tweets correspondant"


col1, col2, col3 = st.columns([1, 5, 1])

with col2:
    ###########################
    # Wordcloud
    st.header('Comparer les mots et hashtags caractérisant chaque candidats')

    # df_master['name'].drop_duplicates()
    liste_candidats_2 = list(df_candidates['nom'].values)
    filtre_candidats2 = st.multiselect('Choisissez les candidats', liste_candidats_2)

    screen_name_name = {}
    for name in filtre_candidats2:
        screen_name_name[name] = df_candidates['screen_name'][df_candidates['nom'] == name].iloc[0]




    wordcloud_comp = st.selectbox('Comparer les:', ['mots', 'hashtags'])

    if wordcloud_comp == "mots":
        st.subheader('Mots charactérisant le plus chaque candidats')
    else:
        st.subheader('Hashtags charactérisant le plus chaque candidats')

col1, col2, col3, col4 = st.columns([1, 2.7, 2.7, 1])

i=2
filtre_candidats_colonnegauche = [filtre_candidats2[i] for i in range(len(filtre_candidats2)) if i/2 == round(i/2)]
filtre_candidats2_colonnedroite = [filtre_candidats2[i] for i in range(len(filtre_candidats2)) if i/2 != round(i/2)]

if wordcloud_comp == "mots":
    with col2:

        pd.DataFrame([eval("st.image('graphs/wordcloud_tokens_" + screen_name_name[
            candidat] + ".png\', caption=" + '\'' + candidat + '\'' + ")").embedding for
                      candidat in filtre_candidats_colonnegauche])

    with col3:
        ##

        pd.DataFrame([eval("st.image('graphs/wordcloud_tokens_" + screen_name_name[
            candidat] + ".png\', caption=" + '\'' + candidat + '\'' + ")").embedding for
                      candidat in filtre_candidats2_colonnedroite])

else:
    with col2:

        pd.DataFrame([eval("st.image('graphs/wordcloud_hashtags_" + screen_name_name[
            candidat] + ".png\', caption=" + '\'' + candidat + '\'' + ")").embedding for
                      candidat in filtre_candidats_colonnegauche])

    with col3:
        ##

        pd.DataFrame([eval("st.image('graphs/wordcloud_hashtags_" + screen_name_name[
            candidat] + ".png\', caption=" + '\'' + candidat + '\'' + ")").embedding for
                      candidat in filtre_candidats2_colonnedroite])





