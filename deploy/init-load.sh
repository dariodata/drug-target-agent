#!/bin/bash
set -e

echo "Init-loader: waiting for Neo4j to be ready..."

# Wait for Neo4j to accept connections (up to 60 seconds)
for i in $(seq 1 30); do
    if python -c "
from neo4j import GraphDatabase
import os
d = GraphDatabase.driver(
    os.environ.get('NEO4J_URI', 'bolt://neo4j:7687'),
    auth=(os.environ.get('NEO4J_USER', 'neo4j'), os.environ['NEO4J_PASSWORD'])
)
d.verify_connectivity()
d.close()
print('Connected.')
" 2>/dev/null; then
        break
    fi
    echo "  Attempt $i/30 - Neo4j not ready yet..."
    sleep 2
done

# Verify we actually connected
python -c "
from neo4j import GraphDatabase
import os
d = GraphDatabase.driver(
    os.environ.get('NEO4J_URI', 'bolt://neo4j:7687'),
    auth=(os.environ.get('NEO4J_USER', 'neo4j'), os.environ['NEO4J_PASSWORD'])
)
d.verify_connectivity()
d.close()
" || { echo "ERROR: Could not connect to Neo4j after 60s"; exit 1; }

# Check if database is empty
COUNT=$(python -c "
from neo4j import GraphDatabase
import os
d = GraphDatabase.driver(
    os.environ.get('NEO4J_URI', 'bolt://neo4j:7687'),
    auth=(os.environ.get('NEO4J_USER', 'neo4j'), os.environ['NEO4J_PASSWORD'])
)
with d.session() as s:
    r = s.run('MATCH (n) RETURN count(n) AS c')
    print(r.single()['c'])
d.close()
")

if [ "$COUNT" = "0" ]; then
    echo "Init-loader: database is empty, loading reports..."
    python -m src.neo4j_loader reports/
    echo "Init-loader: done."
else
    echo "Init-loader: database already has $COUNT nodes, skipping."
fi
