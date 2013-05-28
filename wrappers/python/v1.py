# -*- coding: utf-8 -*-
"""
Requires requests package (for Python 2.5 or older, use "simplejson" instead of "json"
"""
import os
import urllib
import json
import requests
import sys

ENVIRONMENTS = {
    'eugeny': {
        'API_KEY': '6cc57fbdb46add230d3fd02c772e9ff4',
        'AUTH_CODE': '519a139e2769a16d0ac54965', # Must be requested to /passenger/v1/oauth2/auth/
        'REFRESH_TOKEN': 'YwqY9XsBJ7JTFGusHzZpWclNmLcIeaOR', # Must be copied from token code URL after authorization
        'ACCESS_TOKEN': '519a139e2769a16d0ac54964', # Must be copied from token code URL after authorization
        'USER_USERNAME': 'eugeny@tdispatch.com',
        'USER_PASSWORD': '',

        'CLIENT_ID': '2vvvND9JjG@tdispatch.com',
        'CLIENT_SECRET': 'DNlKiOBZAN1Tv79kalvdRSnQxDeIinVi',
        'REDIRECT_URL': '',
        'API_ROOT_URL': 'http://localhost:9500/passenger',
        },
    'mario': {
        'API_KEY': '6cc57fbdb46add230d3fd02c772e9ff4',
        'AUTH_CODE': '519db784b6c12165ca361102', # Must be requested to /passenger/v1/oauth2/auth/
        'REFRESH_TOKEN': 'pN4GJCfUxl6QZak3ew47XqJnrgl95cwX', # Must be copied from token code URL after authorization
        'ACCESS_TOKEN': '519db784b6c12165ca361101', # Must be copied from token code URL after authorization
        'USER_USERNAME': 'eugeny@tdispatch.com',
        'USER_PASSWORD': '12345',

        'CLIENT_ID': 'SHzIP5McTw@tdispatch.com',
        'CLIENT_SECRET': 'buYaP61y01445YYjz0n36ShA6yW7ToJy',
        'REDIRECT_URL': '',
        'API_ROOT_URL': 'http://localhost:9500/passenger',
        },
    'marcin': {
        'API_KEY': '6cc57fbdb46add230d3fd02c772e9ff4',
        'AUTH_CODE': '', # Must be requested to /passenger/v1/oauth2/auth/
        'REFRESH_TOKEN': '', # Must be copied from token code URL after authorization
        'ACCESS_TOKEN': '', # Must be copied from token code URL after authorization
        'USER_USERNAME': '',
        'USER_PASSWORD': '',

        'CLIENT_ID': '49ySP6iHVi@tdispatch.com',
        'CLIENT_SECRET': '4zDptcpczGRdkeioqwahHkwgWyr6csbw',
        'REDIRECT_URL': '',
        'API_ROOT_URL': 'https://t-dispatch.co/passenger',
        },
    'production': {
        'API_KEY': '1062d9111c892769afe1c2276e7b8f3a',
        'USER_USERNAME': '',
        'USER_PASSWORD': '',
        'AUTH_CODE': '', # Must be requested to /passenger/v1/oauth2/auth/
        'REFRESH_TOKEN': '', # Must be copied from token code URL after authorization
        'ACCESS_TOKEN': '', # Must be copied from token code URL after authorization

        'CLIENT_ID': 'QMoD2acIMb@tdispatch.com',
        'CLIENT_SECRET': '6oFcAiWExLEpukfql6r8WNnk6WT6sxQJ',
        'REDIRECT_URL': '',
        'API_ROOT_URL': 'https://api.tdispatch.com/passenger',
        },
    }
ENV = ENVIRONMENTS.get(sys.argv[1] if len(sys.argv) > 1 else 'staging')
if not ENV:
    sys.exit('Environment "%s" not found.' % sys.argv[1])

CLIENT_SCOPES = []
AUTH_URI = ENV['API_ROOT_URL'] + '/oauth2/auth'
TOKEN_URI = ENV['API_ROOT_URL'] + '/oauth2/token'
REVOKE_URI = ENV['API_ROOT_URL'] + '/oauth2/revoke'
SCOPE_URI = ENV['API_ROOT_URL']
API_KEY = ENV['API_KEY']


class RequestFailed(BaseException): pass


class PassengerAPIClient(object):
    auth_uri = AUTH_URI
    token_uri = TOKEN_URI
    scope_uri = SCOPE_URI
    revoke_uri = REVOKE_URI
    api_key = API_KEY
    base_url = None
    client_id = None
    client_secret = None
    username = None
    auth_code = None # Must be informed manually
    refresh_token = None # Must be informed manually
    access_token = None # Must be informed manually
    

    def __init__(self, client_id, client_secret, redirect_url, base_url=ENV['API_ROOT_URL']+"/v1/"):
        """Parameters:
        - client_id: supplied by TDispatch app's registration
        - client_secret: supplied by TDispatch app's registration"""

        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url

    def get_token_request_url(self):
        params = {
            'response_type':'code',
            'client_id':self.client_id,
            'redirect_uri':self.redirect_url,
            'scope':' '.join(CLIENT_SCOPES),
            'key':self.api_key,
            #'state':,
            }
        return '%s?%s' % (self.auth_uri, urllib.urlencode(params))

    def get_refresh_token(self):
        resp = requests.post(self.token_uri, {
            'code':self.auth_code,
            'client_id':self.client_id,
            'client_secret':self.client_secret,
            'redirect_uri':'',
            'grant_type':'authorization_code',
            })
        return resp.content

    def get_access_token(self):
        resp = requests.post(self.token_uri, {
            'refresh_token':self.refresh_token,
            'client_id':self.client_id,
            'client_secret':self.client_secret,
            'grant_type':'refresh_token',
            })
        return resp.content

    def revoke_access_token(self):
        resp = requests.post(self.revoke_uri, {
            'grant_type':'access_token',
            'client_id':self.client_id,
            'client_secret':self.client_secret,
            'refresh_token':self.refresh_token,
            'access_token':self.access_token,
            })
        return resp.content
    
    def revoke_refresh_token(self):
        resp = requests.post(self.revoke_uri, {
            'grant_type':'refresh_token',
            'client_id':self.client_id,
            'client_secret':self.client_secret,
            'refresh_token':self.refresh_token,
            })
        return resp.content

    def request(self, method, url, data=None, api_key=None):
        print '\n', '-'*40
        print '/%s' % url
        url = self.base_url + url
        url += '&' if '?' in url else '?'
        url += 'key=' + api_key if api_key else 'access_token=' + self.access_token
        body = json.dumps(data) if data else ''

        if method.upper() == 'POST':
            resp = requests.post(url, body)
        elif method.upper() == 'PUT':
            resp = requests.put(url, body)
        elif method.upper() == 'DELETE':
            resp = requests.delete(url, body)
        else:
            resp = requests.get(url + ('&' + urllib.urlencode(body) if body else ''))

        if resp.headers['content-type'].startswith('application/json'):
            print resp.content, '\n'
            return json.loads(resp.content)
        elif resp.headers['content-type'].startswith('application/pdf'):
            print '<application/pdf> content'
            return resp.content 
        else:
            raise RequestFailed('Method "%s" returned: %s (%s)' % (url,resp.content,resp.status_code))
        
    # Method for API

    def api_info(self):
        return self.request('GET','api-info')

    # Methods for the Booking
    
    def passenger_bookings(self, **kwargs):
        return self.request('GET', 'bookings?'+urllib.urlencode(kwargs))
    
    def passenger_booking_create(self, **kwargs):
        return self.request('POST','bookings', kwargs)
    
    def passenger_booking_track(self, **kwargs):
        return self.request('POST', 'bookings/track', kwargs)
    
    def passenger_booking_update(self, pk, **kwargs):
        return self.request('POST','bookings/%s' % pk, kwargs)
    
    def passenger_booking_cancel(self, pk, **kwargs):
        return self.request('POST', 'bookings/%s/cancel' % pk, kwargs)
    
    def passenger_booking_receipt(self, url):
        return self.request('GET', url)
    
    
    # Methods for the Regular locations
    
    def passenger_regular_locations(self, **kwargs):
        return self.request('GET', 'locations?'+urllib.urlencode(kwargs))
    
    def passenger_regular_location_create(self, **kwargs):
        return self.request('POST', 'locations', kwargs)
    
    def passenger_regular_location_get(self, pk):
        return self.request('GET', 'locations/%s' % pk)
    
    def passenger_regular_location_update(self, pk, **kwargs):
        return self.request('POST', 'locations/%s' % pk, kwargs)
    
    def passenger_regular_location_delete(self, pk):
        return self.request('POST', 'locations/%s/delete' % pk)
    
    def passenger_location_search(self, **kwargs):
        return self.request('GET', 'locations/search?'+urllib.urlencode(kwargs))
    
    def passenger_location_get_fare(self, **kwargs):
        return self.request('POST', 'locations/fare', kwargs)
    
    # Methods for the Regular journeys
    
    def passenger_regular_journeys(self, **kwargs):
        return self.request('GET', 'journeys?'+urllib.urlencode(kwargs))
    
    def passenger_regular_journeys_create(self, **kwargs):
        return self.request('POST', 'journeys', kwargs)
    
    def passenger_regular_journeys_get(self, pk):
        return self.request('GET', 'journeys/%s' % pk)
    
    def passenger_regular_journeys_update(self, pk, **kwargs):
        return self.request('POST', 'journeys/%s' % pk, kwargs)
    
    def passenger_regular_journeys_delete(self, pk):
        return self.request('POST', 'journeys/%s/delete' % pk)
    
    def drivers_nearby(self, **kwargs):
        return self.request('POST', 'drivers/nearby', kwargs)
    
    def account_fleetdata_get(self):
        return self.request('GET', 'accounts/fleetdata')
    
    def account_preferences_get(self):
        return self.request('GET', 'accounts/preferences')
    
    def account_preferences_update(self, **kwargs):
        return self.request('POST', 'accounts/preferences', kwargs)
    
    def account_create(self, **kwargs):
        return self.request('POST', 'accounts', kwargs, api_key=self.api_key)
    
    def cartype_list(self):
        return self.request('GET', 'vehicletypes')


api = PassengerAPIClient(ENV['CLIENT_ID'], ENV['CLIENT_SECRET'], ENV['REDIRECT_URL'])
api.auth_code = ENV.get('AUTH_CODE')
api.refresh_token = ENV.get('REFRESH_TOKEN')
api.access_token = ENV.get('ACCESS_TOKEN')
api.username = ENV.get('USER_USERNAME')
api.password = ENV.get('USER_PASSWORD')

print '-'*40
if api.access_token:
    print 'Testing the API methods'

    #api.revoke_access_token()
    #api.revoke_refresh_token()
    #sys.exit(0)

    # API info
    api.api_info()
    api.passenger_bookings(limit=1)
    api.passenger_bookings(offset=1,limit=1)
    api.passenger_bookings(pickup_time='2012-11-08T17:56:46Z')
    api.passenger_bookings(status='incoming,draft')
    
    car_types = api.cartype_list()['car_types']
    
    booking = api.passenger_booking_create(
        customer={'name':'Andy Warhol', 'phone':'+49123470416', 'email':'andy@tdispatch.com'},
        pickup_time='2013-05-07T10:30:00-02:00',
        return_pickup_time='2013-05-09T10:30:00-02:00',
        pickup_location={'address':u'Grüntaler strasse 11', 'location':{'lat':52.552037,'lng':13.387291}, 'postcode':'13357'},
        dropoff_location={'address':u'Wöhlertstraße 10', 'location':{'lat':52.53673,'lng':13.379416}, 'postcode':'10115'},
        way_points=[{'address':u'Voltastraße 100', 'location':{'lat':52.542381,'lng':13.392463}, 'postcode':'13355'}],
        extra_instructions='The three guys in blue.',
        luggage=5,
        passengers=3,
        payment_method='cash',
        prepaid=False,
        status='incoming',
        vehicle_type=car_types[-1]['pk'] if len(car_types) else None 
    )['booking']

    api.passenger_booking_update(pk=booking['pk'], luggage=3)
    api.passenger_booking_cancel(pk=booking['pk'], description="My hamster died. Don't want to go to the party anymore.")
    api.passenger_booking_receipt(booking['receipt_url'])
    
    api.passenger_location_get_fare(
        pickup_location={"lat":52.12588, "lng":11.61150},
        dropoff_location={"lat":52.5373399193,"lng":13.378729824}
    )
    api.passenger_regular_locations()
    reg_loc = api.passenger_regular_location_create(
        name="Home, sweet home",
        keywords="magdeburg,home, Eugen",
        location={'address':u'Lessingstraße 23', 'location':{'lat':52.12588,'lng':11.61150}, 'postcode':'39108'}
    )['location']
    api.passenger_regular_location_get(reg_loc['pk'])
    api.passenger_regular_location_update(pk=reg_loc['pk'], name="German home")
    api.passenger_regular_location_delete(pk=reg_loc['pk'])
    
    api.passenger_regular_journeys()
    journey_create_params = {
        "name": "Magdeburg to Berlin", 
        "from_regular_location_id": "515470002769a110b26260bd",
        "to_regular_location_id": "5159a05d2769a10af21c26d4"
    }
    reg_journey = api.passenger_regular_journeys_create(**journey_create_params)['journey']
    api.passenger_regular_journeys_get(reg_journey['pk'])
    api.passenger_regular_journeys_update(pk=reg_journey['pk'], name="German home")
    api.passenger_regular_journeys_delete(pk=reg_journey['pk'])
    api.drivers_nearby(location={'lng':13.378729824,'lat':52.5373399193}, radius=2, limit=15)
    api.account_fleetdata_get()
    api.account_preferences_get()
    api.account_preferences_update(
        birth_date = '1985-10-21T00:00:00',
        location={'address':u'Lessingstraße 23', 'location':{'lat':52.12588,'lng':11.61150}, 'postcode':'39108'},
        use_account_location_as_pickup = True,
        first_name = 'Eugen'
    )
    
    api.passenger_location_search(
        q='lessing'
    )
    
    api.passenger_booking_track(
        booking_pks = [booking['pk']]
    )
elif api.refresh_token:
    print 'Getting new access token'
    print api.get_access_token()
elif api.auth_code:
    print 'Getting refresh token with auth code'
    print api.get_refresh_token()
elif api.username:
    print 'Requesting Passenger authorization'
    print api.get_token_request_url()
else:
    print 'Creating new passenger'
    print api.account_create(
        first_name = 'Eugen',
        last_name = 'von Shevchik',
        phone = '+380975461272',
        email = 'eugeny5@tdispatch.com',
        password = '12345',
        client_id = ENV['CLIENT_ID'],
    )
print '-'*40

