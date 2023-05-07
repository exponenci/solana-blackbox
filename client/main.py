from matlab_sensitivity_analysis import PCEMatlabM
from matlab_sensitivity_analysis import GPMatlabM
from matlab_sensitivity_analysis import PCGPMatlabM

import numpy as np


class DataReader:
    def __init__(self, directory, target=6, SAmethod=PCEMatlabM, datafiles_ids=range(1, 6)) -> None:
        self.directory = directory
        self.ids = datafiles_ids
        self.target = target
        self.SAmethod = SAmethod

    def run_all(self):
        print(f"[working with data in {self.directory}; {self.SAmethod.method_id}]")
        for id in self.ids:
            print(f"case #{id}:")
            self.run_case(id)

    ## TODO: 
    # - socket.close after analysis was finished 
    # - send 0 or 1 before target params to be sure error was not occured
    # - make sa_method x, y and target_param properties

    def run_case(self, id):
        x = np.loadtxt(f'{self.directory}/Xmatrix{id}.txt', dtype=np.float64, delimiter=',')
        y = np.loadtxt(f'{self.directory}/ymatrix{id}.txt', dtype=np.float64, delimiter=',')
        print(f"\tshape={x.shape}", end="\t")
        sa_method = self.SAmethod(x, y, target_params_count=self.target)
        res_params = sa_method.run(addr='192.168.96.3', port=9889)
        # if sa_method.error_occured: 
        print(f"best params to optimize={res_params}")
        sa_method.close_connection()


def main():
    DataReader('testdata', target=1).run_all()
    # DataReader('small_runs_testdata', target=6).run_all()

if __name__ == '__main__':
    main()