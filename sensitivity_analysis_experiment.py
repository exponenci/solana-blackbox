import numpy as np

from sensitivity_analysis.experiment_container import SARunnerContainer
import consts


def run_sensitivity_analysis_experiment(data_csvfile: str = consts.CLUSTER_RUN_INFO_FILE, 
                                        target_param_count: int = consts.SENSITIVITY_ANALYSIS_TARGET_PARAM_COUNT,
                                        params_ids: list = consts.EXPERIMENT_PARAM_IDS, 
                                        scale_params: bool = True,
                                        csv_kwargs: dict = {'delimiter': ',', 'skip_header': 1}) -> dict:
    data = np.genfromtxt(data_csvfile, dtype=np.float64, **csv_kwargs)
    results = dict()
    for method_name, method_runner in consts.SENSITIVITY_ANALYSIS_METHODS.items():
        print(f'Running {method_name} method...')
        if scale_params:
            default_x = data[0, params_ids].copy()
            x = data[:, params_ids].copy() / (default_x * 2) # масштабируем kx -> k/2, где k: 0 < k < 2 # p.s. E[k] = 1
            y = data[:, -2].reshape((-1)).copy() / 10000 # в силу специфики данных про tps имеет смысл отмасштабировать и их 
        else:
            x = data[:, params_ids].copy()
            y = data[:, -2].reshape((-1)).copy()
        exp_container = SARunnerContainer(x_mat=x, 
                                          y_vec=y, 
                                          target_params_count=target_param_count)
        exp_container = method_runner.run(exp_container)
        if exp_container.is_error:
            print(f"error info:  {exp_container.result}\n")
        else: 
            print(f"best params: {exp_container.result}\n")
        results[method_name] = exp_container.result
    return results
