import os
import numpy as np

from cluster.singlecontainer_multinode import SingleContainerMultiNode

from blackbox_experiment import run_blackbox_experiment
from sensitivity_analysis_experiment import run_sensitivity_analysis_experiment
from optimization_experiment import run_optimization_experiment
import consts


def generate_run_info():
    cluster = SingleContainerMultiNode(consts.TARGET_CONFIG)
    # case #1: default config values
    run_blackbox_experiment(cluster,
                            params_ids=list(range(89)),
                            apply_func=lambda v: v,
                            runs_count=1)

    # case #2: random config values for first 63 params within [0.9v, 1.1v] segments for each v-values
    run_blackbox_experiment(cluster, 
                            params_ids=list(range(63)), 
                            apply_func=lambda v: np.random.uniform(0.9 * v, 1.1 * v),
                            runs_count=12)

    # case #3: random config values for first 66 params within [0.83v, 1.17v] segments for each v-values
    run_blackbox_experiment(cluster, 
                            params_ids=list(set(range(66)) - {11, 15, 47}), 
                            apply_func=lambda v: np.random.uniform(0.83 * v, 1.17 * v),
                            runs_count=8)


if __name__ == '__main__':
    os.environ["WORKDIR"] = consts.PROJECT_WORKDIR
    # run blackbox on random config to get some data for SA
    generate_run_info()
    # DEFAULT TPS: 21300.781
    
    # run SA on generated data and chose one of methods' result params_ids that we are going to optimize
    sa_results: dict = run_sensitivity_analysis_experiment()
    print("SA results...")
    for i, kv in enumerate(sa_results.items()):
        print(f"{i}. {kv[0]} method, params_ids={kv[1]}")
    sa_id = int(input("type 0 or 1 or 2 to chose what params_ids will be optimized"))
    params_ids = list(map(int, list(sa_results.values())[sa_id]))
    # RESULT PARAM IDS: [8, 31, 44, 51, 63]
    # PARAM NAMES: [RECV_BATCH_MAX_CPU, 
    #               CRDS_GOSSIP_PULL_MSG_TIMEOUT_MS, 
    #               SHRUNKEN_ACCOUNT_PER_SEC, 
    #               VOTE_THRESHOLD_SIZE,
    #               DEFAULT_TICKS_PER_SECOND]

    # optimize chosen params_ids
    cluster = SingleContainerMultiNode(consts.TARGET_CONFIG)
    run_optimization_experiment(cluster, params_ids)
    # RESULT X: [1.16363636e+03 5.23636364e+04 2.27272727e+02 7.27272764e-01 1.57090909e+02]
    # RESULT TPS: 24261.154

    # WIN RATE: 24261.154 / 21300.781 \approx 14%
