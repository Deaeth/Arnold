from .classes.UserAccount import UserAccount
import json

class GlobalFunctions:
    def __init__(self):
        return

    def check_block(id, command):
        print("id: {} Command: {}".format(id, command))
        user = UserAccount(int(id))

        for blocked_command in user.blocked_commands():
            print(blocked_command[0])
            if command == blocked_command[0]:
                return False
        else:
            return True

    def get_value(key):
        with open("C:/Users/frogg/Desktop/Arnold/cogs/hidden.json") as f:
            return json.load(f)[key]
