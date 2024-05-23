import requests
from oauthlib.oauth1.rfc5849.endpoints import access_token
from requests_oauthlib import OAuth1Session
from api.models.users import User
import bcrypt
from config import settings

class AuthController:
    def __init__(self):
        self.consumer_key = settings.garmin_key
        self.consumer_secret = settings.garmin_secret


    def get_request_token(self, user_id):
        request_token_url = settings.garmin_oauth_request_url
        oauth = OAuth1Session(self.consumer_key, client_secret=self.consumer_secret)
        fetch_response = oauth.fetch_request_token(request_token_url)
        resource_owner_key = fetch_response.get('oauth_token')
        resource_owner_secret = fetch_response.get('oauth_token_secret')
        base_authorization_url = settings.garmin_base_authorization_url
        authorization_url = oauth.authorization_url(base_authorization_url)
        user = User(user_id=user_id)
        user.store_auth_keys(user_id, resource_owner_key, resource_owner_secret)
        return {'authorization_url': authorization_url}


    def get_garmin_access_tokens(self, user_id):
        user = User(user_id=user_id)
        tokens = user.get_garmin_user_tokens()
        if tokens['code'] == 0:
            tokens = tokens['tokens']
            oauth = OAuth1Session(self.consumer_key,
                                  client_secret=self.consumer_secret,
                                  resource_owner_key=tokens['resource_owner_key'],
                                  resource_owner_secret=tokens['resource_owner_secret'],
                                  verifier=tokens['oauth_verifier'])
            oauth_tokens = oauth.fetch_access_token(settings.garmin_access_token_url)
            access_token = oauth_tokens.get('oauth_token')
            access_token_secret = oauth_tokens.get('oauth_token_secret')
            msg = user.store_garmin_access_tokens(access_token, access_token_secret)
        else:
            msg = {'code': -1}
        return msg

    def store_oauth_verifier(self, user_id, oauth_token, oauth_verifier):
        user = User(user_id=user_id)
        store_oauth = user.store_oauth_verifier(user_id, oauth_token, oauth_verifier)
        if store_oauth['code'] == 0:
            store_access_tokens = user.get_garmin_user_tokens()
            garmin_user_id = self.get_garmin_user_id(user_id)
            user.store_garmin_user_id(garmin_user_id)
        return store_oauth

    def get_garmin_user_id(self, user_id):
        user_id_url = 'https://apis.garmin.com/wellness-api/rest/user/id'
        user = User(user_id=user_id)
        tokens = user.get_garmin_user_tokens()
        if tokens['code'] == 0:
            tokens = tokens['tokens']
            oauth = OAuth1Session(self.consumer_key,
                                  client_secret=self.consumer_secret,
                                  resource_owner_key=tokens['access_token'],
                                  resource_owner_secret=tokens['access_token_secret'])
            response = oauth.get(user_id_url)
            data = response.json()
            print(data)
            return data

    def login(self, user):
        print(user.email)
        print(user.pw)
        authenticated = user.authenticate_pw()
        if authenticated['code'] == 0:
            msg =  {'user_id': authenticated['user_id'],  "code":0}
        else:
            msg = {'code': -1, 'message': authenticated['message']}
        print(msg)
        return msg


if __name__ == '__main__':
    print(settings.garmin_key)
    auth = AuthController()
    user = User(user_id=1)
    guid = auth.get_garmin_user_id(1)
    user.store_garmin_user_id(guid['userId'])