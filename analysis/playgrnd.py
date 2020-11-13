import numpy as np

def cronbachs_alpha(X):
    """
    X: ndarray (n_items * n_observations)
    """
    N = X.shape[0]
    corrs = np.corrcoef(X)

    r = 0
    return = (N * r) / (1 + (N - 1) * r)
