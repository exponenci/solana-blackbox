import os
from .experiment_container import ExperimentContainer


def pure_virtual_method():
    raise NotImplementedError("pure virtual method must be defined!")


class SensitivityAnalysisMAbstract:
    # get this static values by env

    ## new instance - configurator
    # methods_mapping: dict = dict() # static: mapping methods_ids with their names/other info
    # logging: bool = True

    def __init__(self, *args, **kwargs) -> None:
        return

    def run(self, exp_container: ExperimentContainer, **kwargs):
        pure_virtual_method()
