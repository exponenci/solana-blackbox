import os
import subprocess
import time

from cluster.cluster import Cluster


# Host - single/multiple
# Container - single/multiple
# Testnet - singel/multiple

# host single & single container & single testnet -> raw docker (done)
# host single & single container & multi testnet -> raw docker (done)
# host single & multi container & multi testnet -> raw docker (done) | swarm | k8s
# host multiple & multi container & multi testnet -> docker swarm | k8s | terraform

class MultiContainerMultiNode(Cluster):
    def __init__(self, configfile_path, 
                base_image: str = 'solana-base', 
                configured_image: str = 'solana-base-with-config', 
                genesis_host: str = 'genesishost',
                logdir: str = '/mnt/solana/dev/logs', 
                network_name: str = 'chains-network',
                validator_count: int = 1) -> None:
        super().__init__()
        self.work_dir = os.getenv('WORKDIR')
        self.configfile_path = os.path.join(self.work_dir, configfile_path)
        self.base_image = base_image
        self.configured_image = configured_image
        self.container_settings = {
            "genesis": {'container-name': 'genesis-container', 'create': False},
            "validator": {'container-name': 'validator-container', 'create': False},
            "client": {'container-name': 'client-container', 'create': False},
        }
        self.genesis_host = genesis_host
        self.logdir = logdir
        self.network_name = network_name
        self.validator_count = validator_count

    def configure(self, create_network: bool = False, container_settings: dict = dict(), *args, **kwargs):

        subprocess.run(f"docker run --ulimit nofile=1000000:1000000 --name tmp_container {self.base_image}", shell=True)
        subprocess.run(f"docker cp {self.configfile_path} tmp_container:/solana/config.toml", shell=True)
        subprocess.run(f"docker stop tmp_container", shell=True)
        subprocess.run(f"docker commit tmp_container {self.configured_image}", shell=True)
        subprocess.run(f"docker container rm tmp_container", shell=True)

        if len(container_settings) == 3:
            self.container_settings = container_settings

        if create_network:
            subprocess.run(f"docker network create -d overlay --attachable {self.network_name}")
        if self.container_settings['genesis']['create']:
            subprocess.run(f"docker run \
                            --ulimit nofile=1000000:1000000 \
                            --name {self.container_settings['genesis']['container-name']} \
                            --network {self.network_name} \
                            -v {self.logdir}:/mnt/logs \
                            --hostname {self.genesis_host} \
                            -p 80:80 \
                            -p 8001:8001 \
                            -p 8899:8899 \
                            -p 9900:9900 \
                            -t -d {self.configured_image}", shell=True)
        else:
            subprocess.run(f"docker start {self.container_settings['genesis']['container-name']}", shell=True)
        if self.container_settings['validator']['create']:
            for i in range(self.validator_count):
                subprocess.run(f"docker run \
                                --ulimit nofile=1000000:1000000 \
                                --name {self.container_settings['validator']['container-name']}-{i} \
                                --network {self.network_name} \
                                -v {self.logdir}:/mnt/logs \
                                -t -d {self.configured_image}", shell=True)
        else:
            for i in range(self.validator_count):
                subprocess.run(f"docker start {self.container_settings['validator']['container-name']}-{i}", shell=True)
        if self.container_settings['client']['create']:
            for i in range(self.validator_count):
                subprocess.run(f"docker run \
                                --ulimit nofile=1000000:1000000 \
                                --name {self.container_settings['client']['container-name']}-{i} \
                                --network {self.network_name} \
                                -v {self.logdir}:/mnt/logs \
                                -t -d {self.configured_image}", shell=True)
        else:
            subprocess.run(f"docker start {self.container_settings['client']['container-name']}", shell=True)

    def start(self, *args):
        # run faucet
        subprocess.run(f"docker exec {self.container_settings['genesis']['container-name']} \
                       nohup bash -c './multinode-demo/faucet.sh &'", shell=True)
        
        # run bootstrap-validator
        subprocess.run(f"docker exec {self.container_settings['genesis']['container-name']} nohup bash -c \
                       'RUST_LOG='trace' ./multinode-demo/bootstrap-validator.sh \
                       --enable-rpc-transaction-history \
                       --gossip-host {self.genesis_host} \
                       --log /mnt/logs/solana_genesis_node.log'", shell=True)
        
        time.sleep(60)

        # run validators
        for i in range(self.validator_count):
            subprocess.run(f"docker exec {self.container_settings['validator']['container-name']}-{i} nohup bash -c \
                           RUST_LOG='trace' ./multinode-demo/validator.sh \
                           --entrypoint {self.genesis_host}:8001 --rpc-port 8899 \
                           --log /mnt/logs/solana_validator_{i}.txt", shell=True)

    def run_client(self, tx_count: int = 50, duration: int = 5, *args):
        subprocess.run(f"docker exec {self.container_settings['client']['container-name']} bash -c \
                       \"./multinode-demo/bench-tps.sh \
                       --tx_count {tx_count} --duration {duration} \
                       --entrypoint {self.genesis_host}:8001 --faucet {self.genesis_host}:9900 \
                       2>/mnt/logs/solana_client_stderr.txt\"", shell=True)

    def stop(self, *args):
        subprocess.run(f"docker stop {self.container_settings['genesis']['container-name']}", shell=True)
        for i in range(self.validator_count):
            subprocess.run(f"docker stop {self.container_settings['validator']['container-name']}-{i}", shell=True)
        subprocess.run(f"docker stop {self.container_settings['client']['container-name']}", shell=True)

    def clear(self, *args):
        subprocess.run(f"docker rm {self.container_settings['genesis']['container-name']}", shell=True)
        for i in range(self.validator_count):
            subprocess.run(f"docker rm {self.container_settings['validator']['container-name']}-{i}", shell=True)
        subprocess.run(f"docker rm {self.container_settings['client']['container-name']}", shell=True)


# if __name__ == '__main__':
#     import threading
#     import time

#     os.environ["WORKDIR"] = "/home/exponenci/course-work/project/"
#     host = MultiContainerMultiNode("client/src/utils/config.toml")
#     print(host.configfile_path)
#     stdout, stderr = host.configure(build_container=False)
#     print('CONFIGURE\n', stdout, stderr)
    
#     def host_start():
#         host.start()
#     t = threading.Thread(target=host_start) # run in different thread
#     t.start()
    
#     time.sleep(120) # time for building dependencies in container
#     print("CLIENT starting...")
#     stdout, stderr = host.run_client()
#     print('CLIENT\n', "STDOUT", stdout.decode(), "STDERR", stderr.decode())

#     stdout, stderr = host.stop()
#     print('STOP\n', stdout[:10000], stderr[:10000])

#     t.join()
# # 