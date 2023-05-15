import io
import os
import yaml
import subprocess

from cluster.cluster import Cluster


class StackCluster(Cluster):
    def __init__(self, 
                 configfile_path, 
                 base_image: str = 'solana-base',
                 composefile: str = 'docker-compose.yml',
                 logdir: str = '/mnt/solana/dev/logs', 
                 stack_name: str = 'solana_chain',
                 validator_count: int = 1) -> None:
        super().__init__()
        self.work_dir = os.getenv('WORKDIR')
        self.configfile_path = os.path.join(self.work_dir, configfile_path) # must be on volume
        self.configfile_volume = os.path.dirname(self.configfile_path)
        self.base_image = base_image
        self.validator_count = validator_count
        self.logdir = logdir
        self.composefile = composefile 
        self.stack_name = stack_name
        with open(composefile, 'r') as stream:
            self.compose_info = yaml.safe_load(stream)

    def configure(self, *args, **kwargs):
        self.compose_info['services']['genesis']['image'] = self.base_image
        self.compose_info['services']['genesis']['volumes'] = [self.logdir + ':/mnt/logs', 
                                                               self.configfile_volume + ':/solana/config']
        self.compose_info['services']['genesis']['environment'] = ['TOML_CONFIG=/solana/config/config.toml']

        self.compose_info['services']['validator']['image'] = self.base_image
        self.compose_info['services']['validator']['volumes'] = [self.logdir + ':/mnt/logs', 
                                                                 self.configfile_volume + ':/solana/config']
        self.compose_info['services']['validator']['environment'] = ['TOML_CONFIG=/solana/config/config.toml']
        self.compose_info['services']['validator']['deploy']['replicas'] = self.validator_count

        self.compose_info['services']['client']['image'] = self.base_image
        self.compose_info['services']['client']['volumes'] = [self.logdir + ':/mnt/logs', 
                                                              self.configfile_volume + ':/solana/config']
        self.compose_info['services']['client']['environment'] = ['TOML_CONFIG=/solana/config/config.toml']

        with io.open(self.composefile, 'w', encoding='utf8') as outfile:
            yaml.dump(self.compose_info, outfile, default_flow_style=False, allow_unicode=True)        

    def start(self, *args):
        subprocess.run(f"docker stack deploy -c {self.composefile} {self.stack_name}", shell=True)

    def stop(self, *args):
        pass

    def clear(self, *args):
        subprocess.run(f"docker stack rm {self.stack_name}", shell=True)
