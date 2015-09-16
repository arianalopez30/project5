#-----------------------------------------
#Imports
#Imports everything I need to get the application to work
#-----------------------------------------
from flask import Flask
app = Flask(__name__)

from functools import wraps

#importing all database needs
from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, jsonify
app = Flask(__name__)

#database connection information
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, User, Category, Item
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

from flask import session as login_session
import random, string
#oauth imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME ="Catalog"

#-----------------------------------------
#Name: login_required
#Description: checks to see if user is logged in
#-----------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('main'))
        return f(*args, **kwargs)
    return decorated_function

#-----------------------------------------
#Name: showLogin
#Description: Creates anti-forgery state token
#-----------------------------------------
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)

#-----------------------------------------
#Name: gconnect
#Description: authenticates a user
#-----------------------------------------
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    #check if user already exists
    email = login_session['email']
    if session.query(User).filter_by(email=email).count():
        user_id = get_user_id(email)
    else:
    #add user to database
        user_id = create_user(login_session)
    
    login_session['user_id'] = user_id
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

#-----------------------------------------
#Name: create_user
#Description: creates a user
#-----------------------------------------
def create_user(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

#-----------------------------------------
#Name: getUserInfo
#Description: gets user info based on user_id
#-----------------------------------------
def get_user_info(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

#-----------------------------------------
#Name: getUserID
#Description: gets userid based on email
#-----------------------------------------
def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None



#-----------------------------------------
#Name: gdisconnect
#Description: disconnects a user
#-----------------------------------------
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


#-----------------------------------------
#Name: main
#Description: The main web page
#-----------------------------------------
@app.route('/')
@app.route('/catalog/')
def main():
	#get all categories for the navigation side
	categories = session.query(Category).all()
	#get all items for the main part of the html
	all_items = session.query(Item).all()

	#check if person is logged in
	if 'username' not in login_session:
		return render_template('view_catalog.html', categories = categories, items = all_items)
	return render_template('catalog.html', categories = categories, items = all_items)

#-----------------------------------------
#Name: view_category_items
#Description: View items based on what category was selected
#There is a specific page for people logged in and people not logged in
#-----------------------------------------
@app.route('/catalog/<int:category_id>/')
def view_category_items(category_id):
	#get all categories for the navigation side
	categories = session.query(Category).all()

	#get the items tied to the category that was selected
	#category= session.query(Category).filter_by(id = category_id).one()
	items = session.query(Item).filter_by(category_id = category_id).all()
	if 'username' not in login_session:
		return render_template('view_category_items.html', categories = categories, items = items)
	return render_template('category_items.html', categories = categories, items = items)



#-----------------------------------------
#Name: add_item
#Description: adds a new item
#-----------------------------------------
@app.route('/add/', methods= ['GET', 'POST'])
@login_required
def add_item():
    categories = session.query(Category).all()
    email = login_session['email']
    user_info = session.query(User).filter_by(email=email).one()
	
    if request.method == 'POST' and ('username' in login_session):
        newItem = Item(name=request.form['name'], description=request.form['description'], category_id=request.form['category_dropdown'], user_id = user_info.id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('main'))
    else:
        categories = session.query(Category).all()
        return render_template('add.html', categories = categories)

#-----------------------------------------
#Name: view_item
#Description: View a specific item
#There is a specific page for people logged in and people not logged in
#-----------------------------------------
@app.route('/catalog/<int:category_id>/<int:item_id>/')
def view_item(category_id, item_id):
	#get all categories for the navigation side
	categories = session.query(Category).all()

	#get the info on the item that was selected
	item = session.query(Item).filter_by(id = item_id).one()
	if 'username' not in login_session:
		return render_template('view_item.html', categories = categories, item = item)

	return render_template('item.html', categories = categories, item = item)

#-----------------------------------------
#Name: delete_item
#Description: will delete a specific item
#-----------------------------------------
@app.route('/delete/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(id = item_id).one()
    if request.method == 'POST' and ('username' in login_session) and (item.user_id == login_session['user_id']):
        session.delete(item)
        session.commit()
        return redirect(url_for('main'))
    elif (item.user_id != login_session['user_id']):
        return render_template('delete_no_permissions.html', categories = categories)
    elif ('username' in login_session) and (item.user_id == login_session['user_id']):
        return render_template('delete.html', categories=categories, item = item)
    else:
        return redirect(url_for('main'))


#-----------------------------------------
#Name: edit_item
#Description: will edit a specific item
#-----------------------------------------
@app.route('/edit/<category_id>/<item_id>/', methods=['GET', 'POST'])

def edit_item(category_id, item_id):
	#get all categories for the navigation side
    categories = session.query(Category).all()
  
	#get the info on the item that was selected
    item = session.query(Item).filter_by(id = item_id).one()

    if request.method == 'POST' and ('username' in login_session) and (item.user_id == login_session['user_id']):
        #gets the edit info from the form
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category_dropdown']:
            item.category_id = request.form['category_dropdown']
        session.add(item)
        session.commit()
        return redirect(url_for('main'))
    elif (item.user_id != login_session['user_id']):
        return render_template('edit_no_permissions.html', categories = categories)
    elif ('username' in login_session) and (item.user_id == login_session['user_id']):
        return render_template('edit_item.html', categories=categories, item = item)
    else:
        return redirect(url_for('main'))


#-----------------------------------------
#Name: catalog_json
#Description: will return a json file
#-----------------------------------------
@app.route('/catalog/json')
def catalog_json():
    catalog = session.query(Category)
    items = session.query(Item)

    outer_dictionary = {}
    inner_dictionary = {}

    outer_dictionary["category"] = [i.serialize for i in catalog]
    inner_dictionary["items"] = [i.serialize for i in items]
    outer_dictionary["items"] = inner_dictionary
    #return jsonify(Category=[i.serialize for i in catalog])
    return jsonify(outer_dictionary)


if __name__ == '__main__':
	app.debug = True
	app.secret_key ='Superman_is_awesome'
	app.run(host = '0.0.0.0', port = 8000)