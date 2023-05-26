from sensitivity_analysis.matlab_sensitivity_analysis import PCEMatlabM, GPMatlabM, PCGPMatlabM

# overall info
PROJECT_WORKDIR: str = '/home/exponenci/course-work/project/'
HOST_LOGDIR_MOUNT: str = '/mnt/solana/dev/logs/'
CONTAINER_LOGDIR_MOUNT: str = '/mnt/logs/'

TOTAL_PARAM_COUNT: int = 89
BASE_CONFIG: str = 'config.toml'
TARGET_CONFIG: str = 'upd_config.toml'
CLUSTER_RUN_INFO_FILE: str = 'result.csv'


# containers' cluster run info
SAVE_CLUSTER_RUN_INFO: bool = True
EXPERIMENT_PARAM_IDS: list = list(range(66))

BLOCKCHAIN_CONVERGENCE_TIME_IN_SEC: int = 100

CLIENT_TX_COUNT: int = 100000
CLIENT_DURATION: int = 90
CLIENT_LOGFILE: str = 'solana_client_stderr.txt'


# sensitivity analysis module info
MATLAB_SERVER_ADDR: str = '10.193.91.250'
MATLAB_SERVER_PORT: int = 9889
SENSITIVITY_ANALYSIS_METHODS: dict = {
    'PCEMatlabM': PCEMatlabM(addr=MATLAB_SERVER_ADDR, port=MATLAB_SERVER_PORT),
    'GPMatlabM': GPMatlabM(addr=MATLAB_SERVER_ADDR, port=MATLAB_SERVER_PORT),
    'PCGPMatlabM': PCGPMatlabM(addr=MATLAB_SERVER_ADDR, port=MATLAB_SERVER_PORT),
}
SENSITIVITY_ANALYSIS_TARGET_PARAM_COUNT: int = 5


# optimization methods arguments info
OPTIMIZATION_MAX_EVALS: int = 5
OPTIMIZATION_BOUNDS_COEFS: tuple = (0.8, 1.2)
