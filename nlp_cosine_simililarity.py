import urllib2

def readURLDoc(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_page = response.read()
    return the_page

#f = open("/root/Myfolder/scoringDocuments/doc1")
#doc1 = str.decode(f.read(), "UTF-8", "ignore")
#f = open("/root/Myfolder/scoringDocuments/doc2")
#doc2 = str.decode(f.read(), "UTF-8", "ignore")
#f = open("/root/Myfolder/scoringDocuments/doc3")
#doc3 = str.decode(f.read(), "UTF-8", "ignore")

doc1 = readURLDoc('https://en.wikipedia.org/wiki/Machine_learning')
doc2 = readURLDoc('https://en.wikipedia.org/wiki/Computer_science')
doc3 = readURLDoc('https://en.wikipedia.org/wiki/Algorithm')
query = 'clustering classification'

#doc1 = "The sky is blue."
#doc2 = "The sun is bright."
#doc3 = "The sun appears in the nice blue sky"
#query = "The sun in the sky is bright."

#sent1 = "did you type \"donald trumb\" to get that result, because I\m only calling him that from now on"
#sent2 = 'Today is #Brexit Tomorrow is #Trumb and after tomorrow !!! Who knows'
#sent3 = 'When you see trumb and boten welcome that exit so you should be sure that will be the worse for the island '
#sent4 = '.for this \'Trumb\' guy, I read he wants no Muslim to sit a foot in America. If so, he\'s gotta be crazy '



#%%
import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer


stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]

print 'Test 1: '
print cosine_sim(query, doc1)
print cosine_sim(query, doc2)
print cosine_sim(query, doc3)


#%%%

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


#train_set = ["president of India",doc1, doc2, doc3]
train_set = [query,doc1, doc2, doc3]

tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix_train = tfidf_vectorizer.fit_transform(train_set)  #finds the tfidf score with normalization
print "cosine scores ==> ",cosine_similarity(tfidf_matrix_train[0:1], tfidf_matrix_train)  #here the first element of tfidf_matrix_train is matched with other three elements


#%%

#from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from nltk.corpus import stopwords
import numpy as np
import numpy.linalg as LA

train_set = [doc1, doc2, doc3] #Documents
test_set = [query] #Query

stopWords = stopwords.words('english')

vectorizer = CountVectorizer(stop_words = stopWords)
#print vectorizer
transformer = TfidfTransformer()
#print transformer

trainVectorizerArray = vectorizer.fit_transform(train_set).toarray()
testVectorizerArray = vectorizer.transform(test_set).toarray()
print 'Fit Vectorizer to train set', trainVectorizerArray
print 'Transform Vectorizer to test set', testVectorizerArray
cx = lambda a, b : round(np.inner(a, b)/(LA.norm(a)*LA.norm(b)), 3)

for vector in trainVectorizerArray:
    #print vector
    for testV in testVectorizerArray:
        #print testV
        cosine = cx(vector, testV)
        print cosine

transformer.fit(trainVectorizerArray)
print
print transformer.transform(trainVectorizerArray).toarray()

transformer.fit(testVectorizerArray)
print 
tfidf = transformer.transform(testVectorizerArray)
print ":::" , tfidf.todense()


#%%

from sklearn.neighbors import LSHForest

X_train = [[0, 1, 1], [0, 0, 1], [1, 1, 1], [0, 1, 0]]
X_test = [[0, 0, 1], [1, 1, 10]]
lshf = LSHForest(random_state=42)
lshf.fit(X_train)  

#LSHForest(min_hash_match=4, n_candidates=50, n_estimators=10,
#          n_neighbors=5, radius=1.0, radius_cutoff_ratio=0.9,
#          random_state=42)
distances, indices = lshf.kneighbors(X_test, n_neighbors=4)
print distances         
       
print indices


