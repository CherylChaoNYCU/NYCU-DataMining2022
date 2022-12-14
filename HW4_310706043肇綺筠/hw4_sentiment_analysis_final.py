# -*- coding: utf-8 -*-
"""HW4_Sentiment_Analysis_final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/151LUQSB1HJD0vvXl7kAgo4A9sH3FBk7v

## HW4_Amazon Review Sentiment Analysis
"""

from google.colab import drive
drive.mount('/content/drive')

import zipfile
dir = '/content/drive/My Drive/colabdata/HW4data.zip'
zp = zipfile.ZipFile(dir)
for f in zp.namelist():
  zp.extract(f,'/content')
zp.close()

# upload_test = files.upload()

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import seaborn as sns
import matplotlib.pyplot as plt
#import plotly.express as ex
import io
import os

data = pd.read_csv('/content/HW4data/Reviews.csv',nrows=10000)
#kaggle_test = pd.read_csv('test.csv')

k_test = pd.read_csv('/content/HW4data/test.csv')

k_test

"""#### Columns:
    * ProductId - Unique identifier for the product
    * UserId - Unique identifier for the user
    * ProfileName - Profile name of User
    * HelpfulnessNumerator - Num of users who found review helpful
    * HelpfulnessDenomitaor - Number of users who indicated whether they found the review helpful or not
    * Score - Rating between 1 to 5
    * Time - Timestamp for the review
    * Summary - Bried summary of the review
    * Text - Text of the review

### 1. 資料前處理

a. 讀取 csv 檔後取前 1 萬筆資料

僅保留"Text"、"Score"兩個欄位

並將 "Score" 欄位內值大於等於4的轉成1，其餘轉成0

1: positive

0: negative

並將text欄位內的文字利用分割符號切割
"""

from sklearn.feature_extraction.text import TfidfVectorizer
new_d = data.loc[:,['Text','Score']]

#testing data(Text欄位)
new_d

#training data(Score欄位)
#dy = np.where(new_d['Score']>=4,1,0)

new_d['sentiment']=new_d.Score.apply(lambda x:1 if x in [4,5] else 0 )
pd.value_counts(new_d.sentiment)

new_d

#pd.value_counts(dy) #2384 negative 7616 positive



"""b. 去除停頓詞stop words 

在Amazon 'Text'欄位中不重要的停頓詞、無法幫助資料判讀的贅詞：

a. html tags.

b. punctuations and special characters

c. Convert the word to lowercase

d. stopwords

e. (word stemming...)

"""

import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import numpy
import re
from bs4 import BeautifulSoup

import nltk
nltk.download('stopwords')

dx = new_d['Text']
#stop_word = [ '(', ')',',', '.', '!', '?', ':', '-',';','\n']
stop=set(stopwords.words('english'))#檢查英文裡面常見的停頓詞
snow = nltk.stem.SnowballStemmer('english')
#stop
def decontracted(phrase):
    phrase=re.sub(r"won't","will not",phrase)
    phrase=re.sub(r"can't","can not",phrase)
    phrase=re.sub(r"n\'t","not",phrase)
    phrase=re.sub(r"\'re","are",phrase)
    phrase=re.sub(r"\'s","is",phrase)
    phrase=re.sub(r"\'d","would",phrase)
    phrase=re.sub(r"\'ll","will",phrase)    
    phrase=re.sub(r"\'t","not",sentence)
    phrase=re.sub(r"\'ve","have",sentence)
    phrase=re.sub(r"\'m","am",sentence)
    return phrase
preprocessed_reviews=[]#存取清理好的Text
test_rev = []

tx = k_test['Text']
for sentence in dx.values:
    sentence=re.sub(r"http\S+"," ",sentence)#remove html tags
    sentence=BeautifulSoup(sentence,'lxml').get_text()
    cleanr=re.compile('<.*?>')
    sentence=re.sub(cleanr,' ',sentence)
    sentence=decontracted(sentence)
    sentence=re.sub("\S\*\d\S*"," ",sentence)
    sentence=re.sub("[^A-Za-z]+"," ",sentence)
    sentence=re.sub(r'[?|!|\'|"|#]',r' ',sentence)
    sentence=re.sub(r'[.|,|)|(|\|/]',r' ',sentence)
    sentence='  '.join(snow.stem(e.lower()) for e in sentence.split() if e.lower() not in stop)
    preprocessed_reviews.append(sentence.strip())

#cleaning the testing set
for sentence in tx.values:
    sentence=re.sub(r"http\S+"," ",sentence)#remove html tags
    sentence=BeautifulSoup(sentence,'lxml').get_text()
    cleanr=re.compile('<.*?>')
    sentence=re.sub(cleanr,' ',sentence)
    sentence=decontracted(sentence)
    sentence=re.sub("\S\*\d\S*"," ",sentence)
    sentence=re.sub("[^A-Za-z]+"," ",sentence)
    sentence=re.sub(r'[?|!|\'|"|#]',r' ',sentence)
    sentence=re.sub(r'[.|,|)|(|\|/]',r' ',sentence)
    sentence='  '.join(snow.stem(e.lower()) for e in sentence.split() if e.lower() not in stop)
    test_rev.append(sentence.strip())

new_d['cleaned_review'] = np.array(preprocessed_reviews)
test_for_k=  test_rev

#test_new

new_d

#making the lenght of neg and positive review the same
#讓正面負面評論的數量一樣多有助於data balanced
new_d = new_d.sample(frac=1)
pos_df=new_d.loc[new_d.sentiment==1,:][:2384]
neg_df=new_d.loc[new_d.sentiment==0,:][:2384]
text_1= pd.concat([pos_df,neg_df])
text_1 = text_1.sample(frac=1) #打亂review的順序
pd.value_counts(text_1.sentiment)

text_1



"""### 2. 建模

b. 自行撰寫function進行k-fold cross-validation(不可使用套件)並計算Accuracy

b-1. input(k, data)，將data切成k份，其中1份當測試集，剩餘k-1份當訓練集建立模型

b-2. 輪流將k份的每份資料都當 測試集，其餘當訓練集建立模型，因此會進行k次，k次都計算出Accuracy

b-3. 將k次的Accuracy平均即為output

#### word2vec

了解此模型背後運作原理：https://clay-atlas.com/blog/2020/01/17/python-chinese-tutorial-gensim-word2vec/

#### 以下開始實作word2vec
"""

#from bs4 import BeautifulSoup 
 # regex
#from tensorflow import keras
from keras.preprocessing.text import Tokenizer
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
import keras
#from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from tensorflow.keras.utils import img_to_array
from keras.layers import Dense,Input,BatchNormalization,Dropout,Flatten
from keras.layers import Conv2D,MaxPooling2D
from keras.datasets import mnist
from keras.models import Sequential
from keras import backend as K

corpus = [] #record all the text in reviews

for i in text_1.cleaned_review:
    corpus.append(i.split()) #each row one review sentence

corpus_testk = []
for i in test_for_k:
    corpus_testk.append(i.split()) #each row one review sentence

corpus

corpus_testk

from gensim.models import Word2Vec
w2v_model = Word2Vec(corpus,min_count=10,window=20 ,workers=10)
w2v_model.save('w2v.model')
w2v_k = Word2Vec(corpus_testk,min_count=10,window=20 ,workers=10)

text_1.cleaned_review



#shuffle完review資料之後重新給text_1的內容編碼(index from 0...n)
#ref:https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reset_index.html

text_1 = text_1.sample(frac=1).reset_index(drop=True)
tok = Tokenizer() #建立token給每個review中的文字
tok.fit_on_texts(text_1.cleaned_review.astype(str))#依照review中某文字出現的次數做排序
vocab_size = len(tok.word_index) + 1
encd_rev = tok.texts_to_sequences(text_1.cleaned_review.astype(str)) #encode reviews,把每個review文字都encode成數字list 
print(vocab_size)

"""### 給kaggle評分用的，處理測試級"""

#kaggle_t = text_1.sample(frac=1).reset_index(drop=True)
tok2 = Tokenizer() #建立token給每個review中的文字
tok2.fit_on_texts(test_for_k)#依照review中某文字出現的次數做排序
vocab_size2 = len(tok2.word_index) + 1
encd_rev_k = tok.texts_to_sequences(test_for_k) #encode reviews,把每個review文字都encode成數字list 
print(vocab_size2)

max_ = -1
for i,rev in enumerate(text_1['cleaned_review']):
    if(type(rev)!=float):
        tokens = rev.split() #這裡是要把review中最長的（文字最多的）找出來，後面要做padding把他們都變一樣長
        if(len(tokens)>max_):
            max_ = len(tokens)
print(max_)

#for kaggle
max2 = -1
for i,rev in enumerate(test_for_k):
    if(type(rev)!=float):
        tokens = rev.split() #這裡是要把review中最長的（文字最多的）找出來，後面要做padding把他們都變一樣長
        if(len(tokens)>max2):
            max2 = len(tokens)
print(max2)

max_rev_len=max_ # max lenght of a review
vocab_size = len(tok.word_index) + 1  # total no of words
vocab_size

#for kaggle
max_rev_len2=max2 # max lenght of a review
vocab_size2 = len(tok2.word_index) + 1  # total no of words
vocab_size2

#把review sequence都padding成一樣長度
from keras_preprocessing.sequence import pad_sequences
pad_rev= pad_sequences(encd_rev, maxlen=max_rev_len2) #encd_rev是每個review的數字list,需把他們都padding成跟最長的review一樣長
pad_rev.shape #各個review現在已經成為長度為476的數字list, 分別對應text_1之中的sentiment(label)

pad_rev2= pad_sequences(encd_rev_k, maxlen=max_rev_len2) #encd_rev是每個review的數字list,需把他們都padding成跟最長的review一樣長
pad_rev2.shape

from sklearn.model_selection import train_test_split
y= text_1.sentiment#.to_numpy()#sentiment (0 neg , 1 pos)轉成二進制, ex. :rev1:0 ->[1,0,0,0] rev2:1->[0,1,0,0]...
x_train,x_test,y_train,y_test=train_test_split(pad_rev,y,test_size=0.20,random_state=42)

#r_ytrain = y_train.reshape(-1,1)



#r_ytest = y_test.reshape(-1,1)

embedding_matrix = np.zeros((vocab_size, 100))
for word, i in tok.word_index.items():
    if word in w2v_model.wv.vocab:
        embedding_matrix[i] = w2v_model.wv.word_vec(word)#訓練過後各個文字的詞向量取出來，丟進embedding matrix,作為接下來進入LSTM用的pretrained weights
print('Null word embeddings: %d' % np.sum(np.sum(embedding_matrix, axis=1) == 0))

"""### 2. 建模(HW4)

a. 分別用CNN與LSTM對train的資料進行建模，可自行設計神經網路的架構

b. 加入Dropout Layer設定Dropout參數(建議0.7)進行比較

c. plot出訓練過程中的Accuracy與Loss值變化



"""

from keras.regularizers import L1L2
from keras.layers import Dense,Flatten,Conv1D,MaxPooling1D
from keras.layers import ReLU,LSTM,GRU, GlobalMaxPooling1D,Conv1D,CuDNNLSTM
from keras.layers import Dropout , Bidirectional
from keras.layers import ZeroPadding2D,Activation
#from tensorflow.keras.layers.embeddings import Embedding
from tensorflow.keras.layers import Embedding
from keras.models import Sequential

"""### CNN"""

# define model
model_cnn = Sequential()
model_cnn.add(Embedding(vocab_size, 100,weights=[embedding_matrix], input_length=max_rev_len2))
model_cnn.add(Conv1D(filters=32, kernel_size=3, activation='relu'))
model_cnn.add(Dropout(0.7))
model_cnn.add(MaxPooling1D(pool_size=2))
model_cnn.add(Conv1D(filters=64, kernel_size=3, activation='relu'))
model_cnn.add(Dropout(0.7))
model_cnn.add(MaxPooling1D(pool_size=2))
model_cnn.add(Flatten())
model_cnn.add(Dense(10, activation='relu'))
model_cnn.add(Dense(1, activation='sigmoid'))
print(model_cnn.summary())

# compile network
model_cnn.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
# fit network
history_cnn = model_cnn.fit(x_train, y_train, epochs=10, verbose=2,validation_data=(x_test,y_test))

#history_cnn=model_cnn.fit(x_train,y_train,batch_size=64,epochs=5,validation_data=(x_test,y_test))

"""### LSTM"""

from keras.layers import LSTM
from keras.preprocessing import sequence

model_lstm = Sequential()
model_lstm.add(Embedding(vocab_size,100,weights=[embedding_matrix], input_length=max_rev_len2,trainable=False))
model_lstm.add(LSTM(100,return_sequences=True))
model_lstm.add(Dropout(0.5))
model_lstm.add(LSTM(100))
model_lstm.add(Dropout(0.5))
model_lstm.add(Dense(1, activation='sigmoid'))

model_lstm.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model_lstm.summary())

history_lstm=  model_lstm.fit(x_train, y_train,validation_data=(x_test, y_test),epochs=15,verbose=2)
#scores = model_lstm.evaluate(x_test, y_test, verbose=0)
#print("Accuracy: %.2f%%" % (scores[1]*100))

"""### 執行結果

#### plot Accuracy
"""

def ploting_acc(tmp,train,val):
  plt.figure()
  plt.plot(tmp.history[train])
  plt.plot(tmp.history[val])
  plt.title('Train History')
  plt.xlabel('epoch')
  plt.ylabel('accuracy')
  plt.legend(['train','val'],loc='upper left')
  plt.show()

"""### plot Loss"""

def ploting_loss(tmp,train,val):
  plt.figure()
  plt.plot(tmp.history[train])
  plt.plot(tmp.history[val])
  plt.title('Train History')
  plt.xlabel('epoch')
  plt.ylabel('loss')
  plt.legend(['train','val'],loc='upper left')
  plt.show()

ploting_acc(history_cnn,'accuracy','val_accuracy')

score = model_cnn.evaluate(x_test,y_test,verbose=0)
print('Test Accuracy CNN:{}'.format(score[1]))

ploting_acc(history_lstm,'accuracy','val_accuracy')

score = model_lstm.evaluate(x_test,y_test,verbose=0)
print('Test Accuracy LSTM:{}'.format(score[1]))

ploting_loss(history_cnn,'loss','val_loss')

ploting_loss(history_lstm,'loss','val_loss')

"""### 評估模型

a. 利用kaggle上test的資料對2.所建立的模型進行測試，並計算Accuracy

1. CNN:
把cnn prediction(通過sigmoid所以介於0~1的機率）>=0.5的當作1 (positive),其餘negative

2. LSTM:

"""

pred = model_cnn.predict(pad_rev2)
output = pd.DataFrame()
myList = np.linspace(1, 5000,5000).astype(int)
output['ID'] = myList
binary = []
for i in range(0,5000):
  if pred[i]>=0.5: #as we get "half neg and half positive, I choose threshold >=0.5 to be '1'"
    binary.append(1)
  else:
    binary.append(0)

output['Score'] = binary
output.to_csv('submitHW4_cnn.csv', index = False)

pred = model_lstm.predict(pad_rev2)
output = pd.DataFrame()
myList = np.linspace(1, 5000,5000).astype(int)
output['ID'] = myList
binary = []
for i in range(0,5000):
  if pred[i]>=0.5: #lstm
    binary.append(1)
  else:
    binary.append(0)

output['Score'] = binary
output.to_csv('submitHW4_lstm.csv', index = False)

"""### 後續debug
1. 試試看不要balanced data(10000全下去train) ->狀況不好，data正負樣本不平衡

2. cnn試試看不要用 pretrained embedding, 或是減少conv層數

3. LSTM網路架構調整一下

"""