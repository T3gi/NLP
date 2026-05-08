import os
from web_scraper import *
from gtts import gTTS
import os
import speech_recognition as sr

recognizer = sr.Recognizer()

def capture_voice_input():
    with sr.Microphone() as source:
        print("Говоріть...")
        audio = recognizer.listen(source)
    return audio

def convert_voice_to_text(audio):
    try:
        text = recognizer.recognize_google(audio, language="uk-UA")
        print("Ви сказали: " + text)
    except sr.UnknownValueError:
        text = ""
        print("Вибачте, я Вас не розумію.")
    except sr.RequestError as e:
        text = ""
        print("Error; {0}".format(e))
    return text

def clean_file(filename):
    with open(f'{filename}.txt', "w", encoding="utf-8") as output_file:
        output_file.write('')

def save_to_file(data, filename):
    with open(f'{filename}.txt', "a", encoding="utf-8") as output_file:
        output_file.write(data)

def text_speech_gtts(mytext, path, lang):

    '''
    Озвучування тексту із gtts
    '''

    language = lang
    myobj = gTTS(text=mytext, lang=language, slow=False)
    myobj.save(path)
    os.system('start '+path)

    return

if __name__ == '__main__':

    directory_name = 'output'

    if not os.path.exists(directory_name):
        os.mkdir(directory_name)

    directory_name += '/all'

    if not os.path.exists(directory_name):
        os.mkdir(directory_name)

    print('Оберіть напрям досліджень:')
    print('1 - Парсинг сайту новин http://bbc.com/ukrainian')
    print('2 - Парсинг сайту новин https://suspilne.media')
    print('3 - Парсинг сайту новин https://www.pravda.com.ua/news')
    print('4 - Парсинг трьох сайтів + TTS')
    print('5 - Зчитування з файлів + TTS')
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

    if (mode <= 3):
        data = ''
        with open(f'{input_directory}', "r", encoding="utf-8") as input_file:
            data = input_file.readlines()
    else:
        input_data = {
            'bbc': '',
            'suspilne': '',
            'pravda': ''
        }
        for input_file in input_directory:
            with open(f'{input_file}', 'r', encoding = 'utf-8') as file_to_analise:
                index = input_file[11:-4]
                input_data[index] = file_to_analise.readlines()

        first, second, third = list(input_data.keys())

        data = list()
        data.extend(input_data[first])
        data.extend(input_data[second])
        data.extend(input_data[third])
    
    print(f'Кількість рядків стрічки новин: {len(data)}')
    
    data = ' '.join(data)

    print(data)

    languages = ['українська', 'англійська']
    lang_codes = {
        'українська': 'uk',
        'англійська': 'en'
    }

    print('Оберіть мову для TTS')

    language = ''
    while language not in languages:
        audio = capture_voice_input()
        language = convert_voice_to_text(audio)

    print('Запускається TTS gtts')
    path = directory_name + '/text_speech_gtts.mp3'
    text_speech_gtts(data, path, lang_codes[language])

