from api import routes

def login(client, username, password):
    return client.post(routes.Routes.AUTH_LOGIN, json={"username": username, "password": password})

def register(client, username, email, password):
    return client.post(routes.Routes.AUTH_REGISTER, json={"username": username, "email":email, "password": password})

def verify_token(client):
    return client.post(routes.Routes.AUTH_VERIFY)
