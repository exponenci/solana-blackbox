from src.sensitivity_analysis.matlab_sensitivity_analysis import PCEMatlabM
# from matlab_sensitivity_analysis import GPMatlabM
# from matlab_sensitivity_analysis import PCGPMatlabM

from src.sensitivity_analysis.experiment_container import ExperimentContainer


import numpy as np


class DataReader:
    def __init__(self, directory, target=6, SAmethod=PCEMatlabM, datafiles_ids=range(1, 6)) -> None:
        self.directory = directory
        self.ids = datafiles_ids
        self.target = target
        self.SAmethod = SAmethod

    def run_all(self):
        print(f"[working with data in {self.directory};]") # self.SAmethod.method_id
        for id in self.ids:
            print(f"case #{id}:")
            self.run_case(id)

    def run_case(self, id):
        exp = ExperimentContainer().read_from_files(f'{self.directory}/Xmatrix{id}.txt', f'{self.directory}/ymatrix{id}.txt')
        exp = self.SAmethod().run(exp, addr='10.193.88.211', port=9889)
        if exp.is_error:
            print(exp.result)
        else: 
            print(f"best params to optimize={exp.result}")


def main():
    DataReader('tests/data', target=1).run_all()
    # DataReader('small_runs_testdata', target=6).run_all()

if __name__ == '__main__':
    main()