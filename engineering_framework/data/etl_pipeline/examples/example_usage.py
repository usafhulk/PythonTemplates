"""ETL Pipeline Example."""
from engineering_framework.data.etl_pipeline.core import (
    ETLPipeline, ListExtractor, ListLoader, FunctionTransformer
)

raw_data = [
    {"name": "  Alice  ", "age": "30"},
    {"name": "  Bob  ", "age": "25"},
]

extractor = ListExtractor(raw_data)
loader = ListLoader()
pipeline = ETLPipeline(extractor, loader)
pipeline.add_transformer(FunctionTransformer(lambda r: {
    "name": r["name"].strip(),
    "age": int(r["age"])
}))

stats = pipeline.run()
print(f"Stats: {stats}")
print(f"Loaded: {loader.records}")
