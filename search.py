import spacy
import nltk
from tqdm import tqdm
from curses.ascii import isalpha, isupper
from re import T
from turtle import right
import pandas as pd
import json
from string import punctuation
punctuation = set(punctuation)
punctuation.add('\n')
punctuation.add(' ')
nlp = spacy.load("en_core_web_sm")


with open("indexes.json", 'r', encoding="utf-8") as f,\
        open("texts.json", 'r', encoding="utf-8") as t:
    indexes = json.load(f)
    texts = json.load(t)


# индексация

def index_df(df: pd.DataFrame):
    indexes = {}
    texts = {}
    count = 0

    for review in tqdm(df["review"]):
        texts[count] = review
        review = nlp(review)
        for word in review:
            if word.lemma_ is not None and word.lemma_ not in punctuation:
                if word.lemma_ not in indexes:
                    indexes[word.lemma_] = [count]
                elif word.lemma_ in indexes and count not in indexes[word.lemma_]:
                    indexes[word.lemma_].append(count)
        count += 1

    with open("indexes.json", 'w', encoding="utf-8") as f,\
            open("texts.json", 'w', encoding="utf-8") as t:
        f.write(json.dumps(indexes, ensure_ascii=False, indent=2))
        t.write(json.dumps(texts, ensure_ascii=False, indent=2))


class Searcher:
    def __init__(self, index=indexes, texts=texts) -> None:
        self.index = index
        self.texts = texts
    
    def get_texts(self, word: str):
        word = word.strip('"').lower()
        doc = nlp(word)
        for i in doc:
            lemma = i.lemma_
        if lemma in self.index:
            text_ids = [x for x in self.index[lemma]]
            texts_raw = [self.texts[str(x)] for x in self.index[lemma]]
        
        return text_ids, texts_raw

    def search(query: str):
        '''
        Делим запрос на несколько подзапросов, каждый со своими правилами(?).
        Находим все предложения удовлетворяющие первый запрос. Они становятся пулом из которого мы будем выбирать предложения по другим запросам.
        Плюс в функцию нужно добавить аргумент required_prev_word, который показывает после чего мы ищем нужное слово.
        '''
        query = query.split()
        if query[0].isalpha() or '"' in query[0] or '+' in query[0]:    # проверяем есть ли слово(?) в первой части запроса, чтобы ограничить число текстов
            pass

    def check(word: str, query: str):   # функция проверяющая слово на соответствие запросу
        word = word.lower()
        if '+' in query:            # для запросов типа 'знать+NOUN'
            w, p = query.split('+')
            w = w.lower()
            pos = nlp(word)[0].pos_
            lemma = nlp(word)[0].lemma_
            if lemma == w and pos == p:
                return True
            else:
                return False

        elif '"' in query:          # для точных запросов
            w = query.strip('"').lower()
            if word == w:
                return True
            else:
                return False

        elif query.isupper():       # для запросов типа VERB
            pos = nlp(word)[0].pos_
            if pos == query:
                return True
            else:
                return False

        else:                       # для поиска со всеми словоформами
            lemma = nlp(word)[0].lemma_
            w = nlp(query)[0].lemma_
            if lemma == w:
                return True
            else:
                return False

    # поиск со всеми словоформами

    def lemma_search(self, prev_word_req=None, word=None):
        word = word.lower()
        doc = nlp(word)
        out = []
        for i in doc:
            lemma = i.lemma_
        if lemma in self.index:
            text_ids = [x for x in self.index[lemma]]
            texts_raw = [self.texts[str(x)] for x in self.index[lemma]]
            for text in texts_raw:
                sentences = nltk.sent_tokenize(text)
                for s in sentences:
                    s_lemm = nlp(s)
                    left, center, right = '', '', ''  # placeholders
                    found = False
                    for token in s_lemm:
                        if token.lemma_ != lemma and not found:
                            left += token.text + ' '
                        elif token.lemma_ == lemma and not found:
                            center = token.text
                            found = True
                        else:
                            right += token.text + ' '

                    if center == '':
                        continue

                    out.append((left, center, right))

            return out

        return []

    # поиск по точной форме

    def strict_search(self, prev_word, word):
        word = word.strip('"').lower()
        doc = nlp(word)
        out = []
        for i in doc:
            lemma = i.lemma_
        if lemma in self.index:
            texts_raw = [self.texts[str(x)] for x in self.index[lemma]]
            for text in texts_raw:
                sentences = nltk.sent_tokenize(text)
                for s in sentences:
                    s_lemm = nlp(s)
                    left, center, right = '', '', ''  # placeholders
                    found = False
                    for token in s_lemm:
                        if token.text != word and not found:
                            left += token.text + ' '
                        elif token.text == word and not found:
                            center = token.text
                            found = True
                        else:
                            right += token.text + ' '

                    if center == '':
                        continue

                    out.append((left, center, right))

            return out

        return []


# запуск кода для теста
if __name__ == "__main__":
    data = pd.read_excel("xlsx_corpus.xlsx")
    # index_df(data)

    with open("indexes.json", 'r', encoding="utf-8") as f,\
            open("texts.json", 'r', encoding="utf-8") as t:
        indexes = json.load(f)
        texts = json.load(t)

    # print(strict_search('"bad"', indexes, texts))
    print(texts["373"])
    print(data.iloc[[373]])
