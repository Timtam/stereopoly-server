from stereopoly.config import SUPPORTED_APP_VERSION

import semver

def generate_error(text):
  return {'error': text}

def check_app_version(f):
  def checker(api, **kwargs):
    try:
      if semver.compare(SUPPORTED_APP_VERSION, api) > 0:
        return generate_error(_('Unsupported app version')), 400
    except ValueError:
      return generate_error(_('Error parsing app version')), 400
    return f(api=api, **kwargs)
  return checker