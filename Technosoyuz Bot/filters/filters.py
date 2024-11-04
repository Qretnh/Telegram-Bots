
def filter_id_in_users(workflow_data: dict, id: int):
    if id in workflow_data.keys():
        return True
    return False
