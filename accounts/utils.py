def get_users_name(user):
    if user is not None:
        if user.get_full_name():
            return user.get_full_name()
        else:
            return user.username
    else:
        return None