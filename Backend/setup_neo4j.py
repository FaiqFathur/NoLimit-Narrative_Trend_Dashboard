import os
from neo4j import GraphDatabase

# Configure these from environment variables or use defaults
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", ""))

# By default, we disabled auth in docker-compose.yml for local development
if not AUTH[1]:
    AUTH = None 

def setup_constraints(driver):
    queries = [
        "CREATE CONSTRAINT post_id_unique IF NOT EXISTS FOR (p:Post) REQUIRE p.id IS UNIQUE",
        "CREATE CONSTRAINT topic_id_unique IF NOT EXISTS FOR (t:Topic) REQUIRE t.id IS UNIQUE",
        "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE"
    ]
    
    with driver.session() as session:
        for query in queries:
            try:
                session.run(query)
                print(f"Successfully executed: {query}")
            except Exception as e:
                print(f"Error executing '{query}': {e}")
                raise

if __name__ == "__main__":
    driver = GraphDatabase.driver(URI, auth=AUTH)
    try:
        driver.verify_connectivity()
        print("Connected to Neo4J.")
        setup_constraints(driver)
        print("Neo4J setup completed successfully.")
    except Exception as e:
        print(f"Failed to connect or setup Neo4J: {e}")
    finally:
        driver.close()
