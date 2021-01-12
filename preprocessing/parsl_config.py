from parsl.config import Config
from parsl.providers import SlurmProvider, LocalProvider
from parsl.monitoring.monitoring import MonitoringHub
from parsl.launchers import SrunLauncher
from parsl.addresses import address_by_hostname
from parsl.executors import HighThroughputExecutor
from parsl.channels import LocalChannel




pconfig = Config(
    executors=[
        HighThroughputExecutor(
            max_workers = 1,
            provider=LocalProvider(
                channel=LocalChannel(),
                max_blocks = 1,
                parallelism = 0,
                nodes_per_block = 1,
                worker_init='export PYTHONPATH="/media/marc/Medien/xmas-oddballmatch:/media/marc/Medien/xmas-oddballmatch/preprocessing"',
            ),
        )
    ]
)

# pconfig = Config(
#     executors=[
#         HighThroughputExecutor(
#             label='Galaxy',
#             max_workers = 1,
#             provider=SlurmProvider(
#                 'galaxy-job',  # Partition / QOS
#                 nodes_per_block = 1,
#                 min_blocks = 1,
#                 max_blocks = 20,
#                 init_blocks = 1,
#                 parallelism = 1.,
#                 # string to prepend to #SBATCH blocks in the submit
#                 #scheduler_options='#SBATCH -C haswell',
#                 # Command to be run before starting a worker
#                 worker_init='module load python; module load MATLAB; source activate ../env/bin/activate; export PYTHONPATH="${PYTHONPATH}:./";',
#                 walltime='01:00:00'
#             ),
#         )
#     ]
# )

