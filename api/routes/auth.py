from fastapi import APIRouter, Request
from api.controllers.auth import AuthController
from api.models.users import User

router = APIRouter()
@router.post("/login")
async def login(user:User):
    auth = AuthController()
    login_status = auth.login(user)
    return login_status

@router.get("/oauth1/{user_id}")
def get_request_token(user_id: str):
    print(user_id)
    auth = AuthController()
    auth_tokens = auth.get_request_token(user_id)
    print(auth_tokens)
    return auth_tokens

@router.post("/oauth-verifier/")
async def get_request_token(request: Request):
    data = await request.json()
    print(data)
    auth = AuthController()
    oAuth_tokens = auth.store_oauth_verifier(user_id=data['user_id'], oauth_token=data['oAuthToken'],
                                             oauth_verifier=data['oAuthVerifier'])
    # print(oAuth_tokens)
    return oAuth_tokens

@router.post("/garmin_user")
def get_garmin_user_token():
    auth = AuthController()
    auth.get_garmin_user_token()


@router.post("/register")
async def register(user:User):
    result = user.create_user(user)
    return result