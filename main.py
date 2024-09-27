import http.cookies
import json
import logging
from charts import Chart
from server import Server
from typing import Optional
from databaser import ChannelDatabase, UserDatabase, User, ChartsDatabase
from channel import Channel

server: Server = Server()
admin: User = User('grigory', '12345678ve', True)
user_db: UserDatabase = UserDatabase('db/users.db')
channels_db: ChannelDatabase = ChannelDatabase('db/channels.db')
charts_db: ChartsDatabase = ChartsDatabase('db/charts.db')
test_chart = Chart('test', [
    ('2010', 100),
    ('2011', 20),
    ('2012', 30),
    ('2013', 47),
    ('2014', 50),
    ('2015', 53),
    ('2016', 11),
    ('2017', 80),
    ('2018', 65),
    ('2019', 19)
])
cookie = http.cookies.SimpleCookie()

def main():
    global server
    print(user_db.get_all_users())
    print(charts_db.get_all_charts())
    print(channels_db.get_all_channels())
    channels_db.add_channel(Channel('test_channel', 1))
    user_db.add_user(admin)
    charts_db.update_chart(1, test_chart)
    server.run()

@server.route('/')
def index() -> str:
    return open('web/html/index.html').read()


@server.route('/signup')
def signup(args: Optional[dict[str, str]] = {}) -> str:
    if args != {}:
        user_db.register_user(args['username'], args['password'])
        print("Start cookie")
        cookie['name'] = "auth"
        cookie['username'] = args['username']
        cookie['password'] = args['password']
        cookie['admin'] = False
        server.set_cookie(cookie)
        print("End cookie")
        return server.redirect('/profile')
    return open('web/html/signup.html').read()

@server.route('/login')
def login(args: Optional[dict[str, str]] = {}) -> str:
    if args != {}:
        if user_db.authenticate_user(args['username'], args['password']):
            logging.info(f"Login success: {args}")
            cookie: http.cookies.SimpleCookie = http.cookies.SimpleCookie()
            user: User = user_db.get_user(args['username'])
            logging.info(f"User: {user}, type: {type(user)}")
            server.clear_session_cookies()
            cookie['username'] = user.username
            cookie['password'] = user.password
            cookie['admin'] = user.is_admin
            cookie['name'] = "auth"
            if user.is_admin:
                users_cookie = http.cookies.SimpleCookie()
                users_cookie['name'] = "users"
                for id, user in enumerate(user_db.get_all_users()):
                    users_cookie[f"user_{id}"] = {
                        "username": user.username,
                        "password": user.password,
                        "is_admin": user.is_admin
                    }
                # server.set_cookie(users_cookie)
            logging.info(f"Cookie: {cookie}")
            server.set_cookie(cookie)
            return server.redirect('/profile')
        else:
            logging.info(f"Login failed: {args}")
            return "Wrong username or password"
    return open('web/html/login.html').read()


@server.route('/getuser')
def getuser(args: Optional[dict[str, str]] = {}) -> str:
    if args.get('name'):
        user = user_db.get_user(args['name'])
        if user:
            return json.dumps({
                "id": user.id,
                "username": user.username,
                "password": user.password,
                "is_admin": user.is_admin
            })
        else:
            return "User not found"
    elif args.get('id'):
        user = user_db.get_user_by_id(int(args['id']))
        if user:
            return json.dumps({
                "id": user.id,
                "username": user.username,
                "password": user.password,
                "is_admin": user.is_admin
            })
        else:
            return "User not found"
    return "Please provide username as a query parameter"

@server.route('/adddata')
def add_data(args: Optional[dict[str, str]] = {}) -> str:
    if args.get('channel_id') and args.get('chart_name') and args.get('key') and args.get('value'):
        chart: Chart = charts_db.get_chart(int(args['channel_id']), args['chart_name'])
        if not chart:
            chart = Chart(args['chart_name'], [])
        key = args['key']
        value = int(args['value']) if args.get('value').isalnum() else 0
        chart.add_data(key, value)
        logging.info(f'Data added to chart: {chart}')
        charts_db.update_chart(int(args['channel_id']), chart)
        return "Data added"
    return "Please provide chart_id and data as query parameters"

@server.route('/cleardata')
def clear_data(args: Optional[dict[str, str]] = {}) -> str:
    if args.get('channel_id') and args.get('chart_name'):
        chart: Chart = charts_db.get_chart(int(args['channel_id']), args['chart_name'])
        if chart:
            chart.data.clear()
            charts_db.update_chart(int(args['channel_id']), chart)
            return "Data cleared"
        else:
            return "Chart not found"
    return "Please provide channel_id and chart_name as query parameters"


@server.route('/addchart')
def add_chart(args: Optional[dict[str, str]] = {}) -> str:
    if args.get('channel_id') and args.get('chart_name'):
        chart = Chart(args['chart_name'], [])
        charts_db.add_chart(int(args['channel_id']), chart)
        return "Chart added"
    return "Please provide channel_id and chart_name as query parameters"

@server.route('/getchannels')
def getchannels(args: Optional[dict[str, str]] = {}) -> str:
    if args.get('owner_id'):
        channels = channels_db.get_owner_channels(int(args['owner_id']))
        ret = {}
        for channel in channels:
            print(channel)
            ret[channel.id] = {
                "name": channel.name,
                "owner_id": channel.owner_id
            }
        return json.dumps(ret)
    if args.get('id'):
        channel = channels_db.get_channel_by_id(int(args['id']))
        if channel:
            return json.dumps({
                "id": channel.id,
                "name": channel.name,
                "owner_id": channel.owner_id
            })
        else:
            return "Channel not found"
    if args.get('name'):
        channel = channels_db.get_channel(args['name'])
        if channel:
            return json.dumps({
                "id": channel.id,
                "name": channel.name,
                "owner_id": channel.owner_id
            })
        else:
            return "Channel not found"
    channels: list[Channel] = channels_db.get_all_channels()
    ret = {}
    for channel in channels:
        ret[int(channel.id)] = {
            "name": channel.name,
            "owner_id": channel.owner_id
        }
    return json.dumps(ret)
        

@server.route('/channels')
def channels(args: Optional[dict[str, str]] = {}) -> str:

    return open('web/html/channels.html').read()

@server.route('/addchannel')
def addchannel(args: Optional[dict[str, str]] = {}) -> str:
    if args.get('name') and args.get('owner_id'):
        channels_db.add_channel(Channel(args['name'], int(args['owner_id'])))
        return server.redirect('/channels')
    return "Please provide name and owner_id as query parameters"

@server.route('/profile')
def profile(args, cookies) -> str:
    if not cookies:
        logging.info(f"No cookies")
        logging.info(f"Cookies: {cookies}")
        return server.redirect('/login')
    logging.info(f"Profile cookie: {cookie}")
    return open('web/html/profile.html').read()

@server.route('/getusers')
def getusers() -> str:
    users = user_db.get_all_users()
    return json.dumps([user.__dict__ for user in users])

@server.route('/getcharts')
def getcharts(args: Optional[dict[str, str]] = {}) -> str:
    if args == {}:
        return "Please provide channel_id or channel_name as a query parameter"
    charts = {}
    if args.get('channel_id'):
        charts = charts_db.get_channel_charts(int(args['channel_id']))
    elif args.get('channel_name'):
        charts = charts_db.get_channel_charts(channels_db.get_channel_id(args['channel_name']))
    ret = {}
    for name, chart in charts.items():
        ret[chart.name] = chart.data
    return json.dumps(ret)

@server.route('/ownerchannels')
def ownerchannels(args) -> str:
    if args.get('username'):
        channels = channels_db.get_owner_channels(user_db.get_user_id(args['username']))
        ret = {}
        for channel in channels:
            ret[int(channel.id)] = {
                "name": channel.name,
                "owner_id": channel.owner_id
            }
        return json.dumps(ret)
    elif args.get('id'):
        channels = channels_db.get_owner_channels(int(args['id']))
        ret = {}
        for channel in channels:
            ret[int(channel.id)] = {
                "name": channel.name,
                "owner_id": channel.owner_id
            }
        return json.dumps(ret)
    return "Please provide username as a query parameter"

@server.route('/setadmin')
def setadmin(args) -> str:
    if args.get('username') and args.get('admin'):
        logging.info(f"Set admin: {args}")
        args['admin'] = True if args.get('admin') == 'true' else False
        user_db.update_user(User(args['username'], user_db.get_user(args['username']).password, args['admin']))
        return "{\"success\": true}"
    return "{\"success\": false}"

if __name__ == "__main__":
    main()