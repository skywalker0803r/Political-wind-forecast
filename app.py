import streamlit as st
from utils import *

use_data_list = []

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

# use data
use_ptt_data = True
ptt = st.checkbox('ptt')
if ptt:
    use_data_list.append('ptt')
    use_ptt_data = True

use_ettoday_data = False
ettoday = st.checkbox('ettoday')
if ettoday:
    use_data_list.append('ettoday')
    use_ettoday_data = True

if st.button('Submit'):
    st.write('使用資料如下')
    st.write(use_data_list)
    #call the custom function
    score = get_score_by_person(URL,last_n_page,figure_name,save=False,use_ettoday_data=use_ettoday_data)
    #output the result
    st.success(f"{figure_name}'s popularity score is {score}")
