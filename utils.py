import requests 
import bs4
from tqdm import tqdm
import pandas as pd
from transformers import pipeline
import warnings 
import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import pandas as pd
import requests
import bs4
import re
import gc
warnings.filterwarnings('ignore')
classifier = pipeline("zero-shot-classification", device=0) #GPU
candidate_labels = ["positive", "negative"]

# 爬ettoday,輸出dataframe
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
    for d in soup.find(class_="part_list_2").find_all('h3'):
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
        soup = bs4.BeautifulSoup(requests.get(連結).text,"html.parser")
        內文 = re.sub('[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]+','',str(soup.select('div.story>p')))
        # 一個dataframe 三個欄位
        df_content.loc[idx,'title'] = 標題
        df_content.loc[idx,'url'] = 連結
        df_content.loc[idx,'content'] = 內文
    return df_content

# 將RAW DATA 有意義的 內文 撈出來
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

# 根據給定的URL計算出TOTAL有幾頁PAGE
def get_total_page_number(URL):
    response = requests.get(URL, headers = {'cookie': 'over18=1;'})
    soup = bs4.BeautifulSoup(response.text,"html.parser")
    number = int(str(soup.select('#action-bar-container > div > div.btn-group.btn-group-paging > a:nth-child(2)')[0]).split('index')[1].split('.html')[0])
    return number

# 根據URL取得這個PAGE的資料dataframe格式
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
    min_len = np.min([len(titles),len(urls),len(contents)])
    df['title'] = titles[:min_len]
    df['url'] = urls[:min_len]
    df['content'] = contents[:min_len]
    return df

# 根據URL和指定頁數取得串接多個PAGE後的dataframe格式資料
def get_some_page_ptt_data(URL,last_n_page):
    total_page_number = get_total_page_number(URL)
    URLS = [f"https://www.ptt.cc/bbs/HatePolitics/index{i}.html" for i in range(total_page_number,total_page_number-last_n_page,-1)]
    df = get_this_index_data(URL) #最新的PAGE
    for u in tqdm(URLS): #最近N個PAGE
        d = get_this_index_data(u)
        df = pd.concat([df,d]) #串起來
    return df

# 根據URL和指定數量PAGE和特定角色計算聲量分數
def get_score_by_person(URL,last_n_page,person_name,save=False,use_ettoday_data=False):
    gc.collect()
    df = get_some_page_ptt_data(URL,last_n_page)
    
    # 是否增加ettoday_data
    if use_ettoday_data == True:
        ettoday_data = craw_ettoday(hours=2)
        df = df.append(ettoday_data)
    
    if save == True:
        df.to_excel('data.xlsx')
    df['all_text'] = df['title'] + df['content']
    idx_lst = []
    for idx,text in enumerate(df['all_text']):
        if person_name in text:
            idx_lst.append(idx)
    key_df = df.iloc[idx_lst,:]
    key_df = key_df.reset_index(drop=True)
    print('資料筆數:',len(key_df))
    key_df['情緒'] = 0
    for idx,text in tqdm(enumerate(key_df['all_text'].values.tolist())):
        key_df.loc[idx,'情緒'] = classifier(text, candidate_labels)['labels'][0]
    score = (key_df['情緒']=='positive').sum()/(key_df['情緒']=='negative').sum()
    return score