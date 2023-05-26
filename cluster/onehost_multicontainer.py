import os
import time
import threading
import subprocess

from cluster.cluster import Cluster


class OneHostMultiContainer(Cluster):
    def __init__(self, configfile_path, 
                genesis_host: str = 'compiledgenesis',
                network_name: str = 'chains-network',
                validator_count: int = 1,
                containers_exists: bool = True,
                remove_containers: bool = False) -> None:
        super().__init__()
        self.configfile_path = os.path.join(os.getenv('WORKDIR'), configfile_path)
        self.container_names = {
            "genesis": 'compiled-genesis',
            "validator": 'compiled-validator',
            "client": 'compiled-client',
        }
        self.genesis_host = genesis_host
        self.network_name = network_name
        self.validator_count = validator_count
        self.containers_exists = containers_exists
        self.remove_containers = remove_containers
    
    def start(self):
        if not self.containers_exists:
            self.setup_network()
            self.create_containers()
        self.start_containers()
        self.configure()
        self.start_cluster()

    def setup_network(self):
        subprocess.run(f"docker network create -d overlay --attachable {self.network_name}")

    def create_containers(self,
                          image_name: str = 'compiled_image',
                          host_logdir: str = '/mnt/solana/dev/logs'):
        subprocess.run(f"docker run \
                        --ulimit nofile=1000000:1000000 \
                        --name {self.container_names['genesis']} \
                        --network {self.network_name} \
                        -v {host_logdir}:/mnt/logs \
                        --hostname {self.genesis_host} \
                        -p 80:80 \
                        -p 8001:8001 \
                        -p 8899:8899 \
                        -p 9900:9900 \
                        -t -d {image_name}", shell=True)
        for i in range(self.validator_count):
            subprocess.run(f"docker run \
                            --ulimit nofile=1000000:1000000 \
                            --name {self.container_names['validator']}-{i} \
                            --network {self.network_name} \
                            -v {host_logdir}:/mnt/logs \
                            -t -d {image_name}", shell=True)
        subprocess.run(f"docker run \
                        --ulimit nofile=1000000:1000000 \
                        --name {self.container_names['client']} \
                        --network {self.network_name} \
                        -v {host_logdir}:/mnt/logs \
                        -t -d {image_name}", shell=True)

    def start_containers(self):
        subprocess.run(f"docker start {self.container_names['genesis']}", shell=True)
        for i in range(self.validator_count):
            subprocess.run(f"docker start {self.container_names['validator']}-{i}", shell=True)
        subprocess.run(f"docker start {self.container_names['client']}", shell=True)

    def configure(self):
        subprocess.run(f"docker cp {self.configfile_path} {self.container_names['genesis']}:/solana/config.toml",
                       shell=True)
        for i in range(self.validator_count):
            subprocess.run(f"docker cp {self.configfile_path} {self.container_names['validator']}-{i}:/solana/config.toml", 
                        shell=True)
        subprocess.run(f"docker cp {self.configfile_path} {self.container_names['client']}:/solana/config.toml", 
                       shell=True)

    def start_cluster(self):
        def start_thread(func):
            t = threading.Thread(target=func)
            t.start()
            self.threads.append(t)
        # run faucet
        genesis_name = self.container_names['genesis']
        validator_base_name = self.container_names['validator']
        
        subprocess.run(f"docker exec {genesis_name} bash -c './multinode-demo/setup.sh &'", 
                       shell=True)
        time.sleep(10)

        start_thread(
            lambda: subprocess.run(f"docker exec {genesis_name} \
                                   nohup bash -c './multinode-demo/faucet.sh &'", 
                                   shell=True)
        )
        time.sleep(10)
        
        # run bootstrap-validator
        start_thread(
            lambda: subprocess.run(f"docker exec {genesis_name} bash -c \
                                   './multinode-demo/bootstrap-validator.sh \
                                   --gossip-host {self.genesis_host} \
                                   --log /mnt/logs/genesis.txt'", 
                                   shell=True)
        )
        time.sleep(120)

        for i in range(self.validator_count):
            start_thread(
                lambda: subprocess.run(f"docker exec {validator_base_name}-{i} bash -c \
                                       './multinode-demo/validator.sh \
                                       --entrypoint {self.genesis_host}:8001 --rpc-port 8899 \
                                       --log /mnt/logs/validator.txt'", 
                                       shell=True)
            )

    def run_client(self, tx_count: int = 50, duration: int = 5, *args):
        subprocess.run(f"docker exec {self.container_names['client']} bash -c \
                       \"./multinode-demo/bench-tps.sh \
                       --tx_count {tx_count} --duration {duration} \
                       --entrypoint {self.genesis_host}:8001 --faucet {self.genesis_host}:9900 \
                       > /mnt/logs/clientout.txt 2>/mnt/logs/solana_client_stderr.txt\"", 
                       shell=True)

    def stop(self, *args):
        self.stop_containers()
        self.stop_cluster()
        if self.remove_containers:
            self.clear()

    def stop_containers(self):
        subprocess.run(f"docker stop {self.container_names['genesis']}", shell=True)
        for i in range(self.validator_count):
            subprocess.run(f"docker stop {self.container_names['validator']}-{i}", shell=True)
        subprocess.run(f"docker stop {self.container_names['client']}", shell=True)
        
    def stop_cluster(self):
        for t in self.threads:
            t.join()

    def clear(self):
        subprocess.run(f"docker rm {self.container_names['genesis']}", shell=True)
        for i in range(self.validator_count):
            subprocess.run(f"docker rm {self.container_names['validator']}-{i}", shell=True)
        subprocess.run(f"docker rm {self.container_names['client']}", shell=True)
