def dict_to_str(d, string="", indent=0):
    for key, value in d.items():
        if isinstance(value, dict):
            string += " " * indent + f"{key}:\n"
            string += dict_to_str(value, "", indent + 4)
        else:
            string += " " * indent + f"{key}: {value}\n"
    return string


def print_dict(d, indent=0):
    if not isinstance(d, dict):
        print(d)
        return
    else:
        string = dict_to_str(d, "", indent)
        print(string)
