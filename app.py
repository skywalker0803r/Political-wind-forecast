import streamlit as st
from utils import *

use_data_list = []

#預設的PTT政治板URL,和預設要抓幾頁:last_n_page
URL = "https://www.ptt.cc/bbs/HatePolitics/index.html"
last_n_page = 100

st.set_page_config(page_title="政治人物聲量分數分析", page_icon=":guardsman:", layout="wide")
st.title("政治人物聲量分數分析")

#輸入政客名稱
figure_name = st.text_input("輸入政治人物名稱:")

#get URL
URL = st.text_input("預設PTT政治板URL:",value=URL)

#get last_n_page
last_n_page = st.number_input("預設撈最近N頁PTT政治版的文章:",value=last_n_page)

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

use_udn_data = False
udn = st.checkbox('udn')
if udn:
    use_data_list.append('udn')
    use_udn_data = True

use_ctinews_data = False
ctinews = st.checkbox('ctinews')
if ctinews:
    use_data_list.append('ctinews')
    use_ctinews_data = True

if st.button('Submit'):
    st.write('使用資料如下')
    st.write(use_data_list)
    score = get_score_by_person(URL,last_n_page,figure_name,save=False,
    use_ettoday_data=use_ettoday_data,
    use_udn_data=use_udn_data,
    use_ctinews_data=use_ctinews_data
    )
    st.success(f"{figure_name}'的政治聲量分數為:{score}")
