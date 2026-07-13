from __future__ import annotations

from .services import ProductionOptimizationService


class OptimizationModel:
    """Compatibility adapter around the pure optimization service."""

    def __init__(self, params: dict):
        self.params = params
        self.service = ProductionOptimizationService()

    def solve(self) -> dict:
        return self.service.solve(self.params).as_legacy_dict()
