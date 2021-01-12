import parsl
from preprocessing.parsl_config import pconfig
from module import my_app

parsl.load(pconfig)

print(my_app().result())

