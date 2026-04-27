import os
import spacy
import re
from web_scraper import *
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import string
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def text_filter(text, lang):
    text = text.replace("\n", "").replace('\\n', '').replace('%', '').replace('–', '')
    text = text.replace(",", "").replace(".", "").replace("?", "").replace("!", "").replace('\"', '')
    text = text.replace(':', '').replace(';', '').replace('“', '').replace('”', '').replace('\'', '')
    text = text.replace('’', '').replace('$', '').replace('-', '').replace('[', '').replace(']', '')
    text = text.replace('(', '').replace(')', '')
    text = re.sub(r'[0-9]+', '', text)
    text = text.split()
    text = ' '.join(text)
    text = text.lower()

    if (lang == 'ua'):
        return nlp(text)
    elif (lang == 'en'):
        return nlp_en(text)

def One_Hot_Encoding(documents):
    words = [word.lower().strip(string.punctuation)
             for doc in documents for word in doc.split()]
    vocabulary = sorted(set(words))

    encoder = OneHotEncoder(sparse_output=False)
    one_hot_vectors = encoder.fit_transform(np.array(vocabulary).reshape(-1, 1))

    word_to_onehot = {vocabulary[i]: one_hot_vectors[i]
                      for i in range(len(vocabulary))}

    for word, vector in word_to_onehot.items():
        print(f"Word: {word}, One-Hot Encoding: {vector}")

    return word_to_onehot

def Bag_of_Words(documents):
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(documents)

    print(X.toarray())
    print(vectorizer.get_feature_names_out())

    return X.toarray(), vectorizer.get_feature_names_out()

def TF_IDF(documents):
    tfidf_vectorizer = TfidfVectorizer()
    X_tfidf = tfidf_vectorizer.fit_transform(documents)

    print(X_tfidf.toarray())
    print(tfidf_vectorizer.get_feature_names_out())

    return X_tfidf.toarray(), tfidf_vectorizer.get_feature_names_out()

def Count_Vectorizer(documents):
    count_vectorizer = CountVectorizer()
    X_count = count_vectorizer.fit_transform(documents)

    print(X_count.toarray())
    print(count_vectorizer.get_feature_names_out())

    return X_count.toarray(), count_vectorizer.get_feature_names_out()

def compare_segments(text):
    half = len(text) // 2
    part1, part2 = text[:half], text[half:]
    phrase = text.split('.')[0]
    
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform([text, part1, part2, phrase])
    sim_matrix = cosine_similarity(matrix)
    
    return pd.DataFrame(sim_matrix, 
                        columns=['Full', 'Part 1', 'Part 2', 'Phrase'],
                        index=['Full', 'Part 1', 'Part 2', 'Phrase'])

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
    print('5 - Аналіз захардкоженого тексту')
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

    if (mode == 5):
        input_file = 'hardcode'
        directory_name += f'/{input_file}'
        if not os.path.exists(directory_name):
            os.mkdir(directory_name)
        text = {'ukrainian':'''
                Весняний ранок повільно розливається містом, фарбуючи небо в ніжні рожеві відтінки.
                Пташки вже розпочали свій гучний концерт, наповнюючи повітря першими бадьорими звуками природи.
                Кожна крапля роси на траві виблискує під променями сонця, нагадуючи про те, що кожен новий день - це можливість почати все з чистого аркуша.''',
                'english':'''
                The golden sun slowly dips below the horizon, painting the sky in shades of amber and violet. 
                As the world grows quiet, the gentle rustle of leaves whispers secrets of the coming night. 
                It is in these fleeting moments of stillness that we often find the clarity we’ve been seeking all day. 
                Every sunset is not just an end, but a quiet promise of a new beginning.'''}

    nlp = spacy.load("uk_core_news_sm")
    nlp_en = spacy.load("en_core_web_sm")

    if (mode < 5):
        with open(f'{input_directory}', 'r', encoding = 'utf-8') as file_to_analise:
            data = str(file_to_analise.readlines())
    else:
        data = text['ukrainian']
        data_en = text['english']

    sentences = sent_tokenize(data)
    sentences = [text_filter(sentence, 'ua') for sentence in sentences]
    sentences = [[token for token in sentence] for sentence in sentences]
    sentences = [' '.join([token.text for token in sentence if not token.is_stop]) for sentence in sentences]
    print(sentences)

    print("One_Hot")
    One_Hot_Encoding(sentences)
    print('Bag_Of_Words')
    Bag_of_Words(sentences)
    print('TF_IDF')
    TF_IDF(sentences)
    print('Count_Vectorizer')
    Count_Vectorizer(sentences)

    introduction_doc = text_filter(data, 'ua')

    token_word = [token.text for token in introduction_doc] 
    text = '\n'.join(token_word)
    save_to_file(text, f'{directory_name}/{input_file}_tokenized')

    token_word_is_stop = [token for token in introduction_doc if not token.is_stop]
    text = [token.text for token in token_word_is_stop]

    print(compare_segments(' '.join(text)))

    text = '\n'.join(text)
    save_to_file(text, f'{directory_name}/{input_file}_no_stop_words')

    token_lemma_list = []
    for token in token_word_is_stop:
        if str(token) != str(token.lemma_):
            token_lemma_list.append(str(token.lemma_))
    text = '\n'.join(token_lemma_list)
    save_to_file(text, f'{directory_name}/{input_file}_lematized')

    text = ''
    for token in token_word_is_stop:
        text += f"{token.text}: {token.pos_}" + '\n'
    save_to_file(text, f'{directory_name}/{input_file}_pos_tages')

    if mode == 5:
        sentences = sent_tokenize(data_en)
        sentences = [text_filter(sentence, 'en') for sentence in sentences]
        sentences = [[token for token in sentence] for sentence in sentences]
        sentences = [' '.join([token.text for token in sentence if not token.is_stop]) for sentence in sentences]
        print(sentences)

        print("One_Hot")
        One_Hot_Encoding(sentences)
        print('Bag_Of_Words')
        Bag_of_Words(sentences)
        print('TF_IDF')
        TF_IDF(sentences)
        print('Count_Vectorizer')
        Count_Vectorizer(sentences)

        introduction_doc_en = text_filter(data_en, 'en')
        token_word = [token.text for token in introduction_doc_en] 
        text = '\n'.join(token_word)
        save_to_file(text, f'{directory_name}/{input_file}_en_tokenized')

        token_word_is_stop = [token for token in introduction_doc_en if not token.is_stop]
        text = [token.text for token in token_word_is_stop]

        print(compare_segments(' '.join(text)))

        text = '\n'.join(text)
        save_to_file(text, f'{directory_name}/{input_file}_en_no_stop_words')

        token_lemma_list = []
        for token in token_word_is_stop:
            if str(token) != str(token.lemma_):
                token_lemma_list.append(str(token.lemma_))
        text = '\n'.join(token_lemma_list)
        save_to_file(text, f'{directory_name}/{input_file}_en_lematized')

        text = ''
        for token in token_word_is_stop:
            text += f"{token.text}: {token.pos_}" + '\n'
        save_to_file(text, f'{directory_name}/{input_file}_en_pos_tages')