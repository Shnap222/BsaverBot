import yaml


class YamlHandler:

    @staticmethod
    def yaml_loader(path):
        """Dumps data to a YAML file"""
        with open(path, "r") as file:
            data = yaml.safe_load(file)
        return data

    @staticmethod
    def yaml_dump(path, data):
        """Dumps data to a YAML file"""
        with open(path, 'w') as file:
            yaml.dump(data, file)