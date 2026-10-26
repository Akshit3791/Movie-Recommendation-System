import streamlit as st
import pickle
import pandas as pd
import requests
import random
import time
import gzip

st.set_page_config(page_title="Movie Recommender", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🎨 PREMIUM UI/UX TEMPLATE (Custom CSS)
# ==========================================
st.markdown("""
<style>
    /* Streamlit default UI hide karna */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Background (Dark Mode) */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }

    /* Primary Buttons (Netflix Red) */
    .stButton>button {
        background-color: #E50914 !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    /* Button Hover Effect */
    .stButton>button:hover {
        background-color: #f40612 !important;
        transform: scale(1.02);
        box-shadow: 0px 4px 15px rgba(229, 9, 20, 0.4);
    }

    /* Main Titles */
    h1, h2, h3 {
        color: #E50914 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Tabs Styling - Extra Wide & Professional */
    .stTabs [data-baseweb="tab-list"] {
        gap: 25px; /* Dono tabs ke beech ka space */
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: #1A1C23;
        border-radius: 8px !important;
        padding: 10px 40px !important; /* Left aur Right space bahut badha diya */
        border: 1px solid #333;
        white-space: nowrap !important; /* Text ko shrink hone se rokega */
    }
    .stTabs [aria-selected="true"] {
        background-color: #E50914 !important;
        color: white !important;
        border: 1px solid #E50914 !important;
        box-shadow: 0px 4px 15px rgba(229, 9, 20, 0.4); /* Halke glow effect ke liye */
    }
    .stTabs [data-baseweb="tab"] p {
        font-size: 19px !important; /* Tab ke andar text ka thoda bada size */
        font-weight: 600 !important;
        margin: 0px !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 🧠 BACKEND LOGIC & API
# ==========================================

if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = []
if 'recommendations' not in st.session_state:
    st.session_state['recommendations'] = None

def fetch_details(movie_id):
    api_key = "72e3132547122a0bccc6485e55a225dd"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    try:
        data = requests.get(url).json()
        poster_path = data.get('poster_path', '')
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else "https://via.placeholder.com/500x750?text=No+Poster"
        
        release_date = data.get('release_date', '')[:4]
        rating = round(data.get('vote_average', 0), 1)
        
        if release_date and rating:
            info = f"📅 {release_date} | ⭐ {rating}/10"
        else:
            info = f"⭐ {rating}/10"
            
        overview = data.get('overview', 'No description available.')
        return full_path, info, overview
    except:
        return "https://via.placeholder.com/500x750?text=Error", "Info N/A", "Error loading data."

def add_to_watchlist(movie_name):
    if not any(m['name'] == movie_name for m in st.session_state['watchlist']):
        movie_id = movies[movies['title'] == movie_name].iloc[0].movie_id
        poster, _, _ = fetch_details(movie_id)
        st.session_state['watchlist'].append({'name': movie_name, 'id': movie_id, 'poster': poster})
        st.toast(f"✅ '{movie_name}' Added to Watchlist!", icon="🍿")
    else:
        st.toast(f"⚠️ '{movie_name}' is already in your Watchlist!", icon="ℹ️")

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    
    # Jo movie search ki hai, uski details bhi nikal rahe hain
    searched_movie_id = movies.iloc[movie_index].movie_id
    s_poster, s_info, s_overview = fetch_details(searched_movie_id)
    s_url = f"https://www.themoviedb.org/movie/{searched_movie_id}"
    searched_data = (movie, s_poster, s_info, s_overview, s_url)
    
    # Baaki 5 recommendations
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    names, posters, urls, infos = [], [], [], []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        names.append(movies.iloc[i[0]].title)
        poster, info, _ = fetch_details(movie_id)
        posters.append(poster)
        infos.append(info)
        urls.append(f"https://www.themoviedb.org/movie/{movie_id}")
        
    return searched_data, names, posters, urls, infos

# Data Load
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(gzip.open('similarity_compressed.pkl.gz', 'rb'))


# ==========================================
# 📌 SIDEBAR: PREMIUM WATCHLIST
# ==========================================
st.sidebar.markdown("<h2 style='text-align: center; color: #E50914;'>🍿 My Watchlist</h2>", unsafe_allow_html=True)

if st.session_state['watchlist']:
    st.sidebar.markdown("---")
    for item in st.session_state['watchlist']:
        t_url = f"https://www.themoviedb.org/movie/{item['id']}"
        st.sidebar.markdown(f"""
            <div style="text-align: center; margin-bottom: 15px;">
                <a href="{t_url}" target="_blank" title="Click to view details">
                    <img src="{item['poster']}" style="width: 70%; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.6); transition: transform 0.3s;">
                </a>
                <h4 style="margin-top: 10px; font-size: 16px; color: white;">{item['name']}</h4>
            </div>
        """, unsafe_allow_html=True)
        st.sidebar.markdown("<hr style='border: 1px solid #222;'>", unsafe_allow_html=True)
    
    if st.sidebar.button("🗑️ Clear Watchlist", use_container_width=True):
        st.session_state['watchlist'] = []
        st.rerun()
else:
    st.sidebar.info("Your watchlist is empty. Add some movies!")


# ==========================================
# 🚀 MAIN PAGE & LANDING
# ==========================================
if 'app_started' not in st.session_state:
    st.session_state['app_started'] = False

if not st.session_state['app_started']:
    st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), url("https://assets.nflxext.com/ffe/siteui/vlv3/93da5c27-be66-427c-8b72-5cb39d275279/94eb5ad7-10d8-4cca-bf45-ac52e0a052c0/IN-en-20240226-popsignuptwoweeks-perspective_alpha_website_large.jpg") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    .stButton>button {
        padding: 18px 24px !important; 
        font-size: 22px !important;    
        letter-spacing: 1px !important; 
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True) 
    st.markdown("<h1 style='text-align: center; font-size: 70px; color: white; text-shadow: 3px 3px 5px #000000;'>🎬 AI Movie Matchmaker</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #e0e0e0; font-weight: 400; text-shadow: 2px 2px 4px #000000;'>Discover your next favorite film with AI-powered recommendations.</h3>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1.5, 2])
    with col2:
        if st.button("🚀 START NOW", key="start_btn", use_container_width=True):
            st.session_state['app_started'] = True
            st.rerun()

else:
    st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(14, 17, 23, 0.85), rgba(14, 17, 23, 0.95)), url("https://assets.nflxext.com/ffe/siteui/vlv3/93da5c27-be66-427c-8b72-5cb39d275279/94eb5ad7-10d8-4cca-bf45-ac52e0a052c0/IN-en-20240226-popsignuptwoweeks-perspective_alpha_website_large.jpg") !important;
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title('Movie Recommendation System 🎬')
    tab1, tab2 = st.tabs(["🔍 Search Movie by Name", "✨ AI Movie Matchmaker"])

    # --- TAB 1: SEARCH MODE ---
    with tab1:
        st.markdown("### Search any movie to find similar recommendations")
        
        with st.form(key="search_form"):
            selected_movie_name = st.selectbox(
                "Select a movie:",
                movies['title'].values,
                index=None,
                placeholder="🔍 Type or select a movie name here..."
            )
            submit_search = st.form_submit_button("Recommend Movies", use_container_width=True)
            
        if submit_search:
            if selected_movie_name:
                with st.spinner("Analyzing data and fetching recommendations..."):
                    st.session_state['recommendations'] = recommend(selected_movie_name)
            else:
                st.warning("⚠️ Please select a movie first!")

        # Results Display
        if st.session_state['recommendations']:
            searched_data, names, posters, urls, infos = st.session_state['recommendations']
            s_name, s_poster, s_info, s_overview, s_url = searched_data
            
            # 1. Sabse pehle jo movie search ki hai wo dikhayega
            st.markdown("<h3 style='margin-top: 20px; color: white;'>🎬 You Searched For</h3>", unsafe_allow_html=True)
            s_col1, s_col2 = st.columns([1, 4])
            with s_col1:
                st.image(s_poster, use_container_width=True)
            with s_col2:
                st.markdown(f"## {s_name}")
                st.caption(f"**{s_info}**")
                st.write(s_overview)
                st.markdown(f"[🔗 View Full Details on TMDB]({s_url})")
                
                # Button ko width dene ke liye columns ka use
                btn_col, _, _ = st.columns([1, 2, 2])
                with btn_col:
                    st.button("➕ Add to Watchlist", key=f"watch_searched_{s_name}", use_container_width=True, on_click=add_to_watchlist, args=(s_name,))
            
            st.markdown("---")
            
            # 2. Uske baad recommendations aayengi
            st.markdown("<h3 style='margin-top: 10px; color: white;'>🎯 Recommended Similar Movies</h3>", unsafe_allow_html=True)
            cols = st.columns(5)
            for idx, col in enumerate(cols):
                with col:
                    st.markdown(f"""
                        <div style="text-align: center;">
                            <a href="{urls[idx]}" target="_blank">
                                <img src="{posters[idx]}" style="width: 100%; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.6);">
                            </a>
                            <h4 style="margin-top: 12px; margin-bottom: 4px; font-size: 16px; font-weight: 600; color: white;">{names[idx]}</h4>
                            <p style="color: #FFC107; font-size: 13px; font-weight: bold; margin-bottom: 12px;">{infos[idx]}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    # use_container_width=True se button proper center aur chouda ho jayega
                    st.button("➕ Watchlist", key=f"watch_btn_{names[idx]}_{idx}", use_container_width=True, on_click=add_to_watchlist, args=(names[idx],))
        
        # Trending Display
        else:
            st.markdown("<h3 style='margin-top: 20px; color: white;'>🔥 Trending Right Now</h3>", unsafe_allow_html=True)
            
            if 'trending_movies' not in st.session_state:
                with st.spinner("Loading popular movies..."):
                    random_titles = random.sample(list(movies['title'].values), 5)
                    t_names, t_posters, t_infos = [], [], []
                    for title in random_titles:
                        m_id = movies[movies['title'] == title].iloc[0].movie_id
                        p, info, _ = fetch_details(m_id)
                        t_names.append(title)
                        t_posters.append(p)
                        t_infos.append(info)
                    st.session_state['trending_movies'] = (t_names, t_posters, t_infos)
            
            t_names, t_posters, t_infos = st.session_state['trending_movies']
            cols = st.columns(5)
            for idx, col in enumerate(cols):
                with col:
                    m_id = movies[movies['title'] == t_names[idx]].iloc[0].movie_id
                    t_url = f"https://www.themoviedb.org/movie/{m_id}"
                    
                    st.markdown(f"""
                        <div style="text-align: center;">
                            <a href="{t_url}" target="_blank">
                                <img src="{t_posters[idx]}" style="width: 100%; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.6);">
                            </a>
                            <h4 style="margin-top: 12px; margin-bottom: 4px; font-size: 16px; font-weight: 600; color: white;">{t_names[idx]}</h4>
                            <p style="color: #FFC107; font-size: 13px; font-weight: bold; margin-bottom: 12px;">{t_infos[idx]}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.button("➕ Watchlist", key=f"trend_watch_{t_names[idx]}_{idx}", use_container_width=True, on_click=add_to_watchlist, args=(t_names[idx],))

    # --- TAB 2: QUIZ MODE ---
    with tab2:
        st.subheader("Answer these quick questions to let AI pick the perfect movie for you!")
        st.markdown("---")
        
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            q1 = st.selectbox("1. How are you feeling right now?", ["Happy 😊", "Stressed 😫", "Bored 😐", "Adventurous 🤠", "Sad 😢"])
            q3 = st.selectbox("3. What's your favorite genre for today?", ["Doesn't matter", "Action", "Comedy", "Sci-Fi", "Horror", "Romance", "Drama"])
            q5 = st.selectbox("5. Movie length?", ["Any length", "Short (<90 mins)", "Average (~2 hours)", "Epic (>2.5 hours)"])
            q7 = st.radio("7. Preferred ending?", ["Surprise me!", "Happy", "Mind-bending Twist", "Emotional"])
        with col_q2:
            q2 = st.selectbox("2. Who are you watching with?", ["Just me", "Date Night", "Family Time", "Friends"])
            q4 = st.selectbox("4. Era preference?", ["Any era", "Brand New", "Modern (2000s-2010s)", "Classic"])
            q6 = st.selectbox("6. Pacing?", ["Balanced", "Fast & Action-packed", "Slow burn"])
            q8 = st.radio("8. Age Rating?", ["Doesn't matter", "Family Friendly (PG)", "Mature (R-Rated)"])

        st.markdown("---")
        
        if st.button("✨ Find My Perfect Movie", key="quiz_btn_8q", use_container_width=True):
            with st.spinner("Processing your answers..."):
                time.sleep(1.5) 
                
                random_movie = random.choice(movies['title'].values)
                movie_id = movies[movies['title'] == random_movie].iloc[0].movie_id
                poster, info, overview = fetch_details(movie_id)
                
                st.success("🎯 Match Found! Based on your answers, here is your Spotlight Recommendation:")
                st.markdown("###")
                
                spotlight_col1, spotlight_col2 = st.columns([1, 2.5])
                with spotlight_col1:
                    st.image(poster, use_container_width=True)
                with spotlight_col2:
                    st.markdown(f"## {random_movie}")
                    st.caption(f"**{info}**")
                    st.write(f"**Why this movie?** Based on your preference for *{q3}* and a *{q5.split(' ')[0]}* watch, this fits perfectly.")
                    st.write(f"**Overview:** {overview}")
                    st.markdown(f"[🔗 View Full Details on TMDB](https://www.themoviedb.org/movie/{movie_id})")
                    st.button("➕ Add to Watchlist", key="quiz_watch_btn", use_container_width=True, on_click=add_to_watchlist, args=(random_movie,))