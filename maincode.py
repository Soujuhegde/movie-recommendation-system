import streamlit as st
from PIL import Image
import json
from Classifier import KNearestNeighbours  # Assuming this is a custom implementation
from bs4 import BeautifulSoup
import requests
import io
from urllib.request import urlopen
from imdb import IMDb

# Set page configuration first
st.set_page_config(
    page_title="🎬 Movie Recommender System",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
with open('C:/Users/Sadguru/PycharmProjects/final project/.venv/movie_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
with open('C:/Users/Sadguru/PycharmProjects/final project/.venv/movie_titles.json', 'r', encoding='utf-8') as f:
    movie_titles = json.load(f)

hdr = {'User-Agent': 'Mozilla/5.0'}

# Create an instance of IMDb
ia = IMDb()

# Function to fetch movie rating
def get_movie_rating(movie_title):
    movie_search = ia.search_movie(movie_title)
    if movie_search:
        movie_id = movie_search[0].movieID
        movie = ia.get_movie(movie_id)
        rating = movie.data.get('rating')
        return rating if rating else 0  # Return 0 if no rating found
    else:
        return 0

# Function to fetch and display movie poster
def fetch_movie_poster(imdb_link):
    url_data = requests.get(imdb_link, headers=hdr).text
    s_data = BeautifulSoup(url_data, 'html.parser')
    imdb_dp = s_data.find("meta", property="og:image")
    if imdb_dp:
        movie_poster_link = imdb_dp.attrs['content']
        u = urlopen(movie_poster_link)
        raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        image = image.resize((158, 301))
        st.image(image, use_column_width=False)
    else:
        st.error("Movie poster not found.")

# Function to recommend movies based on KNN
def recommend_movies(test_point, k):
    target = [0 for _ in movie_titles]
    model = KNearestNeighbours(data, target, test_point, k=k)
    model.fit()
    recommendations = [[movie_titles[i][0], movie_titles[i][2], data[i][-1]] for i in model.indices]

    # Fetch ratings for each recommended movie
    recommendations_with_ratings = [(rec[0], rec[1], get_movie_rating(rec[0])) for rec in recommendations]

    # Sort recommendations based on rating in descending order
    recommendations_with_ratings.sort(key=lambda x: x[2], reverse=True)
    return recommendations_with_ratings

# Custom CSS for enhanced styling
st.markdown("""
    <style>
    body {
        background-color: #f0f4f6;
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
        box-shadow: 0px 0px 10px 0px rgba(0,0,0,0.1);
        border-radius: 10px;
    }
    .stButton > button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
    }
    .stButton > button:hover {
        background-color: #2980b9;
    }
    .stSelectbox {
        background-color: #ecf0f1;
    }
    .stTable th {
        background-color: #3498db;
        color: white;
    }
    .stTable td {
        background-color: #ecf0f1;
    }
    .stMarkdown a {
        color: #2980b9;
    }
    </style>
    """, unsafe_allow_html=True)

# Main function
def run():
    st.sidebar.image('C:/Users/Sadguru/PycharmProjects/final project/.venv/logo.jpg', use_column_width=True)
    st.sidebar.title("🎬 Movie Recommender System")
    st.sidebar.markdown("**Data is based on 'IMDB 5000 Movie Dataset'**")

    genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
              'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']

    movies = [title[0] for title in movie_titles]
    category = ['--Select--', 'Movie based', 'Genre based']

    cat_op = st.sidebar.selectbox('🎥 Select Recommendation Type', category)

    if cat_op == category[0]:
        st.sidebar.warning('Please select Recommendation Type!!')
    elif cat_op == category[1]:
        select_movie = st.sidebar.selectbox('🎬 Select movie: (Recommendation will be based on this selection)',
                                            ['--Select--'] + movies)
        if select_movie == '--Select--':
            st.sidebar.warning('Please select a movie!!')
        else:
            dec = st.sidebar.radio("🖼️ Do you want to fetch the movie poster?", ('Yes', 'No'))
            no_of_reco = st.sidebar.slider('🎞️ Number of movies you want recommended:', min_value=5, max_value=20, step=1, value=10)
            if st.sidebar.button('🚀 Get Recommendations'):
                genres = data[movies.index(select_movie)]
                test_points = genres
                table = recommend_movies(test_points, no_of_reco + 1)
                table.pop(0)
                st.success('🌟 Some of the movies from our recommendations are listed below:')
                for c, (movie, link, rating) in enumerate(table, 1):
                    st.markdown(f"**{c}.** [{movie}]({link}) - IMDb Rating: {rating} ⭐")
                    if dec == 'Yes':
                        fetch_movie_poster(link)
    elif cat_op == category[2]:
        sel_gen = st.sidebar.multiselect('🎥 Select Genres:', genres)
        if sel_gen:
            dec = st.sidebar.radio("🖼️ Do you want to fetch the movie poster?", ('Yes', 'No'))
            imdb_score = st.sidebar.slider('🎞️ Choose IMDb score:', 1, 10, 8)
            no_of_reco = st.sidebar.number_input('🚀 Number of movies:', min_value=5, max_value=20, step=1, value=10)
            if st.sidebar.button('Get Recommendations'):
                test_point = [1 if genre in sel_gen else 0 for genre in genres]
                test_point.append(imdb_score)
                table = recommend_movies(test_point, no_of_reco)
                st.success('🌟 Some of the movies from our recommendations are listed below:')
                for c, (movie, link, rating) in enumerate(table, 1):
                    st.markdown(f"**{c}.** [{movie}]({link}) - IMDb Rating: {rating} ⭐")
                    if dec == 'Yes':
                        fetch_movie_poster(link)

if __name__ == "__main__":
    run()
