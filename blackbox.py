from cluster.singlecontainer_multinode import SingleContainerMultiNode
from utils.config_generator import TomlConfig
from utils.parse_bench_output import parse_from_file

import threading
import time
import os
import numpy as np


CLEAR_CLUSTER = False
TARGET_CONFIG = 'upd_config.toml'
WORKDIR_PROJECT = "/home/exponenci/course-work/project/"


def blackbox(cluster):

    print("STARTING CONFIGURATION PROCESS")
    cluster.configure()
    print("CLUSTER CONFIGURED")
    
    print("STARTING CLUSTER")
    cluster.start_cluster(write_logs=False)
    print("CLUSTER BUILD. WAIT FOR CONVERGENCE")
    time.sleep(100)    
    print("NODES CONVERGED")

    print("RUNNING BENCHMARK")
    bench_res_log_file = '/mnt/logs/solana_client_stderr.txt'
    cluster.run_client(logfile=bench_res_log_file)
    print("BENCHMARK DONE. READING RESULTS")
    results = parse_from_file('/mnt/solana/dev/logs/solana_client_stderr.txt')
    print("RESULTS", results)

    cluster.stop_cluster()

    return results


def limit_params(func, cluster, params_ids):
    def wrapper(param_values=None, apply_func=None):
        config = TomlConfig(updated_filename=TARGET_CONFIG)
        if param_values is not None:
            config.set_ids_values(params_ids, param_values)
        elif apply_func is not None:
            config.map_ids_values(params_ids, apply_func)
        else:
            raise RuntimeError("file `config.toml` must be set")
        
        results = func(cluster)
        return config.get_values_list_updated(), results
    return wrapper


# def test_cluter():
#     cluter = SingleContainerMultiNode(TARGET_CONFIG)
#     cluter.start_container()
#     limited_blackbox = limit_params(blackbox, cluster, result_csv, list(range(63)))
#     for _ in range(5):
#         limited_blackbox(apply_func=lambda k, v: np.random.uniform(0.9 * v, 1.1 * v))

#     sa_methods = list(SensitivityAnalisis)
#     sa_results = list()
#     with open(result_csv) as f:
#         x, y = f
#         for sa_method in sa_methods:
#             sa_results.append(sa_method.run(x, y))

#     with open(sa_results) as f:
#         f.write(sa_results)


if __name__ == '__main__':
    os.environ["WORKDIR"] = "/home/exponenci/course-work/project/"

    cluster = SingleContainerMultiNode(TARGET_CONFIG)
    limited_blackbox = limit_params(blackbox, cluster, list(range(63)))
    for i in range(1):
        print(f'blackbox #{i} starting')
        params, res = limited_blackbox(apply_func=lambda k, v: np.random.uniform(0.9 * v, 1.1 * v))
        tps, droprate = res
        with open('result.csv', 'a') as file:
            line = params
            line.append(tps)
            line.append(droprate)
            file.write(','.join(map(str, line)) + '\n')
        print(f'blackbox #{i} finished', res)
        print(f'=' * 120)

    # config = TomlConfig(updated_filename=TARGET_CONFIG)
    # for i in range(1):
    #     config.apply(lambda k, v: np.random.uniform(0.9 * v, 1.1 * v))
        # # updated_config = TomlConfig(TARGET_CONFIG)
        # # result = blackbox(updated_config.get_values_list())
        # config.save()
        # result = blackbox(config.get_values_list())
        # results = blackbox(config.get_values_list())

    # update config as you wish
    # config.set({
    #     # "NUM_THREADS": 6,
    #     # "DEFAULT_TICKS_PER_SLOT": 1020,
    #     # "ITER_BATCH_SIZE": 500,
    #     # "RECV_BATCH_MAX_CPU": 21,
    #     # "DEFAULT_HASHES_PER_SECOND": 34343434334,
    #     # "DEFAULT_TICKS_PER_SECOND": 790,
    # })
    # config.save() # saves to upd_config.toml
    
    # cluster = SingleContainerMultiNode(target_config, container_setting={'container-name': 'genesis-container', 'create': False})

    # results = blackbox(cluster)
    # print('average_tps: ', results[0], '; droprate: ', results[1])
