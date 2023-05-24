import os
import uuid
from subprocess import Popen, PIPE

validator_count = 'validator_count'
instance_type = 'instance_type'
env_name = 'env_name'
blockchain_type = 'blockchain_type'

default_instance_type = 't2.2xlarge'
variables_template = \
'''
variable "validator_count" {{
  description = "Number of validator instances"
  type        = number
  default     = {validator_count}
}}
variable "instance_type" {{
  description = "AWS instance type"
  type = string
  default = "{instance_type}"
}}
variable "env_name" {{
  description = "Name of the infrastucture"
  type = string
  default = "{env_name}"
}}
variable "default_subnets" {{
  type    = list(string)
  default = ["subnet-0e8d409cecbe85b3f", "subnet-03f67ded970379ad9", "subnet-09472a9daf4cc10d0"]
}}
'''


current_dir = os.path.dirname(os.path.realpath(__file__))
chains_dir = os.path.join(current_dir, '..', 'chains')
base_dir = os.path.join(current_dir, '..')


def chain_configure(uid: str, params: dict):
    tf_variables_path = os.path.join(chains_dir, uid, 'variables.tf')

    output_variables = variables_template

    output_variables = output_variables.format(
        validator_count=params['validator_count'],
        instance_type=params['instance_type'] if 'instance_type' in params else default_instance_type,
        env_name=params['env_name']
    )

    with open(tf_variables_path, 'w') as f:
        f.write(output_variables)

    command = 'cp -r {} {}'.format(
        params['config_path'],
        os.path.join(chains_dir, uid)
    )
    command = command.split()
    process = Popen(command, stdout=PIPE, stderr=PIPE, cwd=base_dir)
    stdout, stderr = process.communicate()
    return uid, (stdout, stderr)
def chain_init(uid: str):
    chain_path = os.path.join(chains_dir, uid)
    command = 'terraform init'
    command = command.split()
    process = Popen(command, stdout=PIPE, stderr=PIPE, cwd=chain_path)
    stdout, stderr = process.communicate()
    return uid, (stdout, stderr)


def chain_start(uid: str):
    chain_path = os.path.join(chains_dir, uid)
    command = 'terraform apply -auto-approve'
    command = command.split()
    process = Popen(command, stdout=PIPE, stderr=PIPE, cwd=chain_path)
    stdout, stderr = process.communicate()
    return uid, (stdout, stderr)


def chain_stop(uid: str):
    chain_path = os.path.join(chains_dir, uid)
    command = 'terraform destroy -auto-approve'
    command = command.split()
    process = Popen(command, stdout=PIPE, stderr=PIPE, cwd=chain_path)
    stdout, stderr = process.communicate()
    return uid, (stdout, stderr)


def chain_remove(uid: str):
    command = 'rm -r chains/{}'.format(uid)
    command = command.split()
    process = Popen(command, stdout=PIPE, stderr=PIPE, cwd=base_dir)
    stdout, stderr = process.communicate()
    return uid, (stdout, stderr)
def chain_new(uid: str = None):
    if uid is None:
        uid = uuid.uuid4().hex
    command = 'cp -r template chains/{}'.format(uid)
    command = command.split()
    print('New chain is created with UID {}'.format(uid))
    print(command)
    process = Popen(command, stdout=PIPE, stderr=PIPE, cwd=base_dir)
    stdout, stderr = process.communicate()

    return uid, (stdout, stderr)


def chain_get_outputs(uid: str = None):
    chain_path = os.path.join(chains_dir, uid)
    command = 'terraform output'
    command = command.split()
    process = Popen(command, stdout=PIPE, stderr=PIPE, cwd=chain_path)
    stdout, stderr = process.communicate()
    outputs = str(stdout, encoding='utf-8').split('\n')
    outputs = [str(output) for output in outputs]
    outputs = [output.split(' ') for output in outputs]
    outputs = [output for output in outputs if len(output)>2]

    outputs = {output[0]: output[2] for output in outputs}
    return outputs, (stdout, stderr)


def chain_get_ip(uid: str = None):
    outputs, logs = chain_get_outputs(uid)
    public_ip = outputs['genesis_public_ip']
    public_ip = public_ip[1:-1]
    return public_ip, logs


def chain_get_logs(uid: str = None):
    ip, logs = chain_get_ip(uid)
    chain_path = os.path.join(chains_dir, uid)
    command = 'scp -r ubuntu@{}:/home/ubuntu/efs/logs .'.format(ip)
    command = command.split()
    print(command)
    process = Popen(command, stdout=PIPE, stderr=PIPE, cwd=chain_path)
    stdout, stderr = process.communicate()
    return uid, (stdout, stderr)


def chain_get_params(uid):
    pass


if __name__ == '__main__':
    print(current_dir)
    print(chains_dir)