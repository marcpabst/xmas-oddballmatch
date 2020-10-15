import parsl
import os
from parsl.config import Config
from parsl.providers import SlurmProvider
from parsl.launchers import SrunLauncher
from parsl.executors import HighThroughputExecutor
from parsl.app.app import python_app, bash_app
import socket

print(parsl.__version__)

config = Config(
    executors=[
        HighThroughputExecutor(
            label='Galaxy',
            # Optional: the network interface on the login node to
            # which compute nodes can communicate
            #address=address_by_interface('bond0.144'),
            cores_per_worker=1,
            provider=SlurmProvider(
                'galaxy-test',  # Partition / QOS
                #nodes_per_block=2,
                # string to prepend to #SBATCH blocks in the submit
                #scheduler_options='#SBATCH -C haswell',
                # Command to be run before starting a worker
                worker_init='module load python; module load MATLAB; source activate env/bin/activate;',
                # We request all hyperthreads on a node.
                #launcher=SrunLauncher(overrides='-c 64'),
                #walltime='00:10:00',
                # Slurm scheduler on Cori can be slow at times,
                # increase the command timeouts
                #cmd_timeout=120,
            ),
        )
    ]
)

parsl.load(config)
parsl.set_stream_logger()

@python_app
def prepare_data(id):
    import socket
    import logging
    logging.info("Running on {}".format(socket.gethostname()))
    __import__('01_prepare_data.py').prepare_data(id)

prepare_data("002").result()