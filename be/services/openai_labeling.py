"""
OpenAI labeling service for generating human-readable topic labels.
"""
from openai import OpenAI
from typing import Any, Dict, List, Optional
from config import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_topic_label(top_words: List[str], sample_documents: List[str]) -> Dict[str, str]:
    """
    Generate a human-readable label and description for a topic using GPT-4.

    Args:
        top_words: List of most important words in the topic
        sample_documents: List of example documents from this topic

    Returns:
        Dictionary with 'name' and 'description' keys

    Example:
        >>> words = ["peace", "harmony", "unity"]
        >>> docs = ["I wish for world peace", "I want everyone to get along"]
        >>> result = generate_topic_label(words, docs)
        >>> print(result['name'])
        "World Peace & Harmony"
    """
    # Prepare the prompt
    words_str = ", ".join(top_words[:10])
    docs_str = "\n".join([f"- {doc}" for doc in sample_documents[:5]])

    prompt = f"""You are analyzing topics from a "wishing well" app where people submit wishes.

Given the following information about a topic:
- Top words: {words_str}
- Sample wishes from this topic:
{docs_str}

Generate a concise, human-readable label and description for this topic.

Return your response in this exact JSON format (no markdown, no explanation):
{{
    "name": "Short, catchy topic name (3-6 words)",
    "description": "Brief description of what kinds of wishes belong here (1-2 sentences)"
}}

Examples of good names:
- "World Peace & Harmony"
- "Financial Freedom"
- "Health & Longevity"
- "Travel & Adventure"
- "Skills & Knowledge"

Make the name sound natural and appealing, like a category in a wish catalog.
"""

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that labels topics concisely."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more focused labels
            max_tokens=150
        )

        result = response.choices[0].message.content.strip()

        # Parse JSON response
        import json
        label_data = json.loads(result)

        return {
            "name": label_data.get("name", "Unknown Topic"),
            "description": label_data.get("description", "")
        }

    except Exception as e:
        print(f"Error generating topic label: {e}")
        # Fallback to a simple label based on top words
        return {
            "name": f"Topic: {', '.join(top_words[:3])}",
            "description": f"Keywords: {words_str}"
        }


def batch_generate_labels(
    topics_data: List[Dict[str, Any]]
) -> Dict[int, Dict[str, str]]:
    """
    Generate labels for multiple topics in batch.

    Args:
        topics_data: List of dicts with keys:
            - topic_id: int
            - top_words: List[str]
            - sample_documents: List[str]

    Returns:
        Dictionary mapping topic_id to label data

    Example:
        >>> topics = [
        ...     {"topic_id": 0, "top_words": [...], "sample_documents": [...]},
        ...     {"topic_id": 1, "top_words": [...], "sample_documents": [...]},
        ... ]
        >>> labels = batch_generate_labels(topics)
        >>> print(labels[0]['name'])
    """
    labels = {}

    for topic_data in topics_data:
        topic_id = topic_data["topic_id"]
        top_words = topic_data["top_words"]
        sample_documents = topic_data["sample_documents"]

        label = generate_topic_label(top_words, sample_documents)
        labels[topic_id] = label

    return labels
