"""ETL Pipeline Tests."""
import pytest
from ..core import ETLPipeline, ListExtractor, ListLoader, FunctionTransformer


def test_basic_etl():
    extractor = ListExtractor([1, 2, 3, 4, 5])
    loader = ListLoader()
    pipeline = ETLPipeline(extractor, loader)
    pipeline.add_transformer(FunctionTransformer(lambda x: x * 2))
    stats = pipeline.run()
    assert stats["extracted"] == 5
    assert stats["transformed"] == 5
    assert loader.records == [2, 4, 6, 8, 10]


def test_etl_with_transform_failure():
    def bad_transform(x):
        if x == 3:
            raise ValueError("bad record")
        return x
    extractor = ListExtractor([1, 2, 3, 4])
    loader = ListLoader()
    pipeline = ETLPipeline(extractor, loader, [FunctionTransformer(bad_transform)])
    stats = pipeline.run()
    assert stats["failed"] == 1
    assert stats["transformed"] == 3


def test_etl_stats():
    extractor = ListExtractor(list(range(10)))
    loader = ListLoader()
    pipeline = ETLPipeline(extractor, loader)
    stats = pipeline.run()
    assert stats["extracted"] == 10
    assert "duration_seconds" in stats
