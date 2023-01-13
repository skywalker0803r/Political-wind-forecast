import requests 
import bs4
from tqdm import tqdm
import pandas as pd
from transformers import pipeline
import warnings 
warnings.filterwarnings('ignore')
classifier = pipeline("zero-shot-classification", device=0) #GPU
candidate_labels = ["positive", "negative"]

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
    df['title'] = titles
    df['url'] = urls
    df['content'] = contents
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
def get_score_by_person(URL,last_n_page,person_name,save=False):
    df = get_some_page_ptt_data(URL,last_n_page)
    if save == True:
        df.to_excel('ptt_post.xlsx')
    df['all_text'] = df['title']+df['content']
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