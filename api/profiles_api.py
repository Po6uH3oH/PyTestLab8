from api import routes

def get_my_profile(client):
    return client.get(routes.Routes.PROFILES_ME)

def get_profiles(client, limit=100, offset=0):
    return client.get(routes.Routes.PROFILES, params={"limit": limit, "offset": offset})

def get_profile_by_id(client, account_id):
    return client.get(routes.Routes.PROFILES_ITEM.format(account_id))
