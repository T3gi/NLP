import os
import re
from web_scraper import *
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import spacy
from nltk.stem import SnowballStemmer

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

def prepare_labeled_framework(data):
    texts = []
    labels = []
    
    categories = {
        "Економіка": ['ощадбанк', 'долар', 'мвф', 'бюджет', 'банк', 'нафта', 'пальне', 'ціни', 'економік', 'експорт', 'імпорт', 'митниц', 'банк'],
        "Політика": ['трамп', 'зеленський', 'путін', 'орбан', 'мзс', 'сша', 'уряд', 'закон', 'макрон', 'вибори', 'парламент', 'посол'],
        "Війна": ['зсу', 'дрон', 'обстріл', 'фронт', 'ппо', 'ракета', 'окупант', 'шахед', 'атака', 'військовий', 'генштаб', 'удар', 'перемиря'],
        "Соціальна сфера": ['лікар', 'пенсі', 'школ', 'діти', 'жінки', 'поліція', 'дтп', 'суд', 'освіт', 'студент', 'лікарн', 'війна']
    }
    
    for line in data:
            
        assigned_label = "Інші новини"
        for cat, keywords in categories.items():
            if any(kw in line for kw in keywords):
                assigned_label = cat
                break
        
        texts.append(line)
        labels.append(assigned_label)
            
    return pd.DataFrame({'text': texts, 'category': labels})

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
        data = file_to_analise.readlines()

    nlp = spacy.load("uk_core_news_sm")
    stemmer = SnowballStemmer(language='english')

    sentences = data
    sentences = [text_filter(sentence) for sentence in sentences]
    sentences = [[token for token in sentence] for sentence in sentences]
    sentences = [[token for token in sentence if not token.is_stop] for sentence in sentences]
    sentences = [[token.lemma_ for token in sentence] for sentence in sentences]
    sentences = [' '.join([stemmer.stem(token) for token in sentence]) for sentence in sentences]

    df = prepare_labeled_framework(sentences)
        
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df['text'])
    y = df['category']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    
    model = SVC(kernel='linear')
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    text = []
    for i in range(len(y_pred)):
        text.append(f'{df["text"][i]}: {y_pred[i]}')

    save_to_file('\n'.join(text), f'{directory_name}/{input_file}_clasterized')

    accuracy = accuracy_score(y_test, y_pred)
    print(f"Кількість новин у каркасі: {len(df)}")
    print(f"Метрика ефективності (Accuracy) на тестовій вибірці: {accuracy*100:.2f}%")
    
    if accuracy < 0.60:
        print("Попередження: Ефективність кластеризації/класифікації нижча за прийнятні 60%!")
    else:
        print("Ефективність є прийнятною (більше 60%).")

