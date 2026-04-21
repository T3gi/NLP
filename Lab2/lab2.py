from bs4 import BeautifulSoup
import requests
import os
import re
import nltk
import datetime
#nltk.download('punkt_tab')
#nltk.download('wordnet')
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.tokenize.simple import CharTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.stem import SnowballStemmer

def Parser_URL_bbc (url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')       
    quotes = soup.find_all('div', class_='promo-text')
    content = ''
    with open('.\\output\\bbc\\bbc.txt', "w", encoding="utf-8") as output_file:
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

def Parser_URL_suspilne (url):
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')        
    quotes = soup.find_all('div', class_= ['c-article-card__content', 'c-article-card-bgimage__content'])
    with open('./output/suspilne/suspilne.txt', "w", encoding="utf-8") as output_file:
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
    with open('.\\output\\pravda\\pravda.txt', "w", encoding="utf-8") as output_file:
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

def filter(text, filename, directory):
    text = text.replace("\n", "").replace('\\n', '').replace('%', '').replace('–', '')
    text = text.replace(",", "").replace(".", "").replace("?", "").replace("!", "").replace('\"', '')
    text = text.replace(':', '').replace(';', '').replace('“', '').replace('”', '').replace('\'', '')
    text = text.replace('’', '').replace('$', '')
    text = re.sub(r'[0-9]+', '', text)

    save_to_file('\n'.join(text.split()), f'{directory}/{filename}_filtered')

    text = text.lower()

    save_to_file('\n'.join(text.split()), f'{directory}/{filename}_normalized')

    return str(text)

def filtering_stop_words(words_in_quote, filename, directory):
    url = 'https://raw.githubusercontent.com/olegdubetcky/Ukrainian-Stopwords/main/ukrainian'
    r = requests.get(url)
    stop_words = str(r.text).split()
    stop_words = stop_words[:len(stop_words) - 1]
    stop_words.append('та')

    stop_words = set(stop_words)

    filtered_list = []
    for word in words_in_quote:
        if word.casefold() not in stop_words:
            filtered_list.append(word)

    text = '\n'.join(filtered_list)

    save_to_file(text, f'{directory}/{filename}_deleted_words')

    return filtered_list

def tokenizing(example_string, filename, directory):
    sentence = sent_tokenize(example_string)  
    word = word_tokenize(example_string)  
    character = CharTokenizer().tokenize(example_string)
    save_to_file('\n'.join(sentence), f'{directory}/{filename}_tokenized_sentences')
    save_to_file('\n'.join(word), f'{directory}/{filename}_tokenized_words')
    save_to_file('\n'.join(character), f'{directory}/{filename}_tokenized_characters')
    return word

def lemmatization(tokens, filename, directory):
    lemma = WordNetLemmatizer()
    lemmatized_tokens = [lemma.lemmatize(token) for token in tokens]

    text = '\n'.join(lemmatized_tokens)

    save_to_file(text, f'{directory}/{filename}_lemmatized')

    return lemmatized_tokens

def stemming(tokens, filename, directory):
    stemmer = SnowballStemmer(language='english')
    steming_tokens = [stemmer.stem(word) for word in tokens]

    text = '\n'.join(steming_tokens)

    save_to_file(text, f'{directory}/{filename}_stemmed')

    return steming_tokens

def top_10(tokens, filename, directory):
    result_dict = dict()
    words_dict = dict()
    for word in tokens:
        if word in words_dict:
            words_dict[word] = words_dict[word] + 1
        else:
            words_dict[word] = 1

    sorted_words = sorted(words_dict.items(), key = lambda item: (item[1], item[0]), reverse = True)

    sorted_words = dict(sorted_words)

    index = 0

    for i in range(10):
        word = list(sorted_words.keys())[index]
        while str(word).isalpha() == False:
            index += 1
            word = list(sorted_words.keys())[index]
        result_dict[word] =sorted_words[word]
        index += 1

    save_to_file(str(result_dict), f'{directory}/{filename}_top_10')

    return result_dict


def save_to_file(data, filename):
    with open(f'{filename}.txt', "w", encoding="utf-8") as output_file:
        output_file.write(data)

if __name__ == '__main__':

    directory_name = 'output'

    if not os.path.exists(directory_name):
        os.mkdir(directory_name)

    print('Оберіть напрям досліджень:')
    print('1 - Парсинг сайту новин http://bbc.com/ukrainian')
    print('2 - Парсинг сайту новин https://suspilne.media')
    print('3 - Парсинг сайту новин https://www.pravda.com.ua/news')
    print('4 - Зчитування інформації з файлу')
    mode = int(input('mode:'))

    if (mode == 1):
        print('Обрано інформаційне джерело: http://bbc.com/ukrainian')
        url = 'http://bbc.com/ukrainian'
        directory_name += '/bbc'
        if not os.path.exists(directory_name):
            os.mkdir(directory_name)
        Parser_URL_bbc(url)
        input_file = 'bbc.txt'
        input_directory = directory_name + '/' + input_file

    if (mode == 2):
        print('Обрано інформаційне джерело: https://suspilne.media/latest')
        url = 'https://suspilne.media/latest'
        directory_name += '/suspilne'
        if not os.path.exists(directory_name):
            os.mkdir(directory_name)
        Parser_URL_suspilne(url)
        input_file = 'suspilne.txt'
        input_directory = directory_name + '/' + input_file

    if (mode == 3):
        print('Обрано інформаційне джерело: https://www.pravda.com.ua/news')
        url = 'https://www.pravda.com.ua/news'
        directory_name += '/pravda'
        if not os.path.exists(directory_name):
            os.mkdir(directory_name)
        Parser_URL_pravda(url)
        input_file = 'pravda.txt'
        input_directory = directory_name + '/' + input_file

    if (mode == 4):
        input_file = input('Введіть назву файлу: ')
        directory_name += f'/{input_file}'
        if not os.path.exists(directory_name):
            os.mkdir(directory_name)
        input_directory = input_file

    with open(f'{input_directory}', 'r', encoding = 'utf-8') as file_to_analise:
        data = str(file_to_analise.readlines())

    data = filter(data, input_file, directory_name)
    data = tokenizing(data, input_file, directory_name)
    data = filtering_stop_words(data, input_file, directory_name)
    data = lemmatization(data, input_file, directory_name)
    data = stemming(data, input_file, directory_name)
    data = top_10(data, input_file, directory_name)


