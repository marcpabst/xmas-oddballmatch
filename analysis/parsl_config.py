from parsl.config import Config
from parsl.providers import SlurmProvider
from parsl.launchers import SrunLauncher
from parsl.executors import HighThroughputExecutor

pconfig = Config(
    executors=[
        HighThroughputExecutor(
            label='Galaxy',
            max_workers = 1,
            provider=SlurmProvider(
                'galaxy-job',  # Partition / QOS
                nodes_per_block = 1,
                min_blocks = 1,
                max_blocks = 20,
                init_blocks= 1,
                parallelism = 1.,
                # string to prepend to #SBATCH blocks in the submit
                #scheduler_options='#SBATCH -C haswell',
                # Command to be run before starting a worker
                worker_init='module load python; module load MATLAB; source activate env/bin/activate; PYTHONPATH="${PYTHONPATH}:./";',
                walltime='24:00:00'
            ),
        )
    ]
)