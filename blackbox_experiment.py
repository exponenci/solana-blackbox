from blackbox import blackbox, limit_params
import consts


def run_blackbox_experiment(cluster=None,
                            narrowed_blackbox=None,
                            apply_func=None,
                            params_ids: list = consts.EXPERIMENT_PARAM_IDS,
                            runs_count: int = 5):
    if apply_func is None:
        raise AttributeError("apply_func must be given to create random values for config params")
    if cluster is not None:
        narrowed_blackbox = limit_params(blackbox, cluster, params_ids)
    elif narrowed_blackbox is None:
        raise AttributeError("either cluster or narrowed_blackbox must be given in arguments")
    print("Starting experiments on configs generated via apply_func...")
    results = list()
    for i in range(runs_count):
        print(f"\nRunning cluster #{i}")
        params, res = narrowed_blackbox(apply_func=apply_func)
        results.append(params, res)
        print(f"Cluster run #{i} is finished\nTps={res[0]}, Droprate={res[1]}")
        print("=" * 120)
    print("\nExperiments are finished")
