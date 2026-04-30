import os
import re
from web_scraper import *
import spacy
import warnings
warnings.filterwarnings(action='ignore')

def text_filter(text):
    text = text.replace("\n", "").replace('\\n', '').replace('%', '').replace('–', '')
    text = text.replace(",", "").replace(".", "").replace("?", "").replace("!", "").replace('\"', '')
    text = text.replace(':', '').replace(';', '').replace('“', '').replace('”', '').replace('\'', '')
    text = text.replace('’', '').replace('$', '').replace('-', '').replace('[', '').replace(']', '')
    text = text.replace('(', '').replace(')', '')
    text = re.sub(r'[0-9]+', '', text)
    text = text.split()
    text = ' '.join(text)
    text = text.lower()

    return nlp(text)

def clean_file(filename):
    with open(f'{filename}.txt', "w", encoding="utf-8") as output_file:
        output_file.write('')

def save_to_file(data, filename):
    with open(f'{filename}.txt', "a", encoding="utf-8") as output_file:
        output_file.write(data)

if __name__ == '__main__':

    directory_name = 'output/all'

    if not os.path.exists(directory_name):
        os.mkdir(directory_name)

    print('Оберіть напрям досліджень:')
    print('1 - Парсинг сайту новин http://bbc.com/ukrainian')
    print('2 - Парсинг сайту новин https://suspilne.media')
    print('3 - Парсинг сайту новин https://www.pravda.com.ua/news')
    print('4 - Парсинг трьох сайтів + порівняльний аналіз')
    print('5 - Порівняльний аналіз')
    mode = int(input('mode:'))

    if (mode == 1):
        print('Обрано інформаційне джерело: http://bbc.com/ukrainian')
        url = 'http://bbc.com/ukrainian'
        Parser_URL_bbc(url)
        input_file = 'bbc.txt'
        input_directory = directory_name + '/' + input_file

    if (mode == 2):
        print('Обрано інформаційне джерело: https://suspilne.media/latest')
        url = 'https://suspilne.media/latest'
        Parser_URL_suspilne(url)
        input_file = 'suspilne.txt'
        input_directory = directory_name + '/' + input_file

    if (mode == 3):
        print('Обрано інформаційне джерело: https://www.pravda.com.ua/news')
        url = 'https://www.pravda.com.ua/news'
        Parser_URL_pravda(url)
        input_file = 'pravda.txt'
        input_directory = directory_name + '/' + input_file

    if (mode == 4):
        url_bbc = 'http://bbc.com/ukrainian'
        url_suspilne = 'https://suspilne.media/latest'
        url_pravda = 'https://www.pravda.com.ua/news'
        Parser_URL_bbc(url_bbc)
        Parser_URL_suspilne(url_suspilne)
        Parser_URL_pravda(url_pravda)
        input_file = ['bbc.txt', 'suspilne.txt', 'pravda.txt']
        input_directory = [directory_name + '/' + inp_file for inp_file in input_file]

    if (mode == 5):
        input_file = ['bbc.txt', 'suspilne.txt', 'pravda.txt']
        input_directory = [directory_name + '/' + inp_file for inp_file in input_file]

    nlp = spacy.load("uk_core_news_sm")

    if (type(input_directory) == type(list())):
        data = {
            'bbc': '',
            'suspilne': '',
            'pravda': ''
        }
        sentences = {
            'bbc': '',
            'suspilne': '',
            'pravda': ''
        }
        for input_file in input_directory:
            with open(f'{input_file}', 'r', encoding = 'utf-8') as file_to_analise:
                index = input_file[11:-4]
                data[index] = file_to_analise.readlines()

        for site in data:
            sentences[site] = [text_filter(sentence) for sentence in data[site]]
            sentences[site] = [[token for token in sentence] for sentence in sentences[site]]
            sentences[site] = [[token for token in sentence if not token.is_stop] for sentence in sentences[site]]
            sentences[site] = [' '.join([token.lemma_ for token in sentence]) for sentence in sentences[site]]


        first, second, third = list(data.keys())

        sentences1 = nlp(' '. join(sentences[first]))
        sentences2 = nlp(' '. join(sentences[second]))
        sentences3 = nlp(' '. join(sentences[third]))

        bbc_to_suspilne = sentences1.similarity(sentences2)
        bbc_to_pravda = sentences1.similarity(sentences3)
        suspilne_to_pravda = sentences2.similarity(sentences3)

        clean_file(f'{directory_name}/bbc_to_suspilne.txt')
        clean_file(f'{directory_name}/bbc_to_pravda.txt')
        clean_file(f'{directory_name}/suspilne_to_pravda.txt')
        save_to_file(f'Global bbc to suspilne similarity: {bbc_to_suspilne}\n', f'{directory_name}/bbc_to_suspilne.txt')
        save_to_file(f'Global bbc to pravda similarity: {bbc_to_pravda}\n', f'{directory_name}/bbc_to_pravda.txt')
        save_to_file(f'Global suspilne to pravda similarity: {suspilne_to_pravda}\n', f'{directory_name}/suspilne_to_pravda.txt')

        for site in sentences:
            sentences[site] = [nlp(sentence) for sentence in sentences[site]]

        text1 = set()
        text2 = set()
        text3 = set()

        for sentence1 in sentences[first]:
            for sentence2 in sentences[second]:
                bbc_to_suspilne = sentence1.similarity(sentence2)
                text1.add(f'{str(sentence1)}   ---   {str(sentence2)}   ---   similarity = {bbc_to_suspilne}\n')
                for sentence3 in sentences[third]:
                    bbc_to_pravda = sentence1.similarity(sentence3)
                    suspilne_to_pravda = sentence2.similarity(sentence3)
                    text2.add(f'{str(sentence1)}   ---   {str(sentence3)}   ---   similarity = {bbc_to_pravda}\n')
                    text3.add(f'{str(sentence2)}   ---   {str(sentence3)}   ---   similarity = {suspilne_to_pravda}\n') 
                    
        save_to_file('\n'.join(text1), f'{directory_name}/bbc_to_suspilne.txt')
        save_to_file('\n'.join(text2), f'{directory_name}/bbc_to_pravda.txt')
        save_to_file('\n'.join(text3), f'{directory_name}/suspilne_to_pravda.txt')


    