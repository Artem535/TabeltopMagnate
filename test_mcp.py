import yaml
from fastmcp import FastMCP
from objectbox import (
    Box,
    Entity,
    Float32Vector,
    HnswIndex,
    Id,
    Store,
    String,
    VectorDistanceType,
)
from sentence_transformers import SentenceTransformer


@Entity()
class Rule:
    id = Id
    internal_id = String
    content = String
    section = String
    game = String
    vector = Float32Vector(
        index=HnswIndex(dimensions=768, distance_type=VectorDistanceType.EUCLIDEAN)
    )


@Entity()
class Terminology:
    id = Id
    internal_id = String
    content = String
    name = String
    slug = String
    kind = String
    path = String
    group = String
    definition = String
    extra = String
    vector = Float32Vector(index=HnswIndex(dimensions=768))


COUNT_ITEMS = 5
server = FastMCP(name="test")
store = Store(directory="./db")
rules_box = Box(store, entity=Rule)
terminology_box = Box(store, entity=Terminology)
model = SentenceTransformer("./model")


@server.tool
def find_in_rulebook(game_name: str, section: str, type_: str, query: str) -> str:
    """
    Search for a rule in the rulebook. By using the vector search.
    """
    search_query = f"#game:{game_name} #section:{section} #type:{type_}\n---\n{query}"
    vector = model.encode(search_query)
    obx_query = rules_box.query(
        Rule.vector.nearest_neighbor(vector, element_count=COUNT_ITEMS)
    ).build()
    result = obx_query.find_ids_with_scores()
    result_list = []
    for id_, score in result:
        obj = rules_box.get(id_)
        result_list.append(
            {
                "id": obj.id,
                "content": obj.content,
                "score": score,
                "game": obj.game,
                "section": obj.section,
            }
        )

    return yaml.safe_dump(result_list, allow_unicode=True)


@server.tool
def find_in_terminology(game_name: str, group: str, query: str) -> str:
    """
    Search for a term in the terminology. By using the vector search.
    """
    search_query = f"#game:{game_name} #group:{group}\n---\n{query}"
    vector = model.encode(search_query)
    obx_query = terminology_box.query(
        Terminology.vector.nearest_neighbor(vector, element_count=COUNT_ITEMS) &
        Terminology.kind.equals("TERM")
    ).build()
    obx_result = obx_query.find_ids_with_scores()
    
    result = []
    for id_, score in obx_result:
        obj: Terminology = terminology_box.get(id_)
        result.append({
            "id": obj.internal_id,
            "score": score,
            "content": obj.content,
            "name": obj.name,
            "group": obj.group,
            "definition": obj.definition,
            "extra": yaml.safe_load(obj.extra),
            "kind": obj.kind,
        })

    return yaml.safe_dump(result, allow_unicode=True)


@server.tool
def find_in_terminology_ner(game_name: str, group: str, query: str) -> str:
    """
    Search for a term in the terminology. By using the vector search.
    """
    search_query = f"#game:{game_name} #group:{group}\n---\n{query}"
    vector = model.encode(search_query)
    obx_query = terminology_box.query(
        Terminology.vector.nearest_neighbor(vector, element_count=COUNT_ITEMS)
        & Terminology.kind.equals("ENTITY")
    ).build()
    obx_result = obx_query.find_ids_with_scores()

    result = []
    for id_, score in obx_result:
        obj: Terminology = terminology_box.get(id_)
        result.append(
            {
                "id": obj.internal_id,
                "score": score,
                "content": obj.content,
                "name": obj.name,
                "group": obj.group,
                "definition": obj.definition,
                "extra": yaml.safe_load(obj.extra),
                "kind": obj.kind,
            }
        )

    return yaml.safe_dump(result, allow_unicode=True)


if __name__ == "__main__":
    server.run("http", port=8000)
