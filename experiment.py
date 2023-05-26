import numpy as np
from numpy import genfromtxt

from sensitivity_analysis.matlab_sensitivity_analysis import PCEMatlabM, GPMatlabM, PCGPMatlabM
from sensitivity_analysis.experiment_container import ExperimentContainer


methods = {
    'PCEMatlabM': PCEMatlabM(addr='10.193.91.250', port=9889),
    'GPMatlabM': GPMatlabM(addr='10.193.91.250', port=9889),
    'PCGPMatlabM': PCGPMatlabM(addr='10.193.91.250', port=9889),
}

to_scale = True

data = genfromtxt('result.csv', delimiter=',', skip_header=1, dtype=np.float64)
for name, method in methods.items():
    print('\n\nMethod:', name)
    default_x = data[0, :66].copy()
    default_y = data[0, -2].reshape((-1)).copy() # here we make SA only on TPS (without droprate)

    if to_scale:
        x = data[:, :66].copy() / (default_x * 2) # масштабируем kx -> k/2, где k: 0 < k < 2 # p.s. E[k] = 1
        y = data[:, -2].reshape((-1)).copy() / 10000
    else:
        x = data[:, :66].copy()
        y = data[:, -2].reshape((-1)).copy()
    exp_container = ExperimentContainer(x_mat=x, y_vec=y)
    exp_container.target_params_count = 6
    exp_container = method.run(exp_container)
    if exp_container.is_error:
        print("RESULT:\t", exp_container.result)
    else: 
        print(f"best params to optimize={exp_container.result}")

# chosed params to optimize: 31, 63, 51, 8, 44
# var2: 63.0, 37.0, 48.0, 42.0, 53.0, 32.0
# var3: 4.0, 11.0, 13.0, 28.0, 20.0, 14.0