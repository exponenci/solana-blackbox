import os
import subprocess

from cluster.cluster import Cluster


def run_cmd_get_output(cmd: str, cwd=None, in_shell=False):
    if in_shell:
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    else:
        proc = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    return proc.stdout, proc.stderr


class SingleContainerSingleNode(Cluster):
    def __init__(self, configfile_path) -> None:
        super().__init__()
        self.work_dir = os.getenv('WORKDIR')
        self.configfile_path = os.path.join(self.work_dir, configfile_path)
        self.container_name = ''

    def configure(self, build_container: bool = True, container_name: str = 'genesis-container', *args):
        self.container_name = container_name
        if build_container:
            stdout, stderr = run_cmd_get_output(f"docker run \
                                                --ulimit nofile=1000000:1000000 \
                                                --name {self.container_name} \
                                                --network chains-network \
                                                -v /mnt/solana/dev/logs:/mnt/logs \
                                                --hostname genesis_node -t -d solana-base")
        else:
            stdout, stderr = run_cmd_get_output(f"docker start {container_name}")
        if stderr:
            return stdout, stderr
        stdout, stderr = run_cmd_get_output(f"docker cp {self.configfile_path} {self.container_name}:/solana/config.toml")
        return stdout, stderr

    def start(self, *args):
        stdout, stderr = run_cmd_get_output(f"""docker exec {self.container_name} bash -c "./multinode-demo/setup.sh && \
                                            nohup bash -c './multinode-demo/faucet.sh &' && \
                                            RUST_LOG='trace' ./multinode-demo/bootstrap-validator.sh \
                                            --enable-rpc-transaction-history \
                                            --log /mnt/logs/solana_genesis_node.log\"""", in_shell=True)
        return stdout, stderr


    def run_client(self, tx_count: int = 50, duration: int = 5, *args):
        stdout, stderr = run_cmd_get_output(f"docker exec {self.container_name} bash -c \
                                            \"./multinode-demo/bench-tps.sh \
                                            --tx_count {tx_count} --duration {duration}\"", in_shell=True)
        return stdout, stderr

    def stop(self, *args):
        return run_cmd_get_output(f"docker stop {self.container_name}")

    def clear(self, *args):
        return run_cmd_get_output(f"docker rm {self.container_name}")


if __name__ == '__main__':
    import threading
    import time

    os.environ["WORKDIR"] = "/home/exponenci/course-work/project/"
    host = SingleContainerSingleNode("client/src/utils/config.toml")
    print(host.configfile_path)
    stdout, stderr = host.configure(build_container=False)
    print('CONFIGURE\n', stdout, stderr)
    
    def host_start():
        stdout, stderr = host.start()
        print('START\n', stdout[:10000], '\n', stderr[:10000])
    t = threading.Thread(target=host_start) # run in different thread
    t.start()
    
    time.sleep(120) # time for building dependencies in container
    print("CLIENT starting...")
    stdout, stderr = host.run_client()
    print('CLIENT\n', "STDOUT", stdout.decode(), "STDERR", stderr.decode())

    stdout, stderr = host.stop()
    print('STOP\n', stdout[:10000], stderr[:10000])

    t.join()
