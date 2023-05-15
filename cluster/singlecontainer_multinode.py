import os
import subprocess
import threading

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
                 base_image: str = 'solana-base', 
                 logdir: str = '/mnt/solana/dev/logs',
                 container_setting = {'container-name': 'genesis-container', 'create': False},
                 validator_count: int = 1) -> None:
        super().__init__()
        self.work_dir = os.getenv('WORKDIR')
        self.configfile_path = os.path.join(self.work_dir, configfile_path)
        self.base_image = base_image
        self.container_setting = container_setting
        self.validator_count = validator_count
        self.logdir = logdir
        self.threads = []

    def configure(self, container_settings: dict = dict(), *args):
        if len(container_settings) == 2:
            self.container_setting = container_settings
        if self.container_setting['create']:
            subprocess.run(f"docker run \
                            --ulimit nofile=1000000:1000000 \
                            --name {self.container_setting['container-name']} \
                            -v {self.logdir}:/mnt/logs \
                            -t -d {self.base_image}", shell=True)
        else:
            subprocess.run(f"docker start {self.container_setting['container-name']}", shell=True)
        subprocess.run(f"docker cp {self.configfile_path} {self.container_setting['container-name']}:/solana/config.toml", shell=True)

    def start(self, *args):
        container_name = self.container_setting['container-name']
        # setup blockchain
        # subprocess.run(f"docker exec {container_name} bash -c \"./multinode-demo/setup.sh\"", shell=True)

        # run faucet
        t = threading.Thread(
            target=lambda: subprocess.run(f"docker exec {container_name} nohup bash -c './multinode-demo/faucet.sh &'", shell=True)
        )
        t.start()
        self.threads.append(t)

        # run bootstrap-validator
        t = threading.Thread(
            target=lambda: subprocess.run(f"docker exec {container_name} nohup bash -c \
                            'RUST_LOG='trace' ./multinode-demo/bootstrap-validator.sh \
                            --enable-rpc-transaction-history \
                            --log /mnt/logs/solana_genesis_node.log'", shell=True)
        )
        t.start()
        self.threads.append(t)
        
        # run validators
        for i in range(self.validator_count):
            t = threading.Thread(
                target=lambda: subprocess.run(f"docker exec {container_name} nohup bash -c \
                                RUST_LOG='trace' ./multinode-demo/validator.sh \
                                --log /mnt/logs/solana_validator_{i}.txt", shell=True)
            )
            t.start()
            self.threads.append(t)

    def run_client(self, tx_count: int = 50, duration: int = 5, *args):
        subprocess.run(f"docker exec {self.container_setting['container-name']} bash -c \
                       \"./multinode-demo/bench-tps.sh \
                       --tx_count {tx_count} --duration {duration} \
                       2>/mnt/logs/solana_client_stderr.txt\"", shell=True)

    def stop(self, *args):
        subprocess.run(f"docker stop {self.container_setting['container-name']}", shell=True)
        for t in self.threads:
            t.join()

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
