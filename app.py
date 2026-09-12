import streamlit as st
import pickle
import pandas as pd
import requests
from urllib.parse import quote

# ---------------- CONFIG ----------------
TMDB_API_KEY = "a48e20546d3675de6a35034e12fdedb8"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
PLACEHOLDER_IMAGE = "https://placehold.co/500x750/1a1a1a/ffffff?text=No+Poster"

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies_df = pd.DataFrame(movies_dict)

    recommendations_dict = pickle.load(
        open('recommendations.pkl', 'rb')
    )

    return movies_df, recommendations_dict


movies, recommendations_dict = load_data()


# ---------------- FETCH POSTER FROM TMDB (with fallback) ----------------
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id, title=None):
    # Try by movie_id first
    try:
        if movie_id is not None and pd.notna(movie_id):
            url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}?api_key={TMDB_API_KEY}&language=en-US"
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                poster_path = response.json().get('poster_path')
                if poster_path:
                    return POSTER_BASE_URL + poster_path
    except Exception:
        pass

    # Fallback: search by title
    try:
        if title:
            search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={quote(title)}"
            response = requests.get(search_url, timeout=8)
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    poster_path = results[0].get('poster_path')
                    if poster_path:
                        return POSTER_BASE_URL + poster_path
    except Exception:
        pass

    return PLACEHOLDER_IMAGE


# ---------------- RECOMMENDATION FUNCTION ----------------
def recommend(movie_name):
    movie_index = movies[movies['title'] == movie_name].index[0]

    recommended_indices = recommendations_dict[movie_index]

    recommended_titles = []
    recommended_posters = []

    for index in recommended_indices:
        row = movies.iloc[index]

        title = row['title']
        movie_id = row['movie_id'] if 'movie_id' in movies.columns else None

        recommended_titles.append(title)
        recommended_posters.append(
            fetch_poster(movie_id, title)
        )

    return recommended_titles, recommended_posters


# ---------------- CUSTOM CSS (Netflix-style dark theme) ----------------
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(180deg, #141414 0%, #000000 100%);
        }
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0);
        }
        .main-title {
            text-align: center;
            font-size: 52px;
            font-weight: 900;
            color: #E50914;
            letter-spacing: 1px;
            margin-bottom: 0px;
            text-shadow: 0px 0px 20px rgba(229,9,20,0.4);
        }
        .sub-title {
            text-align: center;
            font-size: 17px;
            color: #B3B3B3;
            margin-bottom: 35px;
        }
        div[data-baseweb="select"] > div {
            background-color: #2b2b2b;
            border-color: #444;
            color: white;
        }
        div.stButton > button {
            width: 100%;
            background-color: #E50914;
            color: white;
            font-weight: 700;
            font-size: 16px;
            border-radius: 6px;
            padding: 12px;
            border: none;
            transition: background-color 0.2s ease;
        }
        div.stButton > button:hover {
            background-color: #f6121d;
            color: white;
        }
        .section-heading {
            color: #fff;
            font-size: 26px;
            font-weight: 700;
            margin-top: 10px;
            margin-bottom: 20px;
            border-left: 5px solid #E50914;
            padding-left: 12px;
        }
        .movie-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 22px;
            padding: 10px 0 40px 0;
        }
        @media (max-width: 1000px) {
            .movie-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        .movie-card {
            background: #181818;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        .movie-card:hover {
            transform: scale(1.06);
            box-shadow: 0 10px 28px rgba(229,9,20,0.35);
            z-index: 2;
        }
        .poster-img {
            width: 100%;
            height: 330px;
            object-fit: cover;
            display: block;
        }
        .movie-name {
            padding: 12px 10px;
            font-size: 14px;
            font-weight: 600;
            color: #ffffff;
            text-align: center;
            min-height: 42px;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<p class="main-title">🎬 MovieMatch</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Apni pasandeeda movie chuno, hum aapko milti-julti movies dikhayenge — poster ke saath!</p>', unsafe_allow_html=True)

# ---------------- SEARCH / SELECT ----------------
col_a, col_b, col_c = st.columns([1, 2, 1])
with col_b:
    selected_movie_name = st.selectbox(
        "🔍 Movie search karo ya list se select karo",
        movies['title'].values
    )
    show_button = st.button("Recommend Movies")

# ---------------- SHOW RESULTS ----------------
if show_button:
    with st.spinner("Recommendations la rahe hain..."):
        names, posters = recommend(selected_movie_name)

    st.markdown('<p class="section-heading">✨ Aapke liye recommended movies</p>', unsafe_allow_html=True)

    cards_html = '<div class="movie-grid">'
    for name, poster in zip(names, posters):
        cards_html += f'''
            <div class="movie-card">
                <img src="{poster}" class="poster-img" onerror="this.onerror=null;this.src='{PLACEHOLDER_IMAGE}';" />
                <div class="movie-name">{name}</div>
            </div>
        '''
    cards_html += '</div>'

    st.markdown(cards_html, unsafe_allow_html=True)