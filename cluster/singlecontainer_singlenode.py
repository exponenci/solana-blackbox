import os
import subprocess

from cluster.cluster import Cluster


def run_cmd_get_output(cmd: str, cwd=None, in_shell=False, saveout=False):
    if saveout:
        stdout, stderr = subprocess.PIPE, subprocess.PIPE
    else:
        stdout, stderr = None, None
    if in_shell:
        proc = subprocess.run(cmd, shell=True, stdout=stdout, stderr=stderr, cwd=cwd)
    else:
        proc = subprocess.run(cmd.split(), stdout=stdout, stderr=stderr, cwd=cwd)
    if saveout:
        return proc.stdout, proc.stderr


class SingleContainerSingleNode(Cluster):
    def __init__(self, 
                 configfile_path,
                 container_name: str = 'genesis-container',
                 container_exists: bool = True,
                 remove_container: bool = False):
        super().__init__()
        self.configfile_path = os.path.join(os.getenv('WORKDIR'), configfile_path)
        self.container_name = container_name
        self.container_exists = container_exists
        self.remove_container = remove_container

    def start(self):
        if not self.container_exists:
            self.create_container(self.container_name)
        self.start_container()
        self.configure()
        self.start_cluster()

    def create_container(self, 
                         image_name: str = 'solana-base',
                         host_logdir: str = '/mnt/solana/dev/logs'):
        run_cmd_get_output(f"docker run \
                            --ulimit nofile=1000000:1000000 \
                            --name {self.container_name} \
                            -v {host_logdir}:/mnt/logs \
                            -t -d {image_name}")

    def start_container(self):
        run_cmd_get_output(f"docker start {self.container_name}")

    def configure(self):
        run_cmd_get_output(f"docker cp {self.configfile_path} {self.container_name}:/solana/config.toml")

    def start_cluster(self):
        run_cmd_get_output(f"""docker exec {self.container_name} bash -c "./multinode-demo/setup.sh && \
                            nohup bash -c './multinode-demo/faucet.sh &' && \
                            RUST_LOG='trace' ./multinode-demo/bootstrap-validator.sh \
                            --enable-rpc-transaction-history \
                            --log /mnt/logs/solana_genesis_node.log\"""", in_shell=True)

    def run_client(self, 
                   tx_count: int = 50, 
                   duration: int = 5, 
                   logfile: str = '/mnt/logs/solana_client_stderr.txt'):
        subprocess.run(f"docker exec {self.container_name} bash -c \
                       \"./multinode-demo/bench-tps.sh --tx_count {tx_count} --duration {duration} 2>{logfile}\"", 
                       shell=True)

    def stop(self):
        run_cmd_get_output(f"docker stop {self.container_name}")
        if self.remove_container:
            run_cmd_get_output(f"docker rm {self.container_name}")


if __name__ == '__main__':
    import threading
    import time

    os.environ["WORKDIR"] = "/home/exponenci/course-work/project/"
    host = SingleContainerSingleNode("client/src/utils/config.toml")
    print(host.configfile_path)
    host.configure(build_container=False)
    
    def host_start():
        host.start()
    t = threading.Thread(target=host_start) # run in different thread
    t.start()
    
    time.sleep(120) # time for building dependencies in container
    host.run_client()
    host.stop()

    t.join()
