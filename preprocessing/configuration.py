from ruamel.yaml import YAML


def load_configuration(filename):
    # Load config
    yaml = YAML(typ='unsafe')

    with open(filename) as file:
        configuration = yaml.load(file.read())

    return configuration
