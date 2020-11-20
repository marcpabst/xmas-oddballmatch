{
 "metadata": {
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5-final"
  },
  "orig_nbformat": 2,
  "kernelspec": {
   "name": "python38264bitenvvenv500f308f313b45eeaf82c32beb5092d7",
   "display_name": "Python 3.8.2 64-bit ('env': venv)"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2,
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "from ...configuration.configuration import load_configuration\n",
    "\n",
    "import utils\n",
    "\n",
    "from os.path import join\n",
    "import mne\n",
    "from mne_bids import make_bids_basename, read_raw_bids\n",
    "from mne_bids.utils import get_entity_vals\n",
    "\n",
    "import plotting\n",
    "\n",
    "import seaborn as sns\n",
    "\n",
    "config = None\n",
    "\n",
    "\n",
    "nums = [100, 200, 300, 400, 500]\n",
    "N = 10\n",
    "peak_latency = 0.135\n",
    "\n",
    "\n",
    "bids_root_path= \"/media/marc/Medien/xmasoddballmatch-bids\"\n",
    "pipeline_name = \"pipeline01\"\n",
    "\n",
    "ids = get_entity_vals(join(bids_root_path, \"derivatives\"), \"sub\") "
   ]
  },
  {
   "source": [
    "## Load Cleaned Raw Data from Disk"
   ],
   "cell_type": "markdown",
   "metadata": {}
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "def load_and_epoch(id):\n",
    "    # Load Data\n",
    "    raw_filename = utils.get_derivative_file_name(\n",
    "        config[\"bids_root_path\"], id, config[\"pipeline_name\"], \".fif\", suffix=\"raw\", processing=\"cleaned\")\n",
    "    events_filename = utils.get_derivative_file_name(\n",
    "        config[\"bids_root_path\"], id, config[\"pipeline_name\"], \".txt\", suffix=\"eve\", processing=\"prepared\")\n",
    "    raw = mne.io.read_raw_fif(raw_filename, preload=True)\n",
    "    events = mne.read_events(events_filename)\n",
    "\n",
    "    # Epoch Data\n",
    "    raw.pick([\"eeg\", \"eog\"])\n",
    "    epochs = mne.Epochs(raw, events, config[\"events_dict\"],\n",
    "                        tmin=config[\"epoch_window\"][0],\n",
    "                        tmax=config[\"epoch_window\"][1],\n",
    "                        baseline=config[\"baseline_winow\"],\n",
    "                        #reject=config[\"diff_criterion\"],\n",
    "                        reject=None,\n",
    "                        preload=True)\n",
    "\n",
    "    # Fit AutoReject\n",
    "    ar = AutoReject(verbose = False)\n",
    "    ar.fit(epochs)\n",
    "\n",
    "    return {\"epochs\":epochs, \"events\":events, \"ar\":ar}\n",
    "\n",
    "subjects_data = {id: load_and_epoch(id) for id in ids}"
   ]
  },
  {
   "source": [
    "## Epoch Data"
   ],
   "cell_type": "markdown",
   "metadata": {}
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "source": [
    "## Fit AutoReject"
   ],
   "cell_type": "markdown",
   "metadata": {}
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "cond1 = \"random/standard\"\n",
    "cond2 = \"random/deviant\"\n",
    "\n",
    "def get_mean_amplitudes(evokeds, window, picks = \"all\"):\n",
    "\n",
    "    means = []\n",
    "    if isinstance(evokeds, list):\n",
    "        for i, evoked in enumerate(evokeds):\n",
    "            evoked = evoked.copy().pick(picks)\n",
    "\n",
    "            _window = np.arange(evoked.time_as_index(window[0]),\n",
    "                                evoked.time_as_index(window[1]))\n",
    "\n",
    "            data = evoked.data[:, _window]\n",
    "            mean = data.mean()\n",
    "            means.append(mean)\n",
    "    else:\n",
    "        return get_mean_amplitudes([evokeds], window, picks)[0]\n",
    "\n",
    "    return means\n",
    "\n",
    "\n",
    "p_values = {num:[None] * N for num in nums}\n",
    "e_values = {num:[None] * N for num in nums}\n",
    "\n",
    "for i, num in enumerate(nums):\n",
    "    for n in N:\n",
    "\n",
    "        for i,id in enumerate(ids):\n",
    "            # get epochs\n",
    "            epochs = subjects_data[id][\"epochs\"]\n",
    "            evokeds = {cond: [] for cond in [cond1, cond2]}\n",
    "            \n",
    "            for cond in [cond1, cond2]:\n",
    "                # select epochs\n",
    "                s_epochs = epochs[cond]\n",
    "\n",
    "                # draw a random sample of epochs\n",
    "                idx = list(range(len(s_epochs)))\n",
    "                retain_idx = np.random.choice(idx, num)\n",
    "                drop_idx = set(idx) - set(retain_idx)\n",
    "                subsample_epochs = s_epochs.copy().drop(drop_idx)\n",
    "\n",
    "                # apply autoreject\n",
    "                subsample_epochs = ar.transform(subsample_epochs)\n",
    "                # average\n",
    "                evokeds[cond].append(subsample_epochs.average())\n",
    "\n",
    "            # calculate amplitude differenc (effect estimate)\n",
    "            diff_waves = [mne.combine_evoked([e1,e2], [1,-1]) for e1,e2 in zip(evokeds[\"random/standard\"], evokeds[\"random/deviant\"])]\n",
    "            mean_amplitudes = get_mean_amplitudes(diff_waves, peakwindow, picks = [\"mean\"]) \n",
    "            \n",
    "            # calculate p-value\n",
    "            # store value somewhere"
   ]
  }
 ]
}