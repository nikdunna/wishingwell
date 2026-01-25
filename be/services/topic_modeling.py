"""
BERTopic service for topic modeling on wishes.
"""
from typing import List, Tuple, Dict, Any
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

from config import settings


def create_bertopic_model() -> BERTopic:
    """
    Create and configure a BERTopic model with custom parameters.

    Returns:
        Configured BERTopic model

    Example:
        >>> model = create_bertopic_model()
        >>> topics, probs = model.fit_transform(documents)
    """
    # Initialize embedding model
    embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

    # Dimensionality reduction
    umap_model = UMAP(
        n_components=settings.UMAP_N_COMPONENTS,
        min_dist=0.0,
        metric='cosine',
        random_state=42
    )

    # Clustering
    hdbscan_model = HDBSCAN(
        min_cluster_size=settings.HDBSCAN_MIN_CLUSTER_SIZE,
        metric='euclidean',
        cluster_selection_method='eom',
        prediction_data=True
    )

    # Vectorizer - more flexible for small datasets
    vectorizer_model = CountVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,  # Changed from 2 to 1 for small datasets
        max_df=0.95  # Ignore words appearing in >95% of docs
    )

    # Create BERTopic
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        verbose=True,
        calculate_probabilities=True
    )

    return topic_model


def train_model(documents: List[str]) -> Tuple[BERTopic, np.ndarray, np.ndarray]:
    """
    Train a BERTopic model on a list of documents.

    Args:
        documents: List of wish documents

    Returns:
        Tuple of (topic_model, topics, probabilities)
        - topic_model: Trained BERTopic model
        - topics: Array of topic assignments (-1 for outliers)
        - probabilities: Array of topic probabilities

    Example:
        >>> docs = ["I wish for peace", "I wish for health", "I want money"]
        >>> model, topics, probs = train_model(docs)
        >>> print(f"Found {len(set(topics)) - 1} topics")
    """
    model = create_bertopic_model()
    topics, probabilities = model.fit_transform(documents)
    return model, topics, probabilities


def get_topic_words(topic_model: BERTopic, topic_id: int, top_n_words: int = 10) -> List[str]:
    """
    Extract top words for a specific topic.

    Args:
        topic_model: Trained BERTopic model
        topic_id: Topic ID to get words for
        top_n_words: Number of top words to return

    Returns:
        List of top words for the topic

    Example:
        >>> words = get_topic_words(model, topic_id=0, top_n_words=5)
        >>> print(words)
        ['peace', 'world', 'harmony', ...]
    """
    if topic_id == -1:
        return []  # Outlier topic

    topic_info = topic_model.get_topic(topic_id)
    if not topic_info:
        return []

    words = [word for word, _ in topic_info[:top_n_words]]
    return words


def get_document_topics(
    topic_model: BERTopic,
    document: str,
    top_n_topics: int = 3
) -> List[Tuple[int, float]]:
    """
    Get topic distribution for a single document.

    Args:
        topic_model: Trained BERTopic model
        document: Document text to analyze
        top_n_topics: Number of top topics to return

    Returns:
        List of (topic_id, probability) tuples, sorted by probability

    Example:
        >>> topics = get_document_topics(model, "I wish for world peace")
        >>> print(topics)
        [(0, 0.85), (2, 0.12), (1, 0.03)]
    """
    topics, probs = topic_model.transform([document])

    # Filter out outlier topic (-1) and sort by probability
    topic_probs = [
        (int(topic), float(prob))
        for topic, prob in zip(topics[0], probs[0])
        if topic != -1
    ]
    topic_probs.sort(key=lambda x: x[1], reverse=True)

    return topic_probs[:top_n_topics]


def reduce_topics(topic_model: BERTopic, documents: List[str], min_topic_size: int = None) -> BERTopic:
    """
    Reduce number of topics by merging small topics.

    Args:
        topic_model: Trained BERTopic model
        documents: Original training documents
        min_topic_size: Minimum topic size threshold

    Returns:
        Updated BERTopic model with reduced topics

    Example:
        >>> model = reduce_topics(model, docs, min_topic_size=10)
        >>> print(f"Reduced to {model.get_topic_info().shape[0]} topics")
    """
    if min_topic_size is None:
        min_topic_size = settings.MIN_TOPIC_SIZE

    topic_model.reduce_topics(documents, min_topic_size=min_topic_size)
    return topic_model
