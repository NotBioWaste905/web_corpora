"""
Требования
pip install pandas spacy
python -m spacy download en_core_web_sm
"""

import pandas
import spacy
from spacy.lang.en import English
#создается датафрейм corpus (копия того, что ангелина сделала)
corpus = pandas.read_csv('corpus.csv')

# добавление пустого столбца в датафрейм, название столбца "meta"
corpus['meta'] = ''

# Компонент Sentencizer - это компонент, который разделяет предложения по знакам препинания типа ., ! или ?
sentencizer = English()
sentencizer.add_pipe("sentencizer")

# подключение POS тэггер
tagger = spacy.load("en_core_web_sm")


for index in range(0, len(corpus)):
    row = corpus.iloc[index]
    text = row['review']
    sentences = [sent.text for sent in sentencizer(text).sents]
    meta_text = []
    for sentence in sentences:
        doc = tagger(sentence)
        # в массиве meta_sentence будет массив из pos, normal original form для поиска
        meta_sentence = []
        for token in doc:
            # for each word in sentence meta information is pos, normal form, original form
            # для поиска по части речи
            pos = token.pos_
            # для поиска по словоформе
            normal_form = token.lemma_
            original_form = token.text
            meta = (pos, normal_form, original_form)
            meta_sentence.append(meta)
        meta_text.append(meta_sentence)
    corpus['meta'][index] = meta_text

# новая таблица meta с одним столбцом
meta = pandas.DataFrame(corpus['meta'])
print(meta.head())