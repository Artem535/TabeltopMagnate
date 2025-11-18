from fastmcp import FastMCP
from sentence_transformers import SentenceTransformer
from objectbox import (
    Store,
    Box,
    Entity,
    Id,
    String,
    Float32Vector,
    HnswIndex,
    VectorDistanceType,
)
import yaml

@Entity()
class Rule:
    id = Id
    entity_id = String
    content = String
    section = String
    subsection = String
    game = String
    vector = Float32Vector(index=HnswIndex(dimensions=768))


server = FastMCP(name="test")
store = Store(directory="./db/objectbox")
rules_box = Box(store, entity=Rule)
model = SentenceTransformer("./model")

@server.tool
def find_in_rulebook(query: str) -> str:
    """
    Search for a rule in the rulebook. By using the vector search.
    """
    vector = model.encode(query)
    obx_query = rules_box.query(Rule.vector.nearest_neighbor(vector, element_count=2)).build()
    result = obx_query.find_ids_with_scores()
    result_list = []
    for id_, score in result:
        obj = rules_box.get(id_)
        result_list.append({
            "id": obj.id,
            "content": obj.content,
            "score": score,
            "game": obj.game,
            "section": obj.section,
            "subsection": obj.subsection
        })

    return yaml.safe_dump(result_list, allow_unicode=True)

if __name__ == "__main__":
    server.run("http", port=8000)
