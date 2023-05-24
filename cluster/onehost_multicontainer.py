import os
import subprocess
import time

from cluster.cluster import Cluster
import threading

# Host - single/multiple
# Container - single/multiple
# Testnet - singel/multiple

# host single & single container & single testnet -> raw docker (done)
# host single & single container & multi testnet -> raw docker (done)
# host single & multi container & multi testnet -> raw docker (done) | swarm | k8s
# host multiple & multi container & multi testnet -> docker swarm | k8s | terraform

class OneHostMultiContainer(Cluster):
    def __init__(self, configfile_path, 
                base_image: str = 'compiled_image', 
                genesis_host: str = 'compiledgenesis',
                logdir: str = '/mnt/solana/dev/logs', 
                network_name: str = 'chains-network',
                validator_count: int = 1) -> None:
        super().__init__()
        self.work_dir = os.getenv('WORKDIR')
        self.configfile_path = os.path.join(self.work_dir, configfile_path)
        self.base_image = base_image
        self.container_settings = {
            "genesis": {'container-name': 'compiled-genesis', 'create': True},
            "validator": {'container-name': 'compiled-validator', 'create': True},
            "client": {'container-name': 'compiled-client', 'create': False},
        }
        self.genesis_host = genesis_host
        self.logdir = logdir
        self.network_name = network_name
        self.validator_count = validator_count

    def configure(self, create_network: bool = False, container_settings: dict = dict(), *args, **kwargs):

        # subprocess.run(f"docker run --ulimit nofile=1000000:1000000 --name tmp_container {self.base_image}", shell=True)
        # subprocess.run(f"docker cp {self.configfile_path} tmp_container:/solana/config.toml", shell=True)
        # subprocess.run(f"docker stop tmp_container", shell=True)
        # subprocess.run(f"docker commit tmp_container {self.configured_image}", shell=True)
        # subprocess.run(f"docker container rm tmp_container", shell=True)

        if len(container_settings) == 3:
            self.container_settings = container_settings

        if create_network:
            subprocess.run(f"docker network create -d overlay --attachable {self.network_name}")

        genesis_name = self.container_settings['genesis']['container-name']
        validator_base_name = self.container_settings['validator']['container-name']
        client_name = self.container_settings['client']['container-name']
        if self.container_settings['genesis']['create']:
            subprocess.run(f"docker run \
                            --ulimit nofile=1000000:1000000 \
                            --name {genesis_name} \
                            --network {self.network_name} \
                            -v {self.logdir}:/mnt/logs \
                            --hostname {self.genesis_host} \
                            -p 80:80 \
                            -p 8001:8001 \
                            -p 8899:8899 \
                            -p 9900:9900 \
                            -t -d {self.base_image}", shell=True)
        else:
            subprocess.run(f"docker start {genesis_name}", shell=True)
        if self.container_settings['validator']['create']:
            subprocess.run(f"docker run \
                            --ulimit nofile=1000000:1000000 \
                            --name {validator_base_name} \
                            --network {self.network_name} \
                            -v {self.logdir}:/mnt/logs \
                            -t -d {self.base_image}", shell=True)

            # for i in range(self.validator_count):
            #     subprocess.run(f"docker run \
            #                     --ulimit nofile=1000000:1000000 \
            #                     --name {validator_base_name}-{i} \
            #                     --network {self.network_name} \
            #                     -v {self.logdir}:/mnt/logs \
            #                     -t -d {self.base_image}", shell=True)
        else:
            subprocess.run(f"docker start {validator_base_name}", shell=True)
            # for i in range(self.validator_count):
            #     subprocess.run(f"docker start {validator_base_name}-{i}", shell=True)
        if self.container_settings['client']['create']:
            subprocess.run(f"docker run \
                            --ulimit nofile=1000000:1000000 \
                            --name {client_name} \
                            --network {self.network_name} \
                            -v {self.logdir}:/mnt/logs \
                            -t -d {self.base_image}", shell=True)
        else:
            subprocess.run(f"docker start {client_name}", shell=True)

        subprocess.run(f"docker cp {self.configfile_path} {genesis_name}:/solana/config.toml", shell=True)
        subprocess.run(f"docker cp {self.configfile_path} {validator_base_name}:/solana/config.toml", shell=True)
        subprocess.run(f"docker cp {self.configfile_path} {client_name}:/solana/config.toml", shell=True)


    def start(self, *args):
        # run faucet
        genesis_name = self.container_settings['genesis']['container-name']
        validator_base_name = self.container_settings['validator']['container-name']
        
        # t1 = threading.Thread(
        #     target=lambda: subprocess.run(f"docker exec {genesis_name} \
        #                 nohup bash -c './multinode-demo/setup.sh &'", shell=True)
        # )
        # t2 = threading.Thread(target=lambda: subprocess.run(f"docker exec {validator_base_name} \
        #                 nohup bash -c './multinode-demo/setup.sh &'", shell=True)
        # )
        # time.sleep(40)

        t3 = threading.Thread(target=lambda: subprocess.run(f"docker exec {genesis_name} \
                       nohup bash -c './multinode-demo/faucet.sh &'", shell=True))
        
        # time.sleep(5)

        # run bootstrap-validator
        t4 = threading.Thread(target=lambda: subprocess.run(f"docker exec {genesis_name} nohup bash -c \
                       './multinode-demo/bootstrap-validator.sh \
                       --gossip-host {self.genesis_host} \
                       --log /mnt/logs/genesis.txt'", shell=True)
        )
        # time.sleep(90)
        

        t5 = threading.Thread(target=lambda: subprocess.run(f"docker exec {validator_base_name} nohup bash -c \
                        './multinode-demo/validator.sh \
                        --entrypoint {self.genesis_host}:8001 --rpc-port 8899 \
                        --log /mnt/logs/validator.txt'", shell=True)
        )
        # time.sleep(100)

        self.threads = [t3, t4, t5]
        # print("=== STARTING SETUP ===")
        # t1.start()
        # t2.start()
        # time.sleep(40)
        
        print("=== STARTING FAUCET ===")
        t3.start()
        time.sleep(5)

        print("=== STARTING BOOTSTRAP EXECUTION ===")
        t4.start()
        time.sleep(10)

        print("=== STARTING VALIDATOR EXECUTION ===")
        t5.start()
        time.sleep(10)
        print("=== CLUSTER IS STARTED ===")

        # run validators
        # for i in range(self.validator_count):
        #     subprocess.run(f"docker exec {self.container_settings['validator']['container-name']}-{i} nohup bash -c \
        #                    RUST_LOG='trace' ./multinode-demo/validator.sh \
        #                    --entrypoint {self.genesis_host}:8001 --rpc-port 8899 \
        #                    --log /mnt/logs/solana_validator_{i}.txt", shell=True)

    def run_client(self, tx_count: int = 50, duration: int = 5, *args):
        # print("STARTING CLIENT SETUP")
        # subprocess.run(f"docker exec {self.container_settings['client']['container-name']} \
        #         nohup bash -c './multinode-demo/setup.sh &'", shell=True)
        print("WAIT FOR COVEREGE")
        time.sleep(30)
        print("STARTING BENCHMARK")
        subprocess.run(f"docker exec {self.container_settings['client']['container-name']} bash -c \
                       \"./multinode-demo/bench-tps.sh \
                       --tx_count {tx_count} --duration {duration} \
                       --entrypoint {self.genesis_host}:8001 --faucet {self.genesis_host}:9900 \
                       > /mnt/logs/clientout.txt 2>/mnt/logs/clienterr.txt\"", shell=True)

    def stop(self, *args):
        subprocess.run(f"docker stop {self.container_settings['genesis']['container-name']}", shell=True)
        # for i in range(self.validator_count):
        #     subprocess.run(f"docker stop {self.container_settings['validator']['container-name']}-{i}", shell=True)
        subprocess.run(f"docker stop {self.container_settings['validator']['container-name']}", shell=True)
        subprocess.run(f"docker stop {self.container_settings['client']['container-name']}", shell=True)
        for t in self.threads:
            t.join()

    def clear(self, *args):
        # pass
        subprocess.run(f"docker rm {self.container_settings['genesis']['container-name']}", shell=True)
        subprocess.run(f"docker rm {self.container_settings['validator']['container-name']}", shell=True)
        # for i in range(self.validator_count):
        #     subprocess.run(f"docker rm {self.container_settings['validator']['container-name']}-{i}", shell=True)
        # subprocess.run(f"docker rm {self.container_settings['client']['container-name']}", shell=True)
