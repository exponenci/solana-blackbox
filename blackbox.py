from cluster.singlecontainer_multinode import SingleContainerMultiNode
from utils.config_generator import TomlConfig
from utils.parse_bench_output import parse_from_file


def blackbox(cluster, clear_cluster: bool = False):
    cluster.configure()
    
    cluster.start()
    
    cluster.run_client()
    results = parse_from_file('/mnt/solana/dev/logs/solana_client_stderr.txt')
    # cluster.stop()
    if clear_cluster:
        cluster.clear()
    return results


if __name__ == '__main__':
    import threading
    import time
    import os

    os.environ["WORKDIR"] = "/home/exponenci/course-work/project/"
    target_config: str = 'upd_config.toml'
    config = TomlConfig(updated_filename=target_config)

    # update config as you wish
    config.set({
        # "NUM_THREADS": 6,
        # "DEFAULT_TICKS_PER_SLOT": 1020,
        # "ITER_BATCH_SIZE": 500,
        # "RECV_BATCH_MAX_CPU": 21,
        # "DEFAULT_HASHES_PER_SECOND": 34343434334,
        # "DEFAULT_TICKS_PER_SECOND": 790,
    })
    config.save() # saves to upd_config.toml
    
    cluster = SingleContainerMultiNode(target_config, container_setting={'container-name': 'genesis-container', 'create': False})

    results = blackbox(cluster)
    print('average_tps: ', results[0], '; droprate: ', results[1])
