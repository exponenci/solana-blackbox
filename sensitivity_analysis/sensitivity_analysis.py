import os
from .experiment_container import SARunnerContainer


def pure_virtual_method():
    raise NotImplementedError("pure virtual method must be defined!")


class SensitivityAnalysisMAbstract:
    def __init__(self, *args, **kwargs) -> None:
        return

    def run(self, exp_container: SARunnerContainer, **kwargs):
        pure_virtual_method()
