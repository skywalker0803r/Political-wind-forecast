import requests
import bs4
import pandas as pd

url = "https://ctinews.com/"
response = requests.get(url)
soup = bs4.BeautifulSoup(response.text,"html.parser")
soup  = soup.find_all('a','news-link')
url_list = []
for i in soup:
    if 'title' in str(i):
        title = i.split('title=')[1]
        print(title)#.split('title=')[1])
        raise '123'
    url = str(i).split('href=')[1].split('rel')[0].split('title')[0].split("><")[0]
    if ('youtube' not in url) and ( 'videos' not in url):
        url = url.replace('"','')
        url = str('https://ctinews.com')+str(url)
        url_list.append(url)
    df = pd.DataFrame(columns=['url'])
    df['url'] = url_list
#print(df)
