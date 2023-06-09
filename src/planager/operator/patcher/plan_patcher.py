from typing import Optional

from ...entity import Plan, PlanPatches
from ...util import ConfigType


class PlanPatcher:
    def __init__(self, config: Optional[ConfigType] = None) -> None:
        self._config = config

    def __call__(self, plan: Plan, plan_patches: Optional[PlanPatches]) -> Plan:
        if not plan_patches:
            return plan
        return plan  # TODO
