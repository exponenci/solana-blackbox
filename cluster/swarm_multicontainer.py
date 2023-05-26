import io
import os
import subprocess

import yaml

from cluster.cluster import Cluster


class StackCluster(Cluster):
    def __init__(self, 
                 configfile_path, 
                 base_image: str = 'solana-base',
                 composefile: str = 'docker-compose.yml',
                 logdir: str = '/mnt/solana/dev/logs', 
                 stack_name: str = 'solana_chain',
                 validator_count: int = 1,
                 remove_services: bool = False) -> None:
        super().__init__()
        self.configfile_path = os.path.join(os.getenv('WORKDIR'), configfile_path) # must be on volume
        self.configfile_volume = os.path.dirname(self.configfile_path)
        self.base_image = base_image
        self.validator_count = validator_count
        self.logdir = logdir
        self.composefile = composefile 
        self.stack_name = stack_name
        with open(composefile, 'r') as stream:
            self.compose_info = yaml.safe_load(stream)
        self.remove_services = remove_services

    def start(self):
        self.configure()
        self.start_cluster()

    def configure(self):
        genesis_service = self.compose_info['services']['genesis']
        genesis_service['image'] = self.base_image
        genesis_service['volumes'] = [self.logdir + ':/mnt/logs', 
                                      self.configfile_volume + ':/solana/config']
        genesis_service['environment'] = ['TOML_CONFIG=/solana/config/config.toml']


        validator_service = self.compose_info['services']['validator']
        validator_service['image'] = self.base_image
        validator_service['volumes'] = [self.logdir + ':/mnt/logs', 
                                        self.configfile_volume + ':/solana/config']
        validator_service['environment'] = ['TOML_CONFIG=/solana/config/config.toml']
        validator_service['deploy']['replicas'] = self.validator_count


        client_service = self.compose_info['services']['client']
        client_service['image'] = self.base_image
        client_service['volumes'] = [self.logdir + ':/mnt/logs', 
                                     self.configfile_volume + ':/solana/config']
        client_service['environment'] = ['TOML_CONFIG=/solana/config/config.toml']


        with io.open(self.composefile, 'w', encoding='utf8') as outfile:
            yaml.dump(self.compose_info, outfile, default_flow_style=False, allow_unicode=True)        

    def start_cluster(self):
        subprocess.run(f"docker stack deploy -c {self.composefile} {self.stack_name}", shell=True)

    def run_client(self) -> None:
        # executed in background via swarm
        pass

    def stop(self):
        if self.remove_services:
            self.clear()

    def clear(self):
        subprocess.run(f"docker stack rm {self.stack_name}", shell=True)
