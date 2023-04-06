import streamlit as st
from utils import *
from PIL import Image

use_data_list = []

#預設的PTT政治板URL,和預設要抓幾頁:PTT_n_page
#URL = "https://www.ptt.cc/bbs/HatePolitics/index.html"

# 預設撈取頁面數量
PTT_n_page = 10
ettoday_n_page = 10
udn_n_page = 10
setn_n_page = 10
ctinews_n_page = 10

# 置入圖片和標題
st.set_page_config(page_title="政治人物聲量分數分析", page_icon=":guardsman:", layout="wide")
st.title("政治人物聲量分數分析")
image = Image.open('img.jpeg')
st.image(image, caption='')

# 兩種模式讓使用者切換
mode = st.selectbox(
    '選擇模式',
    ('即時爬取並預測', '上傳特定檔案預測'))
if mode == '上傳特定檔案預測':
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        dataframe = pd.read_excel(uploaded_file)
        st.write(dataframe)

#輸入政客名稱
with st.sidebar:
    person_name = st.text_input("輸入政治人物名稱:")

# 使用者定義參數 PTT_n_page
with st.sidebar:
    PTT_n_page = st.number_input("預設撈最近N頁PTT政治版的文章:",value=PTT_n_page)

# 用者定義參數 ettoday_n_page
with st.sidebar:
    ettoday_n_page = st.number_input("預設撈最近N頁ettoday的文章:",value=ettoday_n_page)

# 用者定義參數 udn_n_page
with st.sidebar:
    udn_n_page = st.number_input("預設撈最近N頁udn的文章:",value=udn_n_page)

# 用者定義參數 setn_n_page
with st.sidebar:
    setn_n_page = st.number_input("預設撈最近N頁setn的文章:",value=setn_n_page)

# 用者定義參數 ctinews_n_page
with st.sidebar:
    ctinews_n_page = st.number_input("預設撈最近N頁ctinews的文章:",value=ctinews_n_page)

# 使用者checkbox勾選是否使用該新聞網做為資料來源
with st.sidebar:
    use_ptt_data = True
    ptt = st.checkbox('ptt')
    if ptt:
        use_data_list.append('ptt')
        use_ptt_data = True

with st.sidebar:
    use_udn_data = False
    udn = st.checkbox('udn')
    if udn:
        use_data_list.append('udn')
        use_udn_data = True

with st.sidebar:
    use_ctinews_data = False
    ctinews = st.checkbox('ctinews')
    if ctinews:
        use_data_list.append('ctinews')
        use_ctinews_data = True

with st.sidebar:
    use_setnnews_data = False
    setnnews = st.checkbox('setnnews')
    if setnnews:
        use_data_list.append('setnnews')
        use_setnnews_data = True

# Submit按鈕設置
if st.button('Submit'):
    if mode == '即時爬取並預測':
        with st.sidebar:
            st.write('使用資料如下')
            st.write(use_data_list)
        score = get_score_by_person(
            PTT_n_page = PTT_n_page,
            ettoday_n_page = ettoday_n_page,
            udn_n_page = udn_n_page,
            setn_n_page = setn_n_page,
            ctinews_n_page = ctinews_n_page,
            person_name = person_name,
            save={'ptt':True,'ettoday':True,'udn':True,'ctinews':True,'setnnews':True},
            use_ettoday_data = False,
            use_udn_data = use_udn_data,
            use_ctinews_data = use_ctinews_data,
            use_setnnews_data = use_setnnews_data,
            )
        st.success(f"{person_name}'的政治聲量分數為:{score}")
    
    if mode == '上傳特定檔案預測':
        score = predict_function(dataframe,person_name)
        st.success(f"{person_name}'的政治聲量分數為:{score}")
