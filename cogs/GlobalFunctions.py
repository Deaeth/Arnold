from .classes.UserAccount import UserAccount

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
