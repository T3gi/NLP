import os
import re
from web_scraper import *
import spacy
import warnings
import tensorflow
import numpy as np
warnings.filterwarnings(action='ignore')

Tokenizer = tensorflow.keras.preprocessing.text.Tokenizer
pad_sequences = tensorflow.keras.preprocessing.sequence.pad_sequences

tensorflow.keras
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

    if (mode > 3):
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

        training_data = list()
        training_data.extend(sentences[first])
        training_data.extend(sentences[second])
        training_data.extend(sentences[third])

        print('\n'.join(training_data))

        labels_list = [0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 
                       0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 
                       0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1]
        labels = np.array(labels_list)

        tokenizer = Tokenizer(num_words=100, oov_token='<OOV>')
        tokenizer.fit_on_texts(training_data)
        word_index = tokenizer.word_index
        sequences = tokenizer.texts_to_sequences(training_data)

        sequences = pad_sequences(sequences, maxlen=10, padding='post', truncating='post')

        model = tensorflow.keras.Sequential([
            tensorflow.keras.layers.Embedding(input_dim=len(word_index) + 1, output_dim=16, input_length=10),
            tensorflow.keras.layers.LSTM(64),  # LSTM layer
            tensorflow.keras.layers.Dense(16, activation='relu'),
            tensorflow.keras.layers.Dense(1, activation='sigmoid')
        ])


        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

        model.fit(sequences, labels, epochs=100)

        with open(directory_name + '/combined.txt', 'r', encoding = 'utf-8') as file_to_analise:
            test_texts = file_to_analise.readlines()

        test_texts = [text_filter(sentence) for sentence in test_texts]
        test_texts = [[token for token in sentence] for sentence in test_texts]
        test_texts = [[token for token in sentence if not token.is_stop] for sentence in test_texts]
        test_texts = [' '.join([token.lemma_ for token in sentence]) for sentence in test_texts]

        test_sequences = tokenizer.texts_to_sequences(test_texts)
        test_sequences = pad_sequences(test_sequences, maxlen=10, padding='post', truncating='post')
        test_predictions = model.predict(test_sequences)

        text = []
        for i in range(len(test_predictions)):
            text.append(f'{test_texts[i]}   :   {float(test_predictions[i]):.3f}')

        clean_file(f'{directory_name}/combined_tonality')
        save_to_file('\n'.join(text), f'{directory_name}/combined_tonality')
