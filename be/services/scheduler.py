"""
Scheduler service for automatic batch topic model updates.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import logging
from datetime import datetime

from config import settings
from database import SessionLocal
from services.topic_modeling import train_model, get_topic_words
from services.openai_labeling import generate_topic_label

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Global scheduler instance
scheduler: Optional[BackgroundScheduler] = None


def process_unassigned_wishes():
    """
    Background job to process wishes that don't have a topic yet.
    Trains BERTopic model on unassigned wishes and updates database.
    """
    db = SessionLocal()
    try:
        logger.info("Starting batch update for unassigned wishes...")

        # Fetch wishes without topics
        from models.wish import Wish
        from models.topic import Topic
        from models.topic_wish import TopicWish
        from models.model_update import ModelUpdate

        unassigned_wishes = db.query(Wish).filter(
            Wish.topic_id.is_(None),
            Wish.is_deleted == False
        ).all()

        if len(unassigned_wishes) < settings.HDBSCAN_MIN_CLUSTER_SIZE:
            logger.info(f"Not enough unassigned wishes ({len(unassigned_wishes)}) for training")
            return

        logger.info(f"Processing {len(unassigned_wishes)} unassigned wishes")

        # Extract documents
        documents = [wish.content for wish in unassigned_wishes]
        wish_ids = [wish.id for wish in unassigned_wishes]

        # Train model
        logger.info("Training BERTopic model...")
        topic_model, topics, probabilities = train_model(documents)

        # Get unique topics (excluding outliers -1)
        unique_topics = set([t for t in topics if t != -1])
        logger.info(f"Found {len(unique_topics)} topics")

        # Create model update record
        model_update = ModelUpdate(
            version=_get_next_version(db),
            status="running",
            wishes_count=len(unassigned_wishes),
            topics_created=len(unique_topics),
            configuration={
                "embedding_model": settings.EMBEDDING_MODEL,
                "umap_components": settings.UMAP_N_COMPONENTS,
                "min_cluster_size": settings.HDBSCAN_MIN_CLUSTER_SIZE
            }
        )
        db.add(model_update)
        db.commit()

        try:
            # Process each topic
            for topic_id in unique_topics:
                # Get topic words
                top_words = get_topic_words(topic_model, topic_id, top_n_words=10)

                # Get sample documents for this topic
                topic_indices = [i for i, t in enumerate(topics) if t == topic_id]
                sample_docs = [documents[i] for i in topic_indices[:5]]

                # Generate label with OpenAI
                logger.info(f"Generating label for topic {topic_id}...")
                label_data = generate_topic_label(top_words, sample_docs)

                # Create topic in database
                topic = Topic(
                    name=label_data["name"],
                    description=label_data["description"],
                    wish_count=len(topic_indices),
                    embedding_model=settings.EMBEDDING_MODEL,
                    topic_model_id=str(model_update.id)
                )
                db.add(topic)
                db.flush()  # Get the topic ID

                # Update wishes with primary topic and create associations
                for idx in topic_indices:
                    wish_id = wish_ids[idx]
                    wish = db.query(Wish).filter(Wish.id == wish_id).first()

                    if wish:
                        # Set primary topic
                        wish.topic_id = topic.id

                        # Get probability for this wish-topic pair
                        prob = float(probabilities[idx][topic_id])

                        # Create topic-wish association
                        topic_wish = TopicWish(
                            topic_id=topic.id,
                            wish_id=wish_id,
                            probability=prob,
                            is_primary=True
                        )
                        db.add(topic_wish)

            # Commit all changes
            db.commit()

            # Update model update status
            model_update.status = "completed"
            model_update.completed_at = datetime.now()
            db.commit()

            logger.info(f"Batch update completed successfully: {len(unique_topics)} topics created")

        except Exception as e:
            db.rollback()
            model_update.status = "failed"
            db.commit()
            logger.error(f"Error during batch update: {e}", exc_info=True)
            raise

    except Exception as e:
        logger.error(f"Error in process_unassigned_wishes: {e}", exc_info=True)
    finally:
        db.close()


def _get_next_version(db: Session) -> int:
    """Get the next version number for model updates."""
    from models.model_update import ModelUpdate

    last_update = db.query(ModelUpdate).order_by(ModelUpdate.version.desc()).first()
    if last_update:
        return last_update.version + 1
    return 1


def start_scheduler():
    """Start the background scheduler for batch updates."""
    global scheduler

    if not settings.ENABLE_SCHEDULER:
        logger.info("Scheduler is disabled in configuration")
        return

    if scheduler is not None and scheduler.running:
        logger.warning("Scheduler is already running")
        return

    scheduler = BackgroundScheduler()

    # Schedule batch updates
    scheduler.add_job(
        func=process_unassigned_wishes,
        trigger=IntervalTrigger(minutes=settings.BATCH_UPDATE_INTERVAL_MINUTES),
        id="batch_update",
        name="Batch topic model update",
        replace_existing=True
    )

    scheduler.start()
    logger.info(f"Scheduler started (interval: {settings.BATCH_UPDATE_INTERVAL_MINUTES} minutes)")


def stop_scheduler():
    """Stop the background scheduler."""
    global scheduler

    if scheduler is not None and scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    else:
        logger.warning("Scheduler is not running")


def trigger_manual_update():
    """Manually trigger a batch update (useful for testing)."""
    logger.info("Manually triggering batch update...")
    process_unassigned_wishes()
