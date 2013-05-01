import json
import urllib

from pyramid.view import view_config
from pyramid.url import route_url
from pyramid.httpexceptions import HTTPFound

from velruse import login_url

from .models import DBSession, Attendance, Event


@view_config(route_name='home', renderer='templates/index.pt')
def index(request):
    event = DBSession.query(Event).filter(Event.active==True).first()
    return {
            'event':event,
            'login_url': login_url,
            'providers': request.registry.settings['login_providers'],
    }

@view_config(
    context='velruse.AuthenticationComplete',
#    route_name='register', 
    renderer='templates/register.pt')    
def login(request):
    
    context = request.context
    profile = context.profile
    network = context.provider_type
    data = {}
    
    if network == 'twitter':
        data['user_id'] = profile.get('displayName','')
        
        user_data = json.loads(urllib.urlopen(
                    'http://api.twitter.com/1/users/show.json?%s' %
                    urllib.urlencode(dict(screen_name=data['user_id']))).read())
        
        data['user_name'] = user_data.get('name','')
        data['url'] = 'https://twitter.com/#!/'+data['user_id'],
        data['image_url'] = user_data.get('profile_image_url',''),
        data['email'] = ''
        
    if network == 'facebook':
        data['user_id'] = profile['accounts'][0]['userid']
        data['user_name'] = profile.get('displayName','')
        data['email'] = profile['emails'][0]['value']
        data['image_url'] = 'https://graph.facebook.com/'+data['user_id']+'/picture'
        data['url'] = 'http://facebook.com/'+data['user_id']
    
    db_session = DBSession()    
    event = db_session.query(Event).filter(Event.active==True).first()
    attende = DBSession.query(Attendance).filter(Attendance.user_id==data['user_id']).first()
            
    tasks = ''
    if attende:
        tasks = attende.tasks
        data['email'] = attende.email
    
    data['tasks'] = tasks
    data['network'] = network
    
    return data

@view_config(route_name='register')
def register(request):
    if 'submit' in request.POST:
        db_session = DBSession()
        data = {}
        data['network'] = request.params['network']
        data['user_id'] = request.params['user_id']
        data['user_name'] = request.params['name']
        data['email'] = request.params['email']
        data['tasks'] = request.params['message']
        data['image_url'] = request.params['image_url']
        data['url'] = request.params['url']
        
        event = db_session.query(Event).filter(Event.active==True).first()
        attende = DBSession.query(Attendance).filter(Attendance.user_id==data['user_id']).first()
        data['event'] = event
                
        if attende:
            attende.user_name = data['user_name']
            attende.email = data['email']
            attende.tasks = data['tasks']
            attende.event_id = data['event'].id
    
        else:
            attende = Attendance(**data)
        
        db_session.add(attende)
            
        return HTTPFound(location = request.route_url('home'))    


@view_config(context='velruse.AuthenticationDenied')
def login_denied_view(request):
    return {
        'result': 'denied',
    }