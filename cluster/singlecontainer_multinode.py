import os
import subprocess
import threading
import time

from cluster.cluster import Cluster


# Host - single/multiple
# Container - single/multiple
# Testnet - singel/multiple

# host single & single container & single testnet -> raw docker (done)
# host single & single container & multi testnet -> raw docker (done)
# host single & multi container & multi testnet -> raw docker (done) | swarm (done) | k8s
# host multiple & multi container & multi testnet -> docker swarm | k8s | terraform

class SingleContainerMultiNode(Cluster):
    def __init__(self, 
                 configfile_path, 
                 validator_count: int = 1) -> None:
        super().__init__()
        self.configfile_path = os.path.join(os.getenv('WORKDIR'), configfile_path)
        self.container_name = 'genesis-container'
        self.validator_count = validator_count
        self.threads = []
    
    def create_container(self, container_name: str, image_name: str = 'solana-base', host_logdir: str = '/mnt/solana/dev/logs'):
        self.container_name = container_name
        subprocess.run(f"docker run \
                            --ulimit nofile=1000000:1000000 \
                            --name {self.container_name} \
                            -v {host_logdir}:/mnt/logs \
                            -t -d {image_name}", shell=True)

    def start_containers(self):
        subprocess.run(f"docker start {self.container_name}", shell=True)

    def configure(self, new_configfile_path: str = '', relative_path: bool = False):
        if new_configfile_path:
            if not relative_path:
                self.configfile_path = new_configfile_path
            else:
                self.configfile_path = os.path.join(os.getenv('WORKDIR'), new_configfile_path)
        subprocess.run(f"docker cp {self.configfile_path} {self.container_name}:/solana/config.toml", shell=True)

    def start_cluster(self, write_logs: bool = True, *args):        
        def start_thread(func):
            t = threading.Thread(target=func)
            t.start()
            self.threads.append(t)
        
        # # run faucet
        # print("STARTING FAUCET")
        # start_thread(lambda: subprocess.run(f"docker exec {self.container_name} nohup bash -c './multinode-demo/faucet.sh &'", shell=True))
        # print("WAIT FOR FAUCET...")
        # time.sleep(5)

        # run bootstrap-validator
        print("STARTING BOOTSTRAP-VALIDATOR")
        if write_logs:
            start_thread(
                lambda: subprocess.run(f"docker exec {self.container_name} nohup bash -c \
                                        'RUST_LOG='trace' ./multinode-demo/bootstrap-validator.sh \
                                        --enable-rpc-transaction-history \
                                        --log /mnt/logs/solana_genesis_node.log &'", shell=True)
            )
        else:
            start_thread(
                lambda: subprocess.run(f"docker exec {self.container_name} nohup bash -c \
                                        './multinode-demo/bootstrap-validator.sh --log /dev/null &'", shell=True)
            )
        print("WAIT FOR BOOTSTRAP-VALIDATOR...")
        time.sleep(20)

        # run validators
        print("STARTING VALIDATORS")
        for i in range(self.validator_count):
            if write_logs:
                start_thread(
                    lambda: subprocess.run(f"docker exec {self.container_name} nohup bash -c \
                                            'RUST_LOG='trace' ./multinode-demo/validator.sh \
                                            --log /mnt/logs/solana_validator_{i}.txt &'", shell=True)
                )
            else:
                start_thread(
                    lambda: subprocess.run(f"docker exec {self.container_name} nohup bash -c \
                                            './multinode-demo/validator.sh --log /dev/null &'", shell=True)
                )

    def run_client(self, tx_count: int = 50, duration: int = 20, logfile: str = '/mnt/logs/solana_client_stderr.txt', *args):
        subprocess.run(f"docker exec {self.container_name} bash -c \
                       \"./multinode-demo/bench-tps.sh --tx_count {tx_count} --duration {duration} 2>{logfile}\"",
                       shell=True)

    def stop_cluster(self, *args):
        for t in self.threads:
            t.join()

    def stop_containers(self, *args):
        subprocess.run(f"docker stop {self.container_name}", shell=True)

    def clear(self, *args):
        subprocess.run(f"docker rm {self.container_setting['container-name']}", shell=True)


if __name__ == '__main__':
    import threading
    import time

    os.environ["WORKDIR"] = "/home/exponenci/course-work/project/"
    host = SingleContainerMultiNode("client/src/utils/config.toml")
    print(host.configfile_path)
    stdout, stderr = host.configure(build_container=False)
    print('CONFIGURE\n', stdout, stderr)
    
    def host_start():
        host.start()
    t = threading.Thread(target=host_start) # run in different thread
    t.start()
    
    time.sleep(120) # time for building dependencies in container
    print("CLIENT starting...")
    stdout, stderr = host.run_client()
    print('CLIENT\n', "STDOUT", stdout.decode(), "STDERR", stderr.decode())

    stdout, stderr = host.stop()
    print('STOP\n', stdout[:10000], stderr[:10000])

    t.join()
