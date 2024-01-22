import pandas as pd
import streamlit as st
import pickle
import requests

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

@st.cache_data
def translate_text(text, target_language='en'):
    if target_language == 'en':
        return text
    import requests, uuid

    resource_key = 'a607110a266144ab8273765b7d58541d'

    region = 'eastus'

    endpoint = 'https://api.cognitive.microsofttranslator.com/'

    path = '/translate?api-version=3.0'
    params = f'&from=en&to={target_language}'
    constructed_url = endpoint + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': resource_key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text' : text
    }]
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    # print(response[0]['translations'][0]['text'])
    if request.status_code==200:
        translated_text = response[0]['translations'][0]['text']
        return translated_text
    else:
        print(f"Error: {request.status_code}")
        return "ot"+text

def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{'
                            '}?api_key=3bff838a120e02f0a6a0a0404b8afa14&language=en-US'.format(movie_id))
    data = response.json()
    # print(data)
    return "http://image.tmdb.org/t/p/w500/" + data['poster_path']


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

if 'target_language' not in st.session_state:
    st.session_state['target_language'] = 'en'
    st.session_state["Creator"] = 'Magicbus Team' #Can Insert your name here


st.title(translate_text('Movie Recommendendation System',st.session_state['target_language']))

selected_movie_name = st.selectbox(
    translate_text('Suggest me a movie: ',st.session_state['target_language']),
    movies['title'].values
)


if st.button(translate_text('Recommend',st.session_state['target_language'])):
    names, posters = recommend(selected_movie_name)

    #Comment this for English Movie Names!
    for i in range(len(names)):
        names[i] = translate_text(names[i],st.session_state['target_language'])


    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])




# Add translation language selection
tg_selector = st.empty()
target_language = tg_selector.selectbox(
    translate_text('Select target language for translation:',st.session_state['target_language']),
    ['En', 'Es', 'Fr', 'Hi', 'Mr'])  # Add more languages as needed


if st.button(translate_text('Translate to ',st.session_state['target_language']) + target_language.upper()):
    st.session_state['target_language'] = target_language.lower()
    st.rerun()

st.text(translate_text("If translation gives multiple boxes,please reload the page.",st.session_state["target_language"]))
st.text(f'Created by {st.session_state["Creator"]}')
