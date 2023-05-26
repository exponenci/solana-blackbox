import os
import time
import threading
import subprocess

from cluster.cluster import Cluster


class SingleContainerMultiNode(Cluster):
    def __init__(self, 
                 configfile_path, 
                 container_name: str = 'genesis-container',
                 validator_count: int = 1,
                 container_exists: bool = True,
                 remove_container: bool = False):
        super().__init__()
        self.configfile_path = os.path.join(os.getenv('WORKDIR'), configfile_path)
        self.container_name: str = container_name
        self.validator_count: int = validator_count
        self.container_exists: bool = container_exists
        self.remove_container: bool = remove_container
        self.threads: list = []
    
    def start(self):
        if not self.container_exists:
            self.create_container(self.container_name)
        self.start_container()
        self.configure()
        self.start_cluster(write_logs=False)

    def create_container(self, 
                         container_name: str, 
                         image_name: str = 'solana-base', 
                         host_logdir: str = '/mnt/solana/dev/logs'):
        self.container_name = container_name
        subprocess.run(f"docker run \
                            --ulimit nofile=1000000:1000000 \
                            --name {self.container_name} \
                            -v {host_logdir}:/mnt/logs \
                            -t -d {image_name}", shell=True)

    def start_container(self):
        subprocess.run(f"docker start {self.container_name}", shell=True)

    def configure(self, 
                  new_configfile_path: str = '', 
                  relative_path: bool = False):
        if new_configfile_path:
            if not relative_path:
                self.configfile_path = new_configfile_path
            else:
                self.configfile_path = os.path.join(os.getenv('WORKDIR'), new_configfile_path)
        subprocess.run(f"docker cp {self.configfile_path} {self.container_name}:/solana/config.toml", 
                       shell=True)

    def start_cluster(self, 
                      write_logs: bool = True):        
        def start_thread(func):
            t = threading.Thread(target=func)
            t.start()
            self.threads.append(t)
        
        print("STARTING SETUP")
        subprocess.run(f"docker exec {self.container_name} bash -c './multinode-demo/setup.sh'", 
                       shell=True)
        print("SETUP DONE")
        time.sleep(10)

        # run faucet
        print("STARTING FAUCET")
        start_thread(
            lambda: subprocess.run(f"docker exec {self.container_name} nohup bash -c \
                                   './multinode-demo/faucet.sh 2>/dev/null &'", 
                                   shell=True)
        )
        print("WAIT FOR FAUCET...")
        time.sleep(10)

        # run bootstrap-validator
        print("STARTING BOOTSTRAP-VALIDATOR")
        if write_logs:
            start_thread(
                lambda: subprocess.run(f"docker exec {self.container_name} nohup bash -c \
                                        'RUST_LOG='trace' ./multinode-demo/bootstrap-validator.sh \
                                        --enable-rpc-transaction-history \
                                        --log /mnt/logs/solana_genesis_node.log &'", 
                                        shell=True)
            )
        else:
            start_thread(
                lambda: subprocess.run(f"docker exec {self.container_name} bash -c \
                                        './multinode-demo/bootstrap-validator.sh --log /dev/null'", 
                                        shell=True)
            )
        print("WAIT FOR BOOTSTRAP-VALIDATOR...")
        time.sleep(120)

        # run validators
        print("STARTING VALIDATORS")
        for i in range(self.validator_count):
            if write_logs:
                start_thread(
                    lambda: subprocess.run(f"docker exec {self.container_name} nohup bash -c \
                                            'RUST_LOG='trace' ./multinode-demo/validator.sh \
                                            --log /mnt/logs/solana_validator_{i}.txt &'", 
                                            shell=True)
                )
            else:
                start_thread(
                    lambda: subprocess.run(f"docker exec {self.container_name} bash -c \
                                            './multinode-demo/validator.sh --log /dev/null'", 
                                            shell=True)
                )
        time.sleep(50)

    def run_client(self, 
                   tx_count: int = 50, 
                   duration: int = 20, 
                   logfile: str = '/mnt/logs/solana_client_stderr.txt'):
        subprocess.run(f"docker exec {self.container_name} bash -c \
                       \"./multinode-demo/bench-tps.sh --tx_count {tx_count} --duration {duration} 2>{logfile}\"",
                       shell=True)

    def stop(self):
        self.stop_containers()
        self.stop_cluster()
        if self.remove_container:
            self.clear()

    def stop_containers(self):
        subprocess.run(f"docker stop {self.container_name}", shell=True)

    def stop_cluster(self):
        for t in self.threads:
            t.join()

    def clear(self):
        subprocess.run(f"docker rm {self.container_name}", shell=True)
