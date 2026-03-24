from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, Boolean, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.core.config import settings

Base = declarative_base()


class ContentPieceTable(Base):
    __tablename__ = "content_pieces"
    
    id = Column(String, primary_key=True)
    topic = Column(String, nullable=False)
    keywords = Column(JSON, nullable=True)
    target_platforms = Column(JSON, nullable=False)
    content_type = Column(String, nullable=False)
    additional_context = Column(Text, nullable=True)
    tone = Column(String, nullable=True)
    target_audience = Column(String, nullable=True)
    
    research_data = Column(JSON, nullable=True)
    draft_data = Column(JSON, nullable=True)
    reviewed_data = Column(JSON, nullable=True)
    
    status = Column(String, nullable=False, default="pending")
    platform = Column(String, nullable=False)
    published_url = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HumanReviewTable(Base):
    __tablename__ = "human_reviews"
    
    id = Column(String, primary_key=True)
    content_piece_id = Column(String, nullable=False)
    reviewer_notes = Column(Text, nullable=True)
    approved = Column(Boolean, nullable=False)
    modifications = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow)


class ScheduledPostTable(Base):
    __tablename__ = "scheduled_posts"
    
    id = Column(String, primary_key=True)
    content_piece_id = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)


class AgentResultTable(Base):
    __tablename__ = "agent_results"
    
    id = Column(String, primary_key=True)
    agent_type = Column(String, nullable=False)
    success = Column(Boolean, nullable=False)
    data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=False)
    content_piece_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
