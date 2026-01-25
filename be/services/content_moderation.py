"""
Content moderation service using OpenAI's moderation API.
"""
from openai import OpenAI
from typing import Optional, Tuple
from config import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def moderate_content(content: str) -> Tuple[bool, Optional[str]]:
    """
    Check if content violates OpenAI's content policies.

    Args:
        content: The text content to moderate

    Returns:
        Tuple of (is_safe, rejection_reason)
        - is_safe: True if content passes moderation
        - rejection_reason: None if safe, otherwise reason for rejection

    Example:
        >>> is_safe, reason = moderate_content("I wish for world peace")
        >>> print(is_safe)
        True
    """
    try:
        response = client.moderations.create(input=content)
        result = response.results[0]

        if result.flagged:
            # Collect flagged categories
            flagged_categories = [
                category
                for category, flagged in result.categories.model_dump().items()
                if flagged
            ]

            reason = f"Content flagged for: {', '.join(flagged_categories)}"
            return False, reason

        return True, None

    except Exception as e:
        # If moderation API fails, err on the side of caution
        error_msg = f"Moderation service error: {str(e)}"
        print(f"ERROR: {error_msg}")
        return False, error_msg


def should_reject_wish(content: str) -> Tuple[bool, Optional[str]]:
    """
    Determine if a wish should be rejected based on content moderation.

    Args:
        content: The wish text to evaluate

    Returns:
        Tuple of (should_reject, rejection_reason)
    """
    return moderate_content(content)
