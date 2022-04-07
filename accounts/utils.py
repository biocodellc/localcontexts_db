def get_users_name(user):
    if user.get_full_name():
        return user.get_full_name()
    else:
        return user.username