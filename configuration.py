from ruamel.yaml import YAML


def load_configuration():
    # Load config
    yaml=YAML(typ='unsafe')   # default, if not specfied, is 'rt' (round-trip)
    with open("configuration.yaml") as file:   
        configuration = yaml.load(file.read()  )
    
    return configuration