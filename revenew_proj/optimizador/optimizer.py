from __future__ import annotations

from collections.abc import Mapping

from .services import ProductionOptimizationService, ProductionParameters


class OptimizationModel:
    """Compatibility adapter around the pure optimization service."""

    def __init__(self, params: ProductionParameters | Mapping[str, object]):
        self.params = params
        self.service = ProductionOptimizationService()

    def solve(self) -> dict:
        return self.service.solve(self.params).as_legacy_dict()
