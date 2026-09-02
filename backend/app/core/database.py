from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from neo4j import GraphDatabase

# PostgreSQL Engine
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Neo4J Driver
neo4j_auth = (settings.NEO4J_USER, settings.NEO4J_PASSWORD) if settings.NEO4J_PASSWORD else None
neo4j_driver = GraphDatabase.driver(settings.NEO4J_URI, auth=neo4j_auth)
