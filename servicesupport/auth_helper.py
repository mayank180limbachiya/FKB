import yaml
import msal
import os
import time

# Load the oauth_settings.yml file located in your app DIR
#stream = open('oauth_settings.yml', 'r')
#settings = yaml.load(stream, yaml.SafeLoader)

app_id= "b9f5eb44-66ea-4a07-b270-8c5c414ddf9f" 
app_secret= "uin8Q~FdaOw.oNjr~VcKY6U4wneOqpax494dKdxe" 
redirect= "http://localhost:8000/callback" 
scopes=["user.read"]
authority_data="https://login.microsoftonline.com/f8cdef31-a31e-4b4a-93e4-5f571e91255a"

def load_cache(request):
  # Check for a token cache in the session
  cache = msal.SerializableTokenCache()
  if request.session.get('token_cache'):
    cache.deserialize(request.session['token_cache'])
  return cache

def save_cache(request, cache):
  # If cache has changed, persist back to session
  if cache.has_state_changed:
    request.session['token_cache'] = cache.serialize()

def get_msal_app(cache=None):
  # Initialize the MSAL confidential client
  auth_app = msal.ConfidentialClientApplication(
    app_id,
    authority=authority_data,
    client_credential=app_secret,
    token_cache=cache)
  return auth_app

# Method to generate a sign-in flow
def get_sign_in_flow():
  auth_app = get_msal_app()
  return auth_app.initiate_auth_code_flow(
    scopes,
    redirect_uri=redirect)

# Method to exchange auth code for access token
def get_token_from_code(request):
  cache = load_cache(request)
  auth_app = get_msal_app(cache)

  # Get the flow saved in session
  flow = request.session.pop('auth_flow', {})
  result = auth_app.acquire_token_by_auth_code_flow(flow, request.GET)
  save_cache(request, cache)

  return result


def store_user(request, user):
  try:
    request.session['user'] = {
      'is_authenticated': True,
      'name': user['displayName'],
      'email': user['mail'] if (user['mail'] != None) else user['userPrincipalName'],
      'timeZone': user['mailboxSettings']['timeZone'] if (user['mailboxSettings']['timeZone'] != None) else 'UTC'
    }
  except Exception as e:
    print(e)

def get_token(request):
  cache = load_cache(request)
  auth_app = get_msal_app(cache)

  accounts = auth_app.get_accounts()
  if accounts:
    result = auth_app.acquire_token_silent(
      scopes,
      account=accounts[0])
    save_cache(request, cache)

    return result['access_token']

def remove_user_and_token(request):
  if 'token_cache' in request.session:
    del request.session['token_cache']

  if 'user' in request.session:
    del request.session['user']