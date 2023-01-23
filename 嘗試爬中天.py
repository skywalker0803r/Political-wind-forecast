import requests
import bs4
import pandas as pd
import numpy as np
from tqdm import tqdm_notebook as tqdm


def 爬中天新聞():
    url = "https://ctinews.com/"
    soup = bs4.BeautifulSoup(requests.get(url).text,"html.parser")
    result = soup.find_all('a','news-link')
    urls = []
    titles = []
    contents = []
    for i in tqdm(result[:5]):
        i = str(i)
        try:
            title = i.split('title')[1].split('><')[0].split('「')[1].split('」')[0]
            url = i.split("href")[1].split('title')[0].replace('=','').replace('"','')[:22]
            url = f'https://ctinews.com{url}'
            content = bs4.BeautifulSoup(requests.get(url).text,"html.parser")
            urls.append(url)
            titles.append(title)
            contents.append(content)
        except:
            pass
    df = pd.DataFrame()
    min_len = np.min([len(titles),len(urls),len(contents)])
    df['title'] = titles[:min_len]
    df['url'] = urls[:min_len]
    df['content'] = contents[:min_len]
    return df

if __name__ == '__main__':
    爬中天新聞()