"""
Test MCP server for tabletop game rules and terminology search.

This module sets up an MCP (Model Context Protocol) server using FastMCP
to provide tools for searching game rules, terminology, and game data
using vector similarity search powered by ObjectBox and SentenceTransformers.
"""

from typing import Annotated

import yaml
from fastmcp import FastMCP
from objectbox import (
    Box,
    Entity,
    Float32Vector,
    HnswIndex,
    Id,
    Int16,
    Store,
    String,
)
from pydantic import Field
from sentence_transformers import SentenceTransformer


# ------------------------------------------------------------------
# ObjectBox entities
# ------------------------------------------------------------------
@Entity()
class Rule:
    id = Id  # Unique identifier for the rule
    internal_id = String  # Internal unique ID (e.g., from chunking process)
    content = String  # Full text content of the rule
    section = String  # Rulebook section (e.g., "movement", "combat")
    game = String  # Associated game name
    req_term = String  # YAML string of required terminology terms (list serialized)
    scenario = String  # Enriched searchable text: tags (#section, #type) + "---" + content; this is encoded for vector search
    priority = Int16  # Priority level for rule application
    zone = String  # Rule zone (base/advanced/edge)
    vector = Float32Vector(index=HnswIndex(dimensions=768))  # 768-dim vector embedding for similarity search (encoded from scenario field)


@Entity()
class Terminology:
    id = Id  # Unique identifier
    internal_id = String  # Internal unique ID
    content = String  # Enriched searchable text: tags (#group) + "---" + name; this is encoded for vector search
    name = String  # Display name of the term
    game = String  # Associated game name
    slug = String  # URL-friendly identifier
    kind = String  # Type: "TERM" for definitions, "ENTITY" for named entities
    path = String  # Path or location in the documentation
    group = String  # Category or group for the term
    definition = String  # Definition text
    extra = String  # YAML string of additional metadata
    vector = Float32Vector(index=HnswIndex(dimensions=768))  # 768-dim vector embedding for similarity search (encoded from content field)

@Entity()
class Game:
    id = Id  # Unique identifier
    name = String  # Game name in native script
    latin_name = String  # Game name in Latin script
    vector = Float32Vector(
        index=HnswIndex(dimensions=768)
    )  # 768-dim vector embedding for similarity search (encoded from name field)

# ------------------------------------------------------------------
# Global setup
# ------------------------------------------------------------------
COUNT_ITEMS = 3  # Number of nearest neighbors to retrieve in searches
server = FastMCP(name="rules-mcp")  # Initialize FastMCP server for MCP protocol
store = Store(directory="./db")  # Open ObjectBox database store in ./db directory
rules_box = Box(store, entity=Rule)  # Box for storing and querying Rule entities
terminology_box = Box(store, entity=Terminology)  # Box for storing Terminology entities
game_box = Box(store, entity=Game)  # Box for storing Game entities
model = SentenceTransformer("./model")  # Load pre-trained sentence transformer model for encoding text to vectors


# ------------------------------------------------------------------
# Tools – parameters described inline with Annotated[…, Field(…)]
# ------------------------------------------------------------------
@server.tool
def find_games(
    query: Annotated[str, Field(...)]
) -> str:
    """
    Search for games using vector similarity.

    Parameters
    ----------
    query : str
        Natural-language search query (can be empty).
    """
    vector = model.encode(query)

    obx_query = game_box.query(
        Game.vector.nearest_neighbor(vector, element_count=COUNT_ITEMS)
    ).build()

    results = []
    for id_, score in obx_query.find_ids_with_scores():
        g = game_box.get(id_)
        results.append(
            {
                "id": g.id,
                "name_db": g.name,
                "latin_name": g.latin_name,
                "score": score,
            }
        )

    return yaml.safe_dump(results, allow_unicode=True)


@server.tool
def get_toc(db_game_name: str) -> str:
    """
    Get table of contents for a specific game by listing all rule sections and scenarios.

    """
    rules_query = rules_box.query(
        Rule.game.equals(db_game_name)
    ).build()

    result = []
    for res in rules_query.find():
        result.append({
          "section":  res.section,
          "scenario": res.scenario
        })

    return yaml.safe_dump(result, allow_unicode=True)

@server.tool
def find_in_rulebook(
    db_game_name: Annotated[str, Field(...)],
    section: Annotated[str, Field(...)],
    type_: Annotated[str, Field(...)],
    query: Annotated[str, Field(...)],
    # zone: Annotated[Literal["base", "advanced", "edge"], Field(...)] = "base",
) -> str:
    """
    Search for rules in the rulebook using vector similarity.

    Parameters
    ----------
    db_game_name : str
        Name of the game (required).
    section : str
        Section of the rulebook;.
    type_ : str
        Entity type to search (rule/action/setup/components/etc).
    query : str
        Natural-language search query (can be empty).
    zone : {'base','advanced','edge'}
        Rule zone; defaults to 'base'.
    """
    # Construct enriched search query by adding metadata tags
    search_query = f"#section:{section} #type:{type_}\n---\n{query}"
    # Encode the search query to a vector for similarity search
    vector = model.encode(search_query)

    # Build ObjectBox query to find nearest neighbors, filtered by game name
    obx_query = rules_box.query(
        Rule.vector.nearest_neighbor(vector, element_count=COUNT_ITEMS)
        & Rule.game.equals(db_game_name)
    ).build()

    results = []
    for id_, score in obx_query.find_ids_with_scores():
        r = rules_box.get(id_)
        results.append(
            {
                "id": r.id,
                "content": r.content,
                "score": score,
                "section": r.section,
                "req_term": yaml.safe_load(r.req_term),
                "scenario": r.scenario,
            }
        )

    return yaml.safe_dump(results, allow_unicode=True)


@server.tool
def find_in_terminology(
    db_game_name: Annotated[str, Field(...)],
    group: Annotated[str, Field(...)] = "default",
    query: Annotated[str, Field(...)] = "",
) -> str:
    """
    Search for terminology entries (kind=TERM) using vector similarity.

    Parameters
    ----------
    game_name : str
        Name of the game (required).
    group : str
        Terminology group; defaults to 'default'.
    query : str
        Text query for semantic term search.
    """
    search_query = f"#game:{db_game_name} #group:{group}\n---\n{query}"
    vector = model.encode(search_query)

    obx_query = terminology_box.query(
        Terminology.vector.nearest_neighbor(vector, element_count=COUNT_ITEMS)
        & Terminology.kind.equals("TERM")
        & Terminology.game.equals(db_game_name)
    ).build()

    results = []
    for id_, score in obx_query.find_ids_with_scores():
        t = terminology_box.get(id_)
        results.append(
            {
                "id": t.internal_id,
                "score": score,
                "content": t.content,
                "name": t.name,
                "definition": t.definition,
                "extra": yaml.safe_load(t.extra),
            }
        )

    return yaml.safe_dump(results, allow_unicode=True)


@server.tool
def find_in_terminology_ner(
    db_game_name: Annotated[str, Field(...)],
    group: Annotated[str, Field(...)] = "default",
    query: Annotated[str, Field(...)] = "",
) -> str:
    """
    Search for entity-level terminology (kind=ENTITY) using vector similarity.

    Parameters
    ----------
    game_name : str
        Name of the game (required).
    group : str
        Terminology group; defaults to 'default'.
    query : str
        Text query for semantic term search.
    """
    search_query = f"#group:{group}\n---\n{query}"
    vector = model.encode(search_query)

    obx_query = terminology_box.query(
        Terminology.vector.nearest_neighbor(vector, element_count=COUNT_ITEMS)
        & Terminology.kind.equals("ENTITY")
        & Terminology.game.equals(db_game_name)
    ).build()

    results = []
    for id_, score in obx_query.find_ids_with_scores():
        t = terminology_box.get(id_)
        results.append(
            {
                "score": score,
                "content": t.content,
                "name": t.name,
                "group": t.group,
                "definition": t.definition,
                "extra": yaml.safe_load(t.extra),
            }
        )

    return yaml.safe_dump(results, allow_unicode=True)


# ------------------------------------------------------------------
# Run the MCP server
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Start the FastMCP server on HTTP interface at port 8001
    server.run("http", port=8001)
