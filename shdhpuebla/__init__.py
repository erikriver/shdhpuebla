from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from sqlalchemy import engine_from_config

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    
    session_factory = UnencryptedCookieSessionFactoryConfig( settings['cookie.secret'], )
    
    providers = settings.get('login_providers', '')
    providers = filter(None, [p.strip()
                       for line in providers.splitlines()
                       for p in line.split(', ')])
    settings['login_providers'] = providers
    
    config = Configurator(settings=settings, session_factory=session_factory )
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    if 'facebook' in providers:
        config.include('velruse.providers.facebook')
        config.add_facebook_login_from_settings(prefix='facebook.')
    
    if 'twitter' in providers:
        config.include('velruse.providers.twitter')
        config.add_twitter_login_from_settings(prefix='twitter.')
    
    config.add_route('home', '/')
    config.add_route('register', 'register')
    
#    config.add_route("facebook_login", "/facebook/login")
#    config.add_route("twitter_login", "/twitter/login")
    
    config.scan()
    return config.make_wsgi_app()

