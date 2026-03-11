"""ETL Pipeline Core."""
import logging
import time
from typing import Any, Callable, Iterable, List, Optional

from .interfaces import Extractor, Loader, Pipeline, Transformer

logger = logging.getLogger(__name__)


class ETLPipeline(Pipeline):
    """Composable ETL pipeline."""

    def __init__(self, extractor: Extractor, loader: Loader,
                 transformers: Optional[List[Transformer]] = None) -> None:
        self._extractor = extractor
        self._loader = loader
        self._transformers = transformers or []

    def add_transformer(self, transformer: Transformer) -> "ETLPipeline":
        self._transformers.append(transformer)
        return self

    def run(self) -> dict:
        start = time.time()
        extracted = 0
        transformed = 0
        loaded = 0
        failed = 0

        records = []
        for record in self._extractor.extract():
            extracted += 1
            current = record
            try:
                for transformer in self._transformers:
                    current = transformer.transform(current)
                records.append(current)
                transformed += 1
            except Exception as e:
                logger.error("Transform failed for record: %s", e)
                failed += 1

        try:
            loaded = self._loader.load(records)
        except Exception as e:
            logger.error("Load phase failed: %s", e)

        elapsed = time.time() - start
        stats = {
            "extracted": extracted,
            "transformed": transformed,
            "loaded": loaded,
            "failed": failed,
            "duration_seconds": round(elapsed, 3),
        }
        logger.info("ETL pipeline completed: %s", stats)
        return stats


class ListExtractor(Extractor):
    def __init__(self, data: List[Any]) -> None:
        self._data = data

    def extract(self) -> Iterable[Any]:
        return iter(self._data)


class ListLoader(Loader):
    def __init__(self) -> None:
        self.records: List[Any] = []

    def load(self, records: Iterable[Any]) -> int:
        self.records.extend(records)
        return len(self.records)


class FunctionTransformer(Transformer):
    def __init__(self, func: Callable[[Any], Any]) -> None:
        self._func = func

    def transform(self, record: Any) -> Any:
        return self._func(record)
