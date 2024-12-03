import os


def set_tokens():
    tokens = {}
    file_path = os.path.join("settings", "payments tokens.txt")
    with open(file_path) as file:
        for line in file.readlines():
            try:
                tokens.update({line.split("=")[0]: line.split("=")[1]})
            except:
                pass
    return tokens
