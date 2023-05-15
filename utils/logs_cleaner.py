import os
import subprocess


def clean_chain_logs(logsdirname: str):
    ans = input(f'are you sure to clear {logsdirname}? (y/n)').lower()
    if ans == 'y' or ans == 'yes':
        subprocess.run(f'rm -rf {logsdirname}', shell=True)


if __name__ == '__main__':
    clean_chain_logs(os.getenv('CHAIN_LOG_DIR', '/mnt/solana/dev/logs/'))
