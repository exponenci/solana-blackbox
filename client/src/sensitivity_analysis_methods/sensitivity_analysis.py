import os


def pure_virtual_method():
    raise NotImplementedError("pure virtual method must be defined!")


class SensitivityAnalysisMAbstract:
    # get this static values by env

    ## new instance - configurator
    methods_mapping: dict = dict() # static: mapping methods_ids with their names/other info
    logging: bool = True
    result_file: str = 'result.csv'

    def __init__(self, *args, **kwargs) -> None:
        if len(args) == 2:
            self.x, self.y = args
        else:
            self.x = kwargs.get('x')
            self.y = kwargs.get('y')
        self.target_params_count = kwargs.get('target_params_count')
        return self

    def accept_run_data(self, x, y, target_params_count=None) -> None:
        if target_params_count is None:
            target_params_count = os.getenv('EXP_TARGET_PARAMS_COUNT')
        self.x = x
        self.y = y
        if target_params_count is not None:
            self.target_params_count = target_params_count

    def run(self, x=None, y=None, **kwargs):
        pure_virtual_method()


