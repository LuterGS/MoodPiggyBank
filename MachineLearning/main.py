# -*- coding: utf-8 -*-
"""MoodPiggyBank.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fk7KAUmIOEVA6ME2i-avMf8eIQe1aKKA
"""

# Commented out IPython magic to ensure Python compatibility.
!pip install konlpy
import pandas as pd
import numpy as np
# %matplotlib inline
import matplotlib.pyplot as plt
import re
import urllib.request
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

from tensorflow.keras.layers import Embedding, Dense, LSTM
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

urllib.request.urlretrieve("https://raw.githubusercontent.com/e9t/nsmc/master/ratings_train.txt", filename="ratings_train.txt")
urllib.request.urlretrieve("https://raw.githubusercontent.com/e9t/nsmc/master/ratings_test.txt", filename="ratings_test.txt")

def preprocessing(data):
  data = data.drop_duplicates(subset=['document'])
  data = data.dropna(how = 'any')
  data['document'] = data['document'].str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]","")
  data['document'] = data['document'].replace('', np.nan)
  data = data.dropna(how = 'any')
  return data

def Token(data, okt, stopwords):
  now = 0
  res = list()
  print("start token")
  for sentence in data['document']:
    if now%10000 == 0:
      print(f"token : {now}/{len(data)}")
    now = now +1
    temp = list()
    temp = okt.morphs(sentence, stem=True)
    temp = [word for word in temp if not word in stopwords]
    res.append(temp)
  print("end token")
  return res

def Tokenizing(data, tokenizer):
  return tokenizer.texts_to_sequences(data)

def rmEmpty(data, label):
  drop_data = [index for index, sentence in enumerate(X_train) if len(sentence) < 1]
  data = np.delete(data, drop_data, axis=0)
  label = np.delete(label, drop_data, axis=0)
  return data, label

def sentiment_predict(sentence, okt, stopwords, tokenizer):
  sentence = okt.morphs(sentence, stem=True)
  sentence = [word for word in sentence if not word in stopwords]
  encoded = tokenizer.texts_to_sequences([sentence])
  padding_sentence = pad_sequences(encoded, maxlen = 30)
  score = float(loaded_model.predict(padding_sentence))
  if score > 0.5:
    print(f"긍정 / Score : {score}")
  else:
    print(f"부정 / Score : {score}")

# 데이터 tokenizing 하기
train_data = pd.read_table('ratings_train.txt')
test_data = pd.read_table('ratings_test.txt')
X_train = list()
X_test = list()
okt = Okt()
stopwords = ['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다']

train_data = preprocessing(train_data)
test_data = preprocessing(test_data)

X_train = Token(train_data, okt, stopwords)
X_test = Token(test_data, okt, stopwords)

tokenizer = Tokenizer(19417, oov_token = 'OOV')
tokenizer.fit_on_texts(X_train)

X_train = Tokenizing(X_train, tokenizer)
X_test = Tokenizing(X_test, tokenizer)

# label 데이터 생성
Y_train = np.array(train_data['label'])
Y_test = np.array(test_data['label'])

X_train, Y_train = rmEmpty(X_train, Y_train)

# padding
X_train = pad_sequences(X_train, maxlen = 30)
X_test = pad_sequences(X_test, maxlen = 30)

# Model
model = Sequential(
    [
     Embedding(19417, 100),
     LSTM(128),
     Dense(1, activation = 'sigmoid'),
    ]
)

earlyStop = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=4)
modelCP = ModelCheckpoint('best_model.h5', monitor='val_acc', mode='max', verbose=1, save_best_only=True)

model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['acc'])
history = model.fit(X_train, Y_train, epochs=15, callbacks=[earlyStop, modelCP], batch_size=60, validation_split=0.2)

loaded_model = load_model('best_model.h5')

sentiment_predict("이 영화 재미없어요...", okt, stopwords, tokenizer)

