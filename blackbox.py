import time

from utils.config_generator import TomlConfig
from utils.parse_bench_output import parse_from_file
import consts


def blackbox(cluster):
    print("STARTING CLUSTER")
    cluster.start()

    print("CLUSTER IS STARTED. WAITING FOR VALIDATORS CONVERGENCE")
    time.sleep(consts.BLOCKCHAIN_CONVERGENCE_TIME_IN_SEC)    

    print("VALIDATORS CONVERGED. RUNNING BENCHMARK")
    cluster.run_client(tx_count=consts.CLIENT_TX_COUNT, 
                       duration=consts.CLIENT_DURATION, 
                       logfile=consts.CONTAINER_LOGDIR_MOUNT + consts.CLIENT_LOGFILE)

    results = parse_from_file(consts.HOST_LOGDIR_MOUNT + consts.CLIENT_LOGFILE)
    print("BENCHMARK DONE. RESULTS", results)

    cluster.stop()
    return results


def limit_params(func, cluster, params_ids):
    def wrapper(param_values=None, 
                apply_func=None):
        config = TomlConfig(base_filename=consts.BASE_CONFIG,
                            updated_filename=consts.TARGET_CONFIG)
        
        if param_values is not None:
            config.set_ids_values(params_ids, param_values)
        elif apply_func is not None:
            config.map_ids_values(params_ids, apply_func)
        else:
            raise RuntimeError(f"file {consts.BASE_CONFIG} must be set")
        
        results = func(cluster)
        params = config.get_values_list_updated()

        if consts.SAVE_CLUSTER_RUN_INFO:
            with open(consts.CLUSTER_RUN_INFO_FILE, 'a') as file:
                line = params
                line.append(results[0])
                line.append(results[1])
                file.write(','.join(map(str, line)) + '\n')

        return params, results
    return wrapper
