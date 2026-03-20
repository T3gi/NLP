from bs4 import BeautifulSoup
import requests
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

def Parser_URL_bbc (url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')       
    print(soup)
    quotes = soup.find_all('div', class_='promo-text')
    content = ''
    with open('.\\output\\bbc.txt', "w", encoding="utf-8") as output_file:
        print('----------------------- Стрічка новин', url, '---------------------------------')
        for quote in quotes:
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

def Parser_URL_suspilne_page(url, index):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    url_request = url + str(index)
    response = requests.get(url_request, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')        
    quotes = soup.find_all('div', class_= ['c-article-card__content', 'c-article-card-bgimage__content'])
    with open('.\\output\\suspilne.txt', "a", encoding="utf-8") as output_file:
        text = f'----------------------- Стрічка новин {url_request} ---------------------------------\n'
        for quote in quotes:
            content = ''
            name = quote.find('span', class_ = ['c-article-card__headline-inner', 'c-article-card-bgimage__headline-inner']).text
            name = name.split()
            name = ' '.join(name)
            timing = quote.find('time').contents[0]
            month = str(timing).split(' ')[1]
            day = int(str(timing).split(' ')[0])
            if month != 'березня,' or day >= 8:
                return timing
            content = f'{timing} {name}\n'
            text += content
            output_file.write(content) 
        text += '------------------------------------------------------------------------------'
        print(text)

    return timing

def Parser_URL_suspilne (url):
    url = url + f"/latest/?page="
    with open('.\\output\\suspilne.txt', "w", encoding="utf-8") as output_file:
        output_file.write('') 
    
    index = 100

    timing = Parser_URL_suspilne_page(url, index)

    while int(str(timing).split(' ')[0]) > 8:
        index += 1
        timing = Parser_URL_suspilne_page(url, index)
    else:
        index -= 1

    while str(timing).split(' ')[1] == 'березня,':
        index += 1
        timing = Parser_URL_suspilne_page(url, index)

    return

def Parser_URL_pravda (url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    url += '/date_'
    with open('.\\output\\pravda.txt', "w", encoding="utf-8") as output_file:
        output_file.write('') 

    for i in range(7, 0, -1):
        url_request = url + f'0{i}032026'
        response = requests.get(url_request, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')        
        quotes = soup.find_all('div', class_= 'article_news_list')
        with open('.\\output\\pravda.txt', "a", encoding="utf-8") as output_file:
            print('----------------------- Стрічка новин', url_request, '---------------------------------')
            for quote in quotes:
                content = ''
                timing = quote.find('div', class_ = 'article_time')
                if timing != None:
                    content += f'{i} березня, {timing.text} '
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

def text_wordcloud(text):

    text_raw = " ".join(text)

    wordcloud = WordCloud().generate(text_raw)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()

    return

def top_5(text_list):
    result_dict = dict()
    text = ' '.join(text_list)
    text = text.replace("\n", " ")
    text = text.replace(",", "").replace(".", "").replace("?", "").replace("!", "").replace('\"', '')
    text = text.replace(':', '').replace(';', '').replace('“', '').replace('”', '')
    text = text.lower()
    words = text.split()
    words.sort()
    words_dict = dict()
    for word in words:
        if word in words_dict:
            words_dict[word] = words_dict[word] + 1
        else:
            words_dict[word] = 1

    sorted_words = sorted(words_dict.items(), key = lambda item: (item[1], item[0]), reverse = True)

    sorted_words = dict(sorted_words)

    sorted_words = filtering_stop_words(sorted_words)

    index = 0

    for i in range(5):
        word = list(sorted_words.keys())[index]
        while str(word).isalpha() == False:
            index += 1
            word = list(sorted_words.keys())[index]
        result_dict[word] =sorted_words[word]
        index += 1

    return result_dict

def filtering_stop_words(word):
    words_in_quote = word
    
    url = 'https://raw.githubusercontent.com/olegdubetcky/Ukrainian-Stopwords/main/ukrainian'
    r = requests.get(url)
    stop_words = str(r.text).split()
    stop_words = stop_words[:len(stop_words) - 1]
    stop_words.append('та')

    stop_words = set(stop_words)

    filtered_dict = {}
    for word in words_in_quote:
        if word.casefold() not in stop_words:
            filtered_dict[word] = words_in_quote[word]

    return filtered_dict

def time_distribution(filename):
    with open(filename, encoding="utf-8") as file:
        text = file.readlines()

    result_dict = dict()

    for line in text:
        line = line.split(' ')
        date = ' '.join(line[:2])
        date = date[:-1]
        time = ''.join(line[2:3])
        time = time.split(':')
        if date not in result_dict:
            result_dict[date] = {'ранок':[],
                                'обід':[],
                                'вечір':[],}
        if int(time[0]) < 8 or int(time[0]) == 8 and int(time[1]) == 0:
            index = 'ранок'
        elif int(time[0]) > 8 and int(time[0]) < 16 or int(time[0]) == 16 and int(time[1]) == 0:
            index = 'обід'
        else:
            index = 'вечір'
        result_dict[date][index].append(' '.join(line[3:])[:-1])

    return result_dict

def advanced_analysis(filename):
    news_by_time = time_distribution(f'.\\output\\{filename}.txt')
    news_by_time = dict(sorted(news_by_time.items()))
    top_by_period = dict()

    rows = []

    for day in news_by_time:
        top_by_period[day] = {'ранок':[],
                        'обід':[],
                        'вечір':[],}
        for period in news_by_time[day]:
            top_by_period[day][period] = top_5(news_by_time[day][period])

    for day, periods in top_by_period.items():
        for period, terms in periods.items():
            time_label = f'{period}'
            sum_freq = sum(terms.values())

            for term, freq in terms.items():
                rows.append({
                    'День': day,
                    'Час': time_label,
                    'Топ 5': term,
                    'Частота': freq,
                    'Сума частот': sum_freq,
                    'Коментар': ''
                })

    print(top_by_period)

    df = pd.DataFrame(rows)
    df.to_csv(f'.\\output\\{filename}.csv')

    print(df)

    data = df['Топ 5'].value_counts()[:3]
    data = list(data.keys())

    filtered_df = df[df['Топ 5'].isin(data)]
    result_df = filtered_df.pivot_table(index = 'День', columns = 'Топ 5', values = 'Частота', aggfunc = 'sum', fill_value=0)
    
    print(result_df)

    text_wordcloud(df['Топ 5'])
    sns.lineplot(df, x = 'День', y = 'Сума частот', hue = 'Час')
    plt.show()
    result_df.plot.line()
    plt.show()
    

if __name__ == '__main__':

    directory_name = 'output'

    if not os.path.exists(directory_name):
        os.mkdir(directory_name)

    print('Оберіть напрям досліджень:')
    print('1 - Парсинг сайту новин http://bbc.com/ukrainian')
    print('2 - Парсинг сайту новин https://suspilne.media')
    print('3 - Парсинг сайту новин https://www.pravda.com.ua/news')
    print('4 - Парсинг сайтів новин https://suspilne.media та https://www.pravda.com.ua/news')
    mode = int(input('mode:'))

    if (mode == 1):
        print('Обрано інформаційне джерело: http://bbc.com/ukrainian')
        url = 'http://bbc.com/ukrainian'
        Parser_URL_bbc(url)

    if (mode == 2):
        print('Обрано інформаційне джерело: https://suspilne.media')
        url = 'https://suspilne.media'
        Parser_URL_suspilne(url)

    if (mode == 3):
        print('Обрано інформаційне джерело: https://www.pravda.com.ua/news')
        url = 'https://www.pravda.com.ua/news'
        Parser_URL_pravda(url)

    if (mode == 4):
        print('Обрано інформаційні джерела: https://suspilne.media та https://www.pravda.com.ua/news')
        url1 = 'https://suspilne.media'
        url2 = 'https://www.pravda.com.ua/news'
        Parser_URL_suspilne(url1)
        Parser_URL_pravda(url2)

        advanced_analysis('suspilne')
        advanced_analysis('pravda')
        with open('.\\output\\suspilne.txt', encoding="utf-8") as file1:
            with open('.\\output\\pravda.txt', encoding="utf-8") as file2:
                text1 = file1.read()
                text2 = file2.read()
                text = text1 + text2
                with open('.\\output\\combined.txt', 'w', encoding="utf-8") as file_combined:
                    file_combined.write(text)

        advanced_analysis('combined')