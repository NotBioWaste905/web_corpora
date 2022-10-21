"""
Требования
pip install pandas spacy
python -m spacy download en_core_web_sm
"""

import pandas
import spacy
from spacy.lang.en import English

corpus = pandas.read_csv('corpus.csv')

# добавление пустого столбца в датафрейм, название столбца "meta"
corpus['meta'] = ''

# The Sentencizer component is a pipeline component that splits sentences on punctuation like ., ! or ?.
sentencizer = English()
sentencizer.add_pipe("sentencizer")

# POS таггер
tagger = spacy.load("en_core_web_sm")

for index in range(10, len(corpus)):
    row = corpus.iloc[index]
    text = row['reviews'] #заменить на review
    sentences = [sent.text for sent in sentencizer(text).sents]
    meta_text = []
    for sentence in sentences:
        doc = tagger(sentence)
        meta_sentence = []
        for token in doc:
            # for each word in sentence meta information is pos, normal form, original form
            # для поиска по части речи
            pos = token.pos_
            # для поиса по словоформе
            normal_form = token.lemma_
            original_form = token.text
            meta = (pos, normal_form, original_form)
            meta_sentence.append(meta)
        meta_text.append(meta_sentence)
    corpus['meta'][index] = meta_text
    print(corpus.iloc[index])
    break
