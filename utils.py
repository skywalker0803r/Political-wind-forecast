import requests 
#from selenium import webdriver
import bs4
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from transformers import pipeline
from tqdm import tqdm
import pandas as pd
import numpy as np
import time
import re
import gc
import warnings 
import streamlit as st
warnings.filterwarnings('ignore')

def predict_function(df,person_name,min_data_n=3): #最小資料量min_data_n
    # 合併標題和內文
    df['all_text'] = df['title'] + df['content']
    idx_lst = []
    # 對每一筆新聞進行遍歷
    for idx,text in enumerate(df['all_text']):
        text = str(text)
        # 檢查該政治人物是否出現在文章中
        if person_name in text:
            idx_lst.append(idx)
    # 擷取出有出現特定政治人物的df
    person_name_df = df.iloc[idx_lst,:]
    person_name_df = person_name_df.reset_index(drop=True)
    # 計算一共有多少筆談論該政治人物的文章
    st.write(f'出現{person_name}的資料筆數:',len(person_name_df))
    # 資料不足的情況
    if len(person_name_df) < min_data_n:
        st.write(f'資料過少,少於{n}筆')
    
    # 評分機制 由特定pretrain model做zero-shot-classification看這則文章屬於["positive", "negative"]哪一種
    st.write('create classifier pipeline')
    person_name_df['情緒'] = 0
    classifier = pipeline(
        task="zero-shot-classification", 
        model='joeddav/xlm-roberta-large-xnli',#joeddav/xlm-roberta-large-xnli有支援中文
        device='cpu',
        use_auth_token=True) 
    candidate_labels = ["positive", "negative"]
    
    # 對文章做遍歷個別去計算情緒分數
    st.write('遍歷爬取到的文章個別去計算情緒分數')
    for idx,text in tqdm(enumerate(person_name_df['all_text'].values.tolist())):
        person_name_df.loc[idx,'情緒'] = classifier(text,candidate_labels)['labels'][0]
    
    # 最後將score定義為:positive.sum()/negative.sum()
    st.write("對情緒分數取平均")
    if (person_name_df['情緒']=='negative').sum() > 0:
        score = (person_name_df['情緒']=='positive').sum()/(person_name_df['情緒']=='negative').sum()
    # 分母為0無法計算
    else: 
        score = "score = (person_name_df['情緒']=='positive').sum()/(person_name_df['情緒']=='negative').sum() but can not caculate"
    
    return score

# 輸入句子前處理函數返回乾淨句子
def preprocess_raw_sentence(x):
    x = re.sub(r'[a-zA-Z]','',x) #去除英文
    x = re.sub(r'[\d]','',x) #去除數字
    x = re.sub(r'[^\w\s]','',x) #去除標點符號
    x = x.replace('\n', '').replace('\r', '').replace('\t', '') #去除換行符號
    str.strip(x) # 去除左右空白
    return x 

# 爬三立新聞網
def craw_setn(n=10):
    data ={'titles':[],'urls':[],'contents':[]}
    soup = BeautifulSoup(requests.get('https://www.setn.com/Catalog.aspx?PageGroupID=6').text, 'lxml')
    for s in tqdm(soup.find_all('a',pl='熱門新聞')[:n]):
        data['titles'].append(s.text) 
        data['urls'].append('https://www.setn.com' + s['href'])
        data['contents'].append(BeautifulSoup(requests.get(data['urls'][-1]).text,'lxml').find_all('article')[0].text)
        time.sleep(1)
    df = pd.DataFrame()
    df['title'] = data['titles']
    df['url'] = data['urls']
    df['content'] = data['contents']
    return df

# 爬中天新聞網
def craw_ctinews(n=5,sleep_time=3):
    soup = BeautifulSoup(requests.get('https://ctinews.com/').text, 'lxml')
    titles = []
    urls = []
    contents = []
    for s in soup.find_all('div', class_='base-card__news-title')[:n]:
        try:
            titles.append(s.text)
            urls.append('https://ctinews.com'+re.search('href="(.+?)"', str(s)).group(1))
            contents.append(BeautifulSoup(requests.get(urls[-1]).text,'html.parser').find_all('div',class_='rendered-content em:text-xl leading-normal ck-content')[0].text)
            time.sleep(sleep_time)
        except:
            df = pd.DataFrame()
            df['title'] = ['--','--']
            df['url'] = ['--','--']
            df['content'] = ['--','--']
            return df
    df = pd.DataFrame()
    df['title'] = titles
    df['url'] = urls
    df['content'] = contents
    return df

# 爬UDN新聞網
def craw_UDN(n):
    r = requests.get('https://udn.com/rank/pv/2')
    df = pd.DataFrame()
    titles = []
    urls = []
    contents = []
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        stories = soup.find_all('a', class_='story-list__image--holder')
        for s in tqdm(stories[:n]):
            if type(s.get('aria-label')) is str:  
                titles.append(s['aria-label'])
                urls.append(s.get('href'))
                contents.append(preprocess_raw_sentence(str(BeautifulSoup(requests.get(s.get('href')).text, 'html.parser').find_all('section', class_='article-content__editor'))))
    df['title'] = titles
    df['url'] = urls
    df['content'] = contents
    return df

# 爬ettoday新聞網
'''
def craw_ettoday(hours=2): # hours=2控制資料量
    browser = webdriver.Chrome(executable_path='./chromedriver')
    browser.get("https://www.ettoday.net/news/news-list.htm")
    two_hours_ago = datetime.now() - timedelta(hours = hours)
    print(two_hours_ago)
    two_hours_ago_time = two_hours_ago.strftime("%Y/%m/%d %H:%M")
    print("兩小時前時間：", two_hours_ago_time)
    last_height = browser.execute_script("return document.body.scrollHeight")
    go=True
    while go:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        html_source = browser.page_source
        soup = BeautifulSoup(html_source, "lxml")
        new_height = browser.execute_script("return document.body.scrollHeight")
        #已經到頁面底部
        if new_height == last_height:
            print("已經到頁面最底部，程序停止")
            break
        last_height = new_height
        for d in soup.find(class_="part_list_2").find_all('h3'):
            #已經超出兩小時
            if datetime.strptime(d.find(class_="date").text, '%Y/%m/%d %H:%M') < two_hours_ago:
                print("已經超出兩個小時，程序停止")
                go = False
                break
            else:
                print("目前畫面最下方文章的日期時間為：",d.find_all(class_="date")[-1].text)
    html_source = browser.page_source
    soup = BeautifulSoup(html_source, "lxml")
    news ={"日期時間":[],"標題":[],"連結":[]}
    for d in tqdm(soup.find(class_="part_list_2").find_all('h3')):
        if two_hours_ago_time in d.find(class_="date") :
            pass
        else:
            print(d.find(class_="date").text, d.find_all('a')[-1].text)
            news["日期時間"].append(d.find(class_="date").text)
            news["標題"].append(d.find_all('a')[-1].text)
            news["連結"].append("https://www.ettoday.net" + d.find_all('a')[-1]["href"])
    browser.close()  #很重要喔記得要關掉瀏覽器．不然要手動關掉
    df_news=pd.DataFrame(news)
    df_content = pd.DataFrame(columns=['title','url','content'])
    for idx in df_news.index:
        標題 = df_news.loc[idx,'標題']
        連結 = df_news.loc[idx,'連結']
        內文  = bs4.BeautifulSoup(requests.get(連結).text,'html.parser').find_all('div',class_='story')[0].text.replace('\n','')
        # 一個dataframe 三個欄位
        df_content.loc[idx,'title'] = 標題
        df_content.loc[idx,'url'] = 連結
        df_content.loc[idx,'content'] = 內文
    return df_content
'''

# 爬ptt政治板
def get_some_page_ptt_data(URL="https://www.ptt.cc/bbs/HatePolitics/index.html",PTT_n_page=10):
    def get_content(soup):
        ## 查找所有html 元素 抓出內容
        main_container = soup.find(id='main-container')
        # 把所有文字都抓出來
        all_text = main_container.text
        # 把整個內容切割透過 "-- " 切割成2個陣列
        pre_text = all_text.split('--')[0]
        # 把每段文字 根據 '\n' 切開
        texts = pre_text.split('\n')
        # 如果你爬多篇你會發現 
        contents = texts[2:]
        # 內容
        content = ''.join(contents)
        return content
    
    # 根據PTT的URL取得這個PTT頁面的資料的DataFrame格式
    def get_this_index_data(URL="https://www.ptt.cc/bbs/HatePolitics/index.html"):
        # 發送get 請求 到 ptt 八卦版
        response = requests.get(URL, headers = {'cookie': 'over18=1;'})
        
        #  把網頁程式碼(HTML) 丟入 bs4模組分析
        soup = bs4.BeautifulSoup(response.text,"html.parser")

        ## PTT 上方4個欄位
        result = soup.find_all('div','title')
        urls = []
        titles = []
        contents = []
        for i in result:
            try:
                post_url = 'https://www.ptt.cc'+str(i).split('href="')[1].split('">')[0]
                urls.append(post_url)
                titles.append(str(i).split("]")[1].split("<")[0])
                response = requests.get(post_url, headers = my_headers)
                soup = bs4.BeautifulSoup(response.text,"html.parser")
                contents.append(get_content(soup))
            except:
                pass #(本文已被刪除)
        df = pd.DataFrame()
        df['title'] = titles
        df['url'] = urls
        df['content'] = contents
        return df
    
    # 計算目前ptt政治版總共有多少page
    def get_total_page_number(URL="https://www.ptt.cc/bbs/HatePolitics/index.html"):
        response = requests.get(URL, headers = {'cookie': 'over18=1;'})
        soup = bs4.BeautifulSoup(response.text,"html.parser")
        number = int(str(soup.select('#action-bar-container > div > div.btn-group.btn-group-paging > a:nth-child(2)')[0]).split('index')[1].split('.html')[0])
        return number
    
    total_page_number = get_total_page_number(URL="https://www.ptt.cc/bbs/HatePolitics/index.html")
    
    # 取得一些政治板page的連結稱為URLS
    URLS = [f"https://www.ptt.cc/bbs/HatePolitics/index{i}.html" for i in range(total_page_number,total_page_number-PTT_n_page,-1)]
    
    # 根據特定URL取得這個PAGE的資料dataframe格式
    def get_this_index_data(URL):
        # 設定Header與Cookie
        my_headers = {'cookie': 'over18=1;'}
        # 發送get 請求 到 ptt 八卦版
        response = requests.get(URL, headers = my_headers)
        #  把網頁程式碼(HTML) 丟入 bs4模組分析
        soup = bs4.BeautifulSoup(response.text,"html.parser")
        ## PTT 上方4個欄位
        result = soup.find_all('div','title')
        urls = []
        titles = []
        contents = []
        for i in tqdm(result):
            try:
                titles.append(i.text.replace("\n",''))
                urls.append('https://www.ptt.cc'+str(i.find_all('a')[0]['href']))
                response = requests.get(urls[-1], headers = my_headers)
                soup = bs4.BeautifulSoup(response.text,"html.parser")
                contents.append(get_content(soup))
            except:
                print('頁面刪除')
        df = pd.DataFrame()
        min_len = min(len(titles),len(urls),len(contents))
        df['title'] = titles[:min_len]
        df['url'] = urls[:min_len]
        df['content'] = contents[:min_len]
        return df
    
    #取得PTT政治板最新的PAGE
    df = get_this_index_data(URL) 
    for u in tqdm(URLS): #對URLS做遍歷
        df = df.append(get_this_index_data(u))
    return df

# 根據指定PAGE數量做爬蟲和特定角色計算聲量分數
def get_score_by_person(
    PTT_n_page = 10,
    ettoday_n_page = 10,
    udn_n_page = 10,
    setn_n_page = 10,
    ctinews_n_page = 10,
    person_name = '蔡英文',
    save={'ptt':True,'ettoday':True,'udn':True,'ctinews':True,'setnnews':True},
    use_ettoday_data = False,
    use_udn_data = False,
    use_ctinews_data = False,
    use_setnnews_data = False,
    ):
    # 釋放記憶體
    gc.collect()
    # 取得PTT資料
    df = get_some_page_ptt_data(
        URL="https://www.ptt.cc/bbs/HatePolitics/index.html",
        PTT_n_page=PTT_n_page)
    # 判斷是否保存資料
    if save['ptt'] == True:
        df.to_excel('ptt.xlsx')
    print(f'ptt資料數{len(df)}')
    
    # 是否增加ettoday_data資料
    if use_ettoday_data == True:
        ettoday_data = craw_ettoday(hours=ettoday_n_page)
        # 判斷是否保存資料
        if save['ettoday'] == True:
            try:
                ettoday_data.to_excel('./ettoday.xlsx')
            except:
                pass
        # 與現有的資料進行合併
        df = df.append(ettoday_data)
        print(f'ettoday資料數{len(ettoday_data)}')
    
    # 是否增加udn_data資料
    if use_udn_data == True:
        udn_data = craw_UDN(n=udn_n_page)
        # 判斷是否保存資料
        if save['udn'] == True:
            try:
                udn_data.to_excel('./udn.xlsx')
            except:
                pass
        # 與現有的資料進行合併
        df = df.append(udn_data)
        print(f'udn資料數{len(udn_data)}')
    
    # 是否增加ctinews_data資料
    if use_ctinews_data == True:
        ctinews_data = craw_ctinews(n=ctinews_n_page,sleep_time=3)
        # 判斷是否保存資料
        if save['ctinews'] == True:
            try:
                ctinews_data.to_excel('./ctinews_data.xlsx')
            except:
                pass
        # 與現有資料進行合併
        df = df.append(ctinews_data)
        print(f'ctinews資料數{len(ctinews_data)}')
    
    # 是否增加setn_data資料
    if use_setnnews_data == True:
        setn_data = craw_setn(n=setn_n_page)
        # 判斷是否保存資料
        if save['setnnews'] == True:
            try:
                setn_data.to_excel('./setn_data.xlsx')
            except:
                pass
        # 與現有資料進行合併
        df = df.append(setn_data)
        print(f'setnnews資料數{len(setn_data)}')
    
    # 將合併後的資料和政治人物名稱帶入predict_function取得最後評分結果返回
    return predict_function(df,person_name)