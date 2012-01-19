import cgi
import json
import urllib
import urlparse

from pyramid.view import view_config
from pyramid.url import route_url
from pyramid.httpexceptions import HTTPFound

import oauth2 as oauth

from .models import DBSession, Attendance, Event

TWITTER_CONSUMER_KEY = 'z9L2bzVT65BPsqs3uyJRvA'
TWITTER_CONSUMER_SECRET = 'OFeD4Aie5pJUE6kRBeRI530Xlc0AqYRsQ8uzQhgB8'

TWITTER_REQUEST_TOKEN_URL = 'http://twitter.com/oauth/request_token'
TWITTER_ACCESS_TOKEN_URL = 'http://twitter.com/oauth/access_token'
TWITTER_AUTHORIZE_URL = 'http://twitter.com/oauth/authorize'


@view_config(route_name='home', renderer='templates/index.pt')
def index(request):
    event = DBSession.query(Event).filter(Event.active==True).first()
    return {'event':event}

@view_config(route_name='add', renderer='templates/register.pt')    
def register(request):
    session = request.session
    
    if 'facebook' in session:
        network = 'facebook'
    if 'twitter' in session:
        network = 'twitter'
    
    
    if 'submit' in request.POST:
        db_session = DBSession()
        event = db_session.query(Event).filter(Event.active==True).first()
        
        data = session[network]
        data['network'] = network
        data['user_name'] = request.params['name']
        data['email'] = request.params['email']
        data['tasks'] = request.params['message']
        data['event'] = event
        
        attende = DBSession.query(Attendance).filter(Attendance.user_id==data['user_id']).first()
        if attende:
            attende.user_name = data['user_name']
            attende.email = data['email']
            attende.tasks = data['tasks']
    
        else:
            attende = Attendance(**data)
        
        db_session.add(attende)
            
        return HTTPFound(location = request.route_url('home'))    
    
    user_name = session[network]['user_name']
    email = session[network]['email']
    
    return {'user_name':user_name, 'email':email}

@view_config(route_name='facebook_login')    
def facebook_login_view(request):
    config = request.registry.settings
    FACEBOOK_SCOPE = config.get('facebook.scope')
    FACEBOOK_APP_ID = config.get('facebook.app_id')
    FACEBOOK_APP_SECRET = config.get('facebook.app_secret')
    
    referer = request.params.get('referer', route_url('add', request))
    if referer.startswith(route_url('facebook_login', request)):
        referer = route_url('add', request)
        
    args = dict(client_id=FACEBOOK_APP_ID, scope=FACEBOOK_SCOPE,
            redirect_uri=route_url('facebook_login', request,
                                   _query=[('referer', referer)]))
    verification_code = request.params.get('code', None)
    if not verification_code:
        return HTTPFound(location='https://graph.facebook.com/oauth/authorize?%s'
                         % urllib.urlencode(args))

    args['client_secret'] = FACEBOOK_APP_SECRET
    args['code'] = request.params.get('code', '')
    access_token_url = ('https://graph.facebook.com/oauth/access_token?%s' %
                        urllib.urlencode(args))
    response = cgi.parse_qs(urllib.urlopen(access_token_url).read())
    access_token = response['access_token'][-1]
    session = request.session
    if not access_token:
        session.flash(u'Facebook login error', queue='flash_error')
        session['facebook'] = None
        return HTTPFound(location=route_url('home', request))
    facebook_user = json.loads(urllib.urlopen(
            'https://graph.facebook.com/me?%s' %
            urllib.urlencode(dict(access_token=access_token))).read())
    session['facebook'] = { 'token':access_token,
                            'token_secret':'',
                            'user_id':facebook_user.get(u'id', u''),
                            'user_name':facebook_user.get(u'name', u''),
                            'url':facebook_user.get(u'link', u''),
                            'email':facebook_user.get(u'email', u''),
                            'image_url':'https://graph.facebook.com/'+facebook_user.get(u'id')+'/picture',}
                            
    return HTTPFound(location=referer)
    


@view_config(route_name='twitter_login')
def twitter_login_view(request):
    config = request.registry.settings
    TWITTER_CONSUMER_SECRET = config.get('twitter.consumer_secret')
    TWITTER_CONSUMER_KEY    = config.get('twitter.consumer_key')
    consumer = oauth.Consumer(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    
    referer = request.params.get('referer', route_url('add', request))
    
    if referer.startswith(route_url('twitter_login', request)):
        referer = route_url('add', request)

    session = request.session
    if session.get('twitter_access_token', u'') and session.get(
            'twitter_access_token_secret', u''):
        return HTTPFound(location=referer)

    twitter_request_token = session.get('twitter_request_token', u'')
    session['twitter'] = None
    if not twitter_request_token:
        twitter_callback_uri = route_url('twitter_login', request,
                _query=[('referer', referer)])
        client = oauth.Client(consumer)
        body = urllib.urlencode(dict(oauth_callback=twitter_callback_uri))
        resp, content = client.request(TWITTER_REQUEST_TOKEN_URL, 'POST',
                body=body)
        if resp['status'] != '200':
            session.flash(u'Twitter login error', queue='flash_error')
            session['twitter'] = None
            return HTTPFound(location=route_url('home', request))
        else:
            twitter_request_token = dict(urlparse.parse_qsl(content))
            session['twitter_request_token'] = twitter_request_token
            return HTTPFound(location='%s?oauth_token=%s' % (TWITTER_AUTHORIZE_URL,
                    twitter_request_token['oauth_token']))

    # redirect back from Twitter
    token = oauth.Token(twitter_request_token['oauth_token'],
                        twitter_request_token['oauth_token_secret'])
    twitter_oauth_verifier = request.params.get('oauth_verifier', '')
    if not twitter_oauth_verifier:
        session.flash(u'Twitter login error', queue='flash_error')
        session['twitter'] = None
        return HTTPFound(location=route_url('home', request))

    token.set_verifier(twitter_oauth_verifier)
    client = oauth.Client(consumer, token)
    resp, content = client.request(TWITTER_ACCESS_TOKEN_URL, "POST")
    access_token = dict(urlparse.parse_qsl(content))
    
    twitter_user = json.loads(urllib.urlopen(
            'http://api.twitter.com/1/users/show.json?%s' %
            urllib.urlencode(dict(screen_name=access_token['screen_name']))).read())
        
    session['twitter'] = {  'token': access_token['oauth_token'],
                            'token_secret': access_token['oauth_token_secret'],
                            'user_id': access_token['screen_name'],
                            'user_name': twitter_user.get('name',''),
                            'url': 'https://twitter.com/#!/'+access_token['screen_name'],
                            'email': '',
                            'image_url': twitter_user.get('profile_image_url',''),
                        }
    
    
    return HTTPFound(location=referer)
    