import yaml
from yaml import SafeLoader
import os
from .helpers import dict_to_str

class Parameters:
    def __init__(self, yaml_path:str, referential_path:str):
        assert os.path.exists(yaml_path), f"YAML file not found: {yaml_path}"
        with open(yaml_path, 'r') as file:
            self.params = yaml.load(file, Loader=SafeLoader)
        assert os.path.exists(referential_path), f"Referential file not found: {referential_path}"
        with open(referential_path, 'r') as file:
            self.referential = yaml.load(file, Loader=SafeLoader)
        self.params["attributes"] = {}
        self.setup_check()
        self.setup_enrich()
        self.yaml_path = yaml_path
        self.referential_path = referential_path

    def __repr__(self):
        return f"Parameters(yaml_path='{self.yaml_path}', referential_path='{self.referential_path}')"
    
    def __str__(self):
        return dict_to_str(self.params)

    def setup_check(self):
        # Check the referential to ensure parameters are valid and to enrich them
        def check_values(param_dict, ref_dict, key, full_key):
            assert key in param_dict, f"Missing key '{key}' in parameters"
            assert key in ref_dict, f"Missing key '{key}' in referential"
            assert param_dict[key] in ref_dict[key]["values"], f"Invalid value '{param_dict[key]}' for key '{full_key}' (allowed: {ref_dict[key]['values']})"
        # Walk through the referential["dive_parameters"] and check each parameter that has a "values" key
        def check_parameters(param_dict, ref_dict, full_key=""):
            for key, ref_value in ref_dict.items():
                if isinstance(ref_value, dict) and "values" in ref_value:
                    check_values(param_dict, ref_dict, key, key if not full_key else full_key + "." + key)
                elif isinstance(ref_value, dict):
                    if key in param_dict and isinstance(param_dict[key], dict):
                        check_parameters(param_dict[key], ref_value, full_key + "." + key if full_key else key)
        check_parameters(self.params, self.referential["dive_parameters"])
    
    def setup_enrich(self):
        def enrich(ref_dict:dict, key:str, key_path:list=[]):
            if isinstance(ref_dict[key], dict) and "attributes" in ref_dict[key]:
                target = self.params["attributes"]
                params_value = self.params
                for k in key_path:
                    if k not in target:
                        target[k] = {}
                    target = target[k]
                    params_value = params_value[k]
                target[key] = ref_dict[key]["attributes"][params_value[key]]
            elif isinstance(ref_dict[key], dict):
                for sub_key in ref_dict[key]:
                    enrich(ref_dict[key], sub_key, key_path + [key])
        for key in self.referential["dive_parameters"]:
            enrich(self.referential["dive_parameters"], key)
    
    def get_parameter(self, key_path:list):
        target = self.params
        for key in key_path:
            if key not in target:
                raise KeyError(f"Key path {'.'.join(key_path)} not found in parameters")
            target = target[key]
        return target

