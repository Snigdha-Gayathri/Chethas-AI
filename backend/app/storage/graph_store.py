from __future__ import annotations

from typing import Dict, Any, List, Optional, Union
from neo4j import AsyncGraphDatabase, AsyncDriver
from app.config import get_settings

class GraphStore:
    """Wrapper for Neo4j Graph Database."""

    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        """Initialize Neo4j driver lazily — connection is not verified until first use."""
        settings = get_settings()
        self._uri = uri or settings.neo4j_uri
        self._user = user or settings.neo4j_user
        self._pwd = password or settings.neo4j_password
        self._driver: Optional[AsyncDriver] = None

    @property
    def driver(self) -> AsyncDriver:
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(self._uri, auth=(self._user, self._pwd))
        return self._driver

    async def initialize(self) -> None:
        """Create indexes and constraints."""
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
        ]
        try:
            async with self.driver.session() as session:
                for q in queries:
                    await session.run(q)
        except Exception:
            pass

    async def add_entity(self, entity_type: str, properties: Dict[str, Any]) -> str:
        """Create or merge an entity node."""
        if "id" not in properties:
            import uuid
            properties["id"] = str(uuid.uuid4())
            
        cypher = f"""
        MERGE (n:{entity_type} {{id: $id}})
        SET n += $properties
        RETURN n.id AS id
        """
        async with self.driver.session() as session:
            result = await session.run(cypher, id=properties["id"], properties=properties)
            record = await result.single()
            return record["id"]

    async def add_relationship(self, from_id: str, to_id: str, rel_type: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Create a relationship between entities."""
        props = properties or {}
        cypher = f"""
        MATCH (a {{id: $from_id}}), (b {{id: $to_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += $properties
        """
        async with self.driver.session() as session:
            await session.run(cypher, from_id=from_id, to_id=to_id, properties=props)

    async def query(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query."""
        try:
            async with self.driver.session() as session:
                result = await session.run(cypher, parameters=params or {})
                records = await result.data()
                return records
        except Exception:
            return []

    async def get_neighbors(self, entity_id: str, depth: int = 1) -> Dict[str, Any]:
        """Get entity and its neighbors up to given depth."""
        cypher = """
        MATCH path = (n {id: $entity_id})-[*1..$depth]-(m)
        RETURN path
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(cypher, entity_id=entity_id, depth=depth)
                records = await result.data()
                return {"entity_id": entity_id, "neighbors": records}
        except Exception:
            return {"entity_id": entity_id, "neighbors": []}

    async def search_entities(self, entity_type_or_query: Union[str, Optional[str]], properties: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search entities by type/properties or by a general text query string."""
        if properties is None and isinstance(entity_type_or_query, str):
            # General text query search across node properties
            cypher = """
            MATCH (n)
            WHERE any(prop in keys(n) WHERE toLower(toString(n[prop])) CONTAINS toLower($q))
            RETURN n LIMIT 10
            """
            try:
                async with self.driver.session() as session:
                    result = await session.run(cypher, q=entity_type_or_query)
                    records = await result.data()
                    return [record["n"] for record in records]
            except Exception:
                return []

        entity_type = entity_type_or_query
        props = properties or {}
        label = f":{entity_type}" if entity_type else ""
        
        where_clauses = []
        for k in props.keys():
            where_clauses.append(f"n.{k} = ${k}")
            
        where_stmt = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        cypher = f"""
        MATCH (n{label})
        {where_stmt}
        RETURN n
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(cypher, **props)
                records = await result.data()
                return [record["n"] for record in records]
        except Exception:
            return []

    async def close(self) -> None:
        """Close the driver if it was initialized."""
        if self._driver is not None:
            try:
                await self._driver.close()
            except Exception:
                pass
            self._driver = None

