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
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis

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


# pyLDAvis visualization
print("\n" + "="*50)
print("PREPARING PYLDAVIS VISUALIZATION...")
print("="*50)

# Prepare the visualization data
vis_data = gensimvis.prepare(lda, doc_term_matrix, dictionary)

# Save visualization to HTML file
output_file = 'lda_visualization.html'
pyLDAvis.save_html(vis_data, output_file)
print(f"\n✓ Visualization saved to: {output_file}")
print("  Open this file in your web browser to explore the LDA topics interactively.")

# Display topic-word associations for reference
print("\n" + "="*50)
print("TOPIC INTERPRETATION (Top 10 words per topic)")
print("="*50)
for idx, topic in lda.print_topics(num_topics=3, num_words=10):
    print(f"\nTopic {idx}:")
    words = [word.split('*')[1].replace('"', '') for word in topic.split(' + ')]
    for i, word in enumerate(words, 1):
        print(f"  {i}. {word}")

# Document-topic dominance analysis
print("\n" + "="*50)
print("DOCUMENT-TOPIC DOMINANCE")
print("="*50)
for i, doc in enumerate(doc_term_matrix, 1):
    doc_topics = lda.get_document_topics(doc, minimum_probability=0.0)
    sorted_topics = sorted(doc_topics, key=lambda x: x[1], reverse=True)
    dominant_topic = sorted_topics[0]
    print(f"Doc {i}: Dominant Topic {dominant_topic[0]} ({dominant_topic[1]:.3f})")
    print(f"  Text: {corpus[i-1][:80]}...")
