#%%
import numpy as np
import itertools as it
var =       {"ICA": {"yes":True, "no":False},
            "BaselineCorrection": {"yes":[-.1,0], "no":None},
            "Filtering": {"No Filtering":None, "Sussman":"sussman", "Widmann":"normal"},
            "WindowWidth": {"25 ms":0.025, "50 ms":0.050, "75 ms":0.075},
            "RejectionCriterion": {"75 µV":75e-6, "100 µV":100e-6, "125 µV":125e-6}}

# %%
combinations = it.product(*[set(v.keys()) for v in var.values()])
comb_list = [{o:p for o, p in zip(var.keys(), el)} for el in list(combinations)]
len(comb_list)
# %%
