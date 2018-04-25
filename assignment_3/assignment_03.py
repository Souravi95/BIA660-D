
import pandas as pd
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import linear_model
from sklearn import svm
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn import model_selection
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import cross_validate
import datetime
import matplotlib.pyplot as plt
import spacy


nlp= spacy.load('en')
df= pd.read_csv("C:\\Users\\soura\\Downloads\\Amazon scrape\\Amazon scrape\\output.csv")
print(df)

#cleaning the data frame to remove the unnecesary variables and words
df['rating']= df['rating'].str.extract('(\d+)', expand=True)
df['rating'].astype(int)
df['review_date']= pd.to_datetime(df['review_date'], format= "%d-%b-%y")
print(df['review_date'].sort_values())

#Filtering the data to get the values from 1 january 2017 until the day of scraping
mask = (df['review_date'] > '12-12-2016') & (df['review_date'] <= '15-4-2018')
df.loc[mask]
df = df.loc[mask]
#print(df)
print(df.head())
#creating a cleaned csv file
df.to_csv("Assignment_03.csv", sep=',')

#Preprocessing: to evaluate the reviews in order to get the counter vectorized form for further analysis
review= df['review']
review.count()
cv = CountVectorizer(lowercase=True)
cv = CountVectorizer(lowercase=True, stop_words='english', ngram_range=(2, 2))
data = cv.fit_transform(review)
print(data)
print(cv.get_feature_names())

def noun_adj_verb_filter(sentences):

    preprocessed_sentences = []
    keep_types = {'NOUN', 'PROPN', 'ADJ', 'VERB'}

    for sentence in sentences:
        doc = nlp(sentence)

        keep_tokens_string = ' '.join([t.text for t in doc if t.pos_ in keep_types])
        preprocessed_sentences.append(keep_tokens_string)

    return preprocessed_sentences

preproc_sents = noun_adj_verb_filter(df['review'])
print(preproc_sents)

cv = CountVectorizer(lowercase=True, stop_words='english',)
data1 = cv.fit_transform(preproc_sents)
print(data.toarray())
print(cv.get_feature_names())

#evaluating the length of review and plotting it for available observations
text_length = df['review'].apply(len)
print(text_length)
plt.hist(text_length)
plt.xlabel("review length")
plt.ylabel("Number of reviews")
plt.show()

#splitting the data into training and test set(of reviews and ratings)
y= df['rating']
X_train, X_test, y_train, y_test = train_test_split(data1, y, test_size=0.2)
print (X_train.shape, y_train.shape)
print (X_test.shape, y_test.shape )

#regression analysis of reviews against the reviews
lm = linear_model.LinearRegression()
model = lm.fit(X_train, y_train)
predictions = lm.predict(X_test)
print(predictions)

plt.scatter(y_test, predictions)
plt.xlabel('Actual Value')
plt.ylabel('Predicted')
plt.show()

#randomforest classification
rf= RandomForestClassifier()
scores = cross_validate(rf, data1, y, cv=10, n_jobs=-1, return_train_score=True)
print(scores)

#Modelling
#Model 1: Multinomial Naive Bayes
model = MultinomialNB()
model.fit(data1, y)
predictionsNB = model.predict(X_test)
#print(predictionsNB)
print(accuracy_score(y_test, predictionsNB, normalize= True))

#Model 2: Support Vector Machine Algorithm
model2 = svm.LinearSVC()
model2_fit= model2.fit(data1, y)
#model2.score(data1, y)
predictedSVM = model2.predict(X_test)
print(predictedSVM)
print(accuracy_score(y_test, predictedSVM, normalize= True))
