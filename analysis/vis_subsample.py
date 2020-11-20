from configuration import load_configuration
from mne_bids.utils import get_entity_vals

import argparse

import time
import pandas as pd
import parsl
from parsl.app.app import python_app
from parsl_config import pconfig

import matplotlib.pyplot as plt
import ptitprince as pt

config = None

@python_app
def func(config):
    import mne
    from autoreject import AutoReject
    import utils
    import sys
    import numpy as np
    import pandas as pd

    data = pd.read_csv("out100.csv", header=0)

    return data


   

def main():
    parsl.load(pconfig)

    df = func(config).result()
    summ = df.groupby(['id', 'num', "run"], as_index=False).agg('mean')

    f, ax = plt.subplots(figsize=(7, 5))

    ax=pt.RainCloud(x = "num", y = "amplitude_difference", data = summ, ax = ax)


    plt.savefig('fig_out.png', bbox_inches='tight')


if __name__ == '__main__':
    main()