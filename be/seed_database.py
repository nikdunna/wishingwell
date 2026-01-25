"""
Seed the Wishing Well database with sample wishes for testing and MVP launch.
Run this with: pipenv run python seed_database.py
"""
from database import SessionLocal
from models.wish import Wish
from datetime import datetime

# 50 diverse wishes covering different topic areas
SAMPLE_WISHES = [
    # Health & Wellness
    "I wish for perfect health and immunity from all diseases for myself and my loved ones.",
    "I wish to live forever and experience all of humanity's future achievements.",
    "I wish for the ability to heal any injury or illness with a touch.",
    "I wish for mental clarity and freedom from anxiety and depression.",
    "I wish to wake up every morning feeling refreshed and energized.",
    "I wish for my loved ones to recover from their illnesses.",
    "I wish to be free from chronic pain and have unlimited vitality.",

    # Wealth & Financial Freedom
    "I wish for unlimited financial wealth so I never have to worry about money again.",
    "I wish for financial independence and the ability to retire comfortably.",
    "I wish to never have to work a job I don't enjoy just to pay bills.",
    "I wish my family would be set for life financially.",
    "I wish for a passive income that covers all my expenses.",
    "I wish to be debt-free and own my home outright.",

    # Travel & Adventure
    "I wish to travel through time and witness any moment in history firsthand.",
    "I wish for the ability to teleport anywhere in the world instantly.",
    "I wish to travel to every country and experience all cultures.",
    "I wish for an unlimited travel budget to explore the world.",
    "I wish to visit space and see Earth from above.",
    "I wish to go on an African safari and see all the wild animals.",
    "I wish to backpack through Europe for a year.",

    # Love & Relationships
    "I wish to find my soulmate and build a happy life together.",
    "I wish for a loving and supportive partner who understands me.",
    "I wish to repair my broken relationship with my parents.",
    "I wish for true friends who will always be there for me.",
    "I wish to reconnect with my estranged sibling.",
    "I wish for a happy marriage that lasts a lifetime.",

    # Knowledge & Skills
    "I wish to have the knowledge and skills to master any instrument or art form instantly.",
    "I wish to speak and understand every language in the world fluently.",
    "I wish for the power to read people's minds and understand their deepest thoughts.",
    "I wish to download skills directly into my brain like in The Matrix.",
    "I wish to be a genius at mathematics and physics.",
    "I wish to master playing the piano virtuoso style.",

    # World Peace & Harmony
    "I wish for world peace and harmony among all nations and people.",
    "I wish for an end to all wars and conflicts worldwide.",
    "I wish humanity would come together to solve climate change.",
    "I wish for equality and justice for all people regardless of race or gender.",
    "I wish to bring back loved ones who have passed away and spend one more day with them.",
    "I wish for universal compassion and empathy among all humans.",

    # Personal Growth
    "I wish for the confidence to pursue my dreams without fear.",
    "I wish to overcome my social anxiety and be comfortable in any situation.",
    "I wish for the motivation to exercise and maintain a healthy lifestyle.",
    "I wish to break free from bad habits that hold me back.",
    "I wish for the discipline to achieve my goals.",

    # Career & Success
    "I wish for a successful career that makes a positive impact on the world.",
    "I wish to start my own business and have it be wildly successful.",
    "I wish for recognition in my field and to be respected by my peers.",
    "I wish to find work that feels meaningful and fulfilling.",
    "I wish to get promoted to a leadership position at my job.",

    # Happiness & Fulfillment
    "I wish for true happiness and contentment in life.",
    "I wish to find my life's purpose and pursue it passionately.",
    "I wish for inner peace and freedom from constant worry.",
    "I wish to appreciate every moment and live life to the fullest.",
    "I wish for the ability to fly and explore the world from the sky without any limitations.",

    # Special Powers
    "I wish for the ability to see the future.",
    "I wish for superhuman strength and invincibility.",
    "I wish for the power to grant other people's wishes.",
    "I wish to be invisible whenever I want.",
    "I wish to control time - pause, fast forward, rewind.",

    # Technology & Innovation
    "I wish for flying cars to become a reality.",
    "I wish for humans to colonize Mars in my lifetime.",
    "I wish for a cure for all types of cancer to be discovered.",
    "I wish artificial intelligence would solve all our problems.",
    "I wish for clean unlimited energy for the entire world.",
]


def seed_database():
    """Populate the database with sample wishes."""
    db = SessionLocal()

    try:
        # Check if database already has wishes
        existing_count = db.query(Wish).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} wishes. Skipping seed.")
            return

        print(f"Seeding database with {len(SAMPLE_WISHES)} sample wishes...")

        # Create wishes
        wishes = []
        for content in SAMPLE_WISHES:
            wish = Wish(content=content)
            wishes.append(wish)
            db.add(wish)

        db.commit()

        print(f"✅ Successfully seeded database with {len(wishes)} wishes!")
        print(f"   You can now run topic modeling with: POST /api/v1/admin/model/train")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
