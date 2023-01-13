import streamlit as st
from utils import *

#default parameter
URL = "https://www.ptt.cc/bbs/HatePolitics/index.html"
last_n_page = 100

st.set_page_config(page_title="Political Figure Popularity", page_icon=":guardsman:", layout="wide")
st.title("Political Figure Popularity")

#get input
figure_name = st.text_input("Enter the name of the political figure:")

#get URL
URL = st.text_input("Enter the URL:",value=URL)

#get last_n_page
last_n_page = st.number_input("Enter the last_n_page:",value=last_n_page)

if st.button('Submit'):
    #call the custom function
    score = get_score_by_person(URL,last_n_page,figure_name,save=False)
    #output the result
    st.success(f"{figure_name}'s popularity score is {score}")
