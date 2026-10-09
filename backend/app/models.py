"""
models.py — SQLAlchemy ORM definitions for CodeCompass.

Defines the database schema mapping for persisting project metadata and 
associated static analysis findings.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Project(Base):
    """
    ORM model representing a scanned codebase project.
    Stores aggregated metadata and the overall Code Readiness Score (CRS).
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    crs_score = Column(Integer, default=100)
    total_files = Column(Integer, default=0)
    total_lines = Column(Integer, default=0)
    total_functions = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    #Relationships
    issues = relationship("AuditIssue", back_populates="project")

class AuditIssue(Base):
    """
    ORM model representing a specific anti-pattern or vulnerability finding.
    Linked to a parent Project via a foreign key constraint.
    """
    __tablename__ = "audit_issues"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    rule_name = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    line_number = Column(Integer, nullable=False)
    viva_tip = Column(Text, nullable=False)

    project = relationship("Project", back_populates="issues")