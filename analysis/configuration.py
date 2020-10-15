from ruamel.yaml import YAML


def load_configuration():
    # Load config
    yaml = YAML(typ='unsafe')
    with open("configuration.yaml") as file:
        configuration = yaml.load(file.read())

    return configuration