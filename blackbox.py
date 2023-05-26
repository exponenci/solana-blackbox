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

    cluster.start_containers()
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
    cluster.run_client(tx_count=100000, duration=90, logfile=bench_res_log_file)
    print("BENCHMARK DONE. READING RESULTS")
    results = parse_from_file('/mnt/solana/dev/logs/solana_client_stderr.txt')
    print("RESULTS", results)

    cluster.stop_containers()
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

    # cluster = SingleContainerMultiNode('config.toml')
    # config = TomlConfig()
    # print('blackbox default starting')
    # print('param names: ', ','.join(config.get_all_keys()))
    # params = config.get_values_list()
    # tps, droprate = blackbox(cluster)
    # with open('result.csv', 'a') as file:
    #     line = params
    #     line.append(tps)
    #     line.append(droprate)
    #     file.write(','.join(map(str, line)) + '\n')
    # print('blackbox default finished', (tps, droprate))
    # print('=' * 120)

    cluster = SingleContainerMultiNode(TARGET_CONFIG)
    limited_blackbox = limit_params(blackbox, cluster, list(range(63)))
    for i in range(12):
        print(f'blackbox +-10% #{i} starting')
        params, res = limited_blackbox(apply_func=lambda v: np.random.uniform(0.9 * v, 1.1 * v))
        tps, droprate = res
        with open('result.csv', 'a') as file:
            line = params
            line.append(tps)
            line.append(droprate)
            file.write(','.join(map(str, line)) + '\n')
        print(f'blackbox +-10% #{i} finished', res)
        print('=' * 120)


    # cluster = SingleContainerMultiNode(TARGET_CONFIG)
    # limited_blackbox = limit_params(blackbox, cluster, list(set(range(66)) - {11, 15, 47} ))
    # for i in range(8):
    #     print(f'blackbox +-17% #{i} starting')
    #     params, res = limited_blackbox(apply_func=lambda k, v: np.random.uniform(0.83 * v, 1.17 * v))
    #     tps, droprate = res
    #     with open('result.csv', 'a') as file:
    #         line = params
    #         line.append(tps)
    #         line.append(droprate)
    #         file.write(','.join(map(str, line)) + '\n')
    #     print(f'blackbox +-17% #{i} finished', res)
    #     print('=' * 120)
