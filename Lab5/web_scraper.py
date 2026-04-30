import requests
import datetime
from bs4 import BeautifulSoup

def Parser_URL_bbc (url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')       
    quotes = soup.find_all('div', class_='promo-text')
    content = ''
    with open('.\\output\\all\\bbc.txt', "w", encoding="utf-8") as output_file:
        print('----------------------- Стрічка новин', url, '---------------------------------')
        for quote in quotes:
            content = ''
            name = quote.find('a')
            timing = quote.find('time')
            if timing != None:
                content += timing.contents[0] + ' '
            span_text = name.find('span')
            if span_text != None:
                span_text = span_text.contents[1]
                span_text = span_text.split()
                span_text = ' '.join(span_text)
                content += span_text + '\n'
            else:
                name = name.contents[0]
                name = name.split()
                name = ' '.join(name)
                content += name + '\n'
            print(content)
            output_file.write(content)  
        print('------------------------------------------------------------------------------')

    return

def Parser_URL_suspilne (url):
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')        
    quotes = soup.find_all('div', class_= ['c-article-card__content', 'c-article-card-bgimage__content'])
    with open('./output/all/suspilne.txt', "w", encoding="utf-8") as output_file:
        text = f'----------------------- Стрічка новин {url} ---------------------------------\n'
        for quote in quotes:
            content = ''
            name = quote.find('span', class_ = ['c-article-card__headline-inner', 'c-article-card-bgimage__headline-inner']).text
            name = name.split()
            name = ' '.join(name)
            timing = quote.find('time').contents[0]
            content = f'{timing} {name}\n'
            text += content
            output_file.write(content) 
        text += '------------------------------------------------------------------------------'
        print(text)

    return

def Parser_URL_pravda (url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')        
    quotes = soup.find_all('div', class_= ['article_news_list', 'news_date'])
    dates = soup.find_all('div', class_= 'news_date')
    if dates != []:
        date = dates[0].text
        print(date)
        date = date.split()
        date[0] = str(int(date[0]) + 1)
        date = ' '.join(date)
        print(date)
    else:
        date = datetime.datetime.today()
    with open('.\\output\\all\\pravda.txt', "w", encoding="utf-8") as output_file:
        print('----------------------- Стрічка новин', url, '---------------------------------')
        for quote in quotes:
            if quote in dates:
                date = ' '.join(quote.text.split())
                continue
            content = ''
            timing = quote.find('div', class_ = 'article_time')
            if timing != None:
                content += f'{date}, {timing.text} '
            name = quote.find('div', class_ = 'article_title')
            if name != None:
                name = name.text
                name = name.split()
                name = ' '.join(name)
                name += '\n'
                content += name
            output_file.write(content) 
        print('------------------------------------------------------------------------------')

    return