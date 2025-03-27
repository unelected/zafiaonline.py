def get_user_attributes(client):
    for key, value in client.__dict__.items():
        if not callable(value):
            setattr(client, key, value)