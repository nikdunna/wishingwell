import string
import nltk
nltk.download('stopwords')
nltk.download('wordnet')  
nltk.download('omw-1.4')  
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from gensim import corpora
from gensim.models import LsiModel
from gensim.models import LdaModel

doc_1 = "I wish for the ability to speak and understand every language in the world fluently."

doc_2 = "I wish for perfect health and immunity from all diseases for myself and my loved ones."

doc_3 = "I wish for unlimited financial wealth so I never have to worry about money again."

doc_4 = "I wish to travel through time and witness any moment in history firsthand."

doc_5 = "I wish for the power to read people's minds and understand their deepest thoughts."

doc_6 = "I wish to live forever and experience all of humanity's future achievements."

doc_7 = "I wish for the ability to fly and explore the world from the sky without any limitations."

doc_8 = "I wish to have the knowledge and skills to master any instrument or art form instantly."

doc_9 = "I wish for world peace and harmony among all nations and people."

doc_10 = "I wish to bring back loved ones who have passed away and spend one more day with them."

corpus = [doc_1, doc_2, doc_3, doc_4, doc_5, doc_6, doc_7, doc_8, doc_9, doc_10]


stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()

def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = "".join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized


cleaned_corpus = [clean(doc).split() for doc in corpus]

# Creating document-term matrix 
dictionary = corpora.Dictionary(cleaned_corpus)
doc_term_matrix = [dictionary.doc2bow(doc) for doc in cleaned_corpus]


# LSA model
lsa = LsiModel(doc_term_matrix, num_topics=3, id2word = dictionary)

# LSA model
print("LSA MODEL RESULTS:")
print(lsa.print_topics(num_topics=-1, num_words=10))



# LDA model
lda = LdaModel(doc_term_matrix, num_topics=3, id2word = dictionary)

# Results
print("LDA MODEL RESULTS:")
print(lda.print_topics(num_topics=3, num_words=3))