from stereopoly.config import SUPPORTED_APP_VERSION

import semver

def generate_error(text):
  return {'error': text}

def check_app_version(f):
  def checker(api, **kwargs):
    if semver.compare(SUPPORTED_APP_VERSION, api) > 0:
      return generate_error('Unsupported app version'), 400
    return f(api=api, **kwargs)
  return checker