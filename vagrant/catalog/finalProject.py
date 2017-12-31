from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# JSON APIs to view Category Information
@app.route('/category/<int:category_id>/items/JSON')
def categoryItemsJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(
        cat_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])

@app.route('/category/<int:category_id>/items/<int:item_id>/JSON')
def catalogItemJSON(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)

@app.route('/category/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])

# Show all categories. Different templates are used depending on route 
# values and existance of user information.
@app.route('/', methods=['GET']) # Show Categories and Items
@app.route('/category/', methods=['GET']) # Show Categories and Items
@app.route('/category/<int:category_id>', methods=['GET']) # Show Categories and Items
@app.route('/category/<int:category_id>/items', methods=['GET']) # Show Categories and Items
@app.route('/category/<int:category_id>/<int:item_id>', methods=['GET']) # Show Item Description
@app.route('/category/<int:category_id>/items/<int:item_id>', methods=['GET']) # Show Item Description
@app.route('/category/<int:category_id>/items/<string:action>', methods=['GET']) # Show Create Form
@app.route('/category/<int:category_id>/items/<int:item_id>/<string:action>', methods=['GET']) # Show Edit Form
def showCategories(category_id=0, item_id=0, action=None):
    user = None
    category = None
    item = None
    category = None

    if category_id > 0:
        category = session.query(Category).filter_by(id=category_id).one()
        items = session.query(Item).filter_by(
            cat_id=category_id).order_by(asc(Item.id)).all()
    else:
        items = session.query(Item).order_by(asc(Item.id)).limit(10).all()

    if item_id > 0 and category_id > 0:
        try:
            item = session.query(Item).filter_by(id=item_id, cat_id=category_id).one()
        except:
            pass
    elif item_id > 0:
        item = session.query(Item).filter_by(id=item_id).one()


    categories = session.query(Category).order_by(asc(Category.id))

    if 'username' not in login_session:
        return render_template('publiccategories.html', 
            categories=categories,
            category=category,
            items=items, 
            user=user, 
            item=item, 
            category_id=category_id,
            item_id=item_id,
            action=None)
    else:
        user = login_session['username']
        return render_template('categories.html', 
            categories=categories,
            category=category,
            items=items, 
            user=user, 
            item=item, 
            category_id=category_id,
            item_id=item_id,
            action=action)

# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    user = None
    if 'user_id' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        new_category = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        user = login_session['username']
        return render_template('newCategory.html', user=user)

# Edit a category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    user = None
    editedCategory = session.query(
        Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')

    if editedCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this category. Please create your own category in order to edit.');}</script><body onload='myFunction()'>"

    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedCategory.name)
            return redirect(url_for('showCategories'))
    else:
        user = login_session['username']
        return render_template('editCategory.html', category=editedCategory, user=user)

# Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this category. Please create your own category in order to delete.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCategories', category_id=category_id))
    else:
        return render_template('deleteCategory.html', category=categoryToDelete)

# Create a new catalog item
@app.route('/category/<int:category_id>/items/<string:action>', methods=['POST'])
def newItem(category_id=0, action=None):
    user = None
    if 'username' not in login_session:
        return redirect('/login')

    if 'user_id' not in login_session:
        return "<script>function myFunction() {alert('You must be logged in to add items.');}</script><body onload='myFunction()'>"

    user = login_session['username']

    newItem = Item(title=request.form['title'],
                    description=request.form['description'], 
                    cat_id=request.form['cat_id'])
    newItem.user_id = getUserID(login_session['email'])

    session.add(newItem)
    session.commit()

    flash('%s Item Successfully Created' % (newItem.title))
    return redirect(url_for('showCategories'))

# Create a new catalog item
@app.route('/category/<int:category_id>/items/<int:item_id>/edit', methods=['POST'])
def editItem(category_id=0, item_id=0):
    item = session.query(Item).filter_by(id=item_id ).one()
    try:
        user = None
        if 'username' not in login_session:
            return redirect('/login')


        if login_session['user_id'] != item.user_id:
            return "<script>function myFunction() {alert('You are only authorized to update items you created.');}</script><body onload='myFunction()'>"

        user = login_session['username']

        item.title = request.form['title']
        item.description = request.form['description']
        item.cat_id = request.form['cat_id']

        session.commit()
        flash('%s Item Successfully Updated' % (item.title))
        return redirect(url_for('showCategories', category_id=category_id, item_id=item_id))
    except:
        flash('%s Item Update Failed' % (item.title))
        return redirect(url_for('showCategories'))

# Delete a catalog item
@app.route('/category/<int:category_id>/items/<int:item_id>/delete', methods=['POST'])
def deleteItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')

    category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(Item).filter_by(id=item_id).one()

    if login_session['user_id'] != itemToDelete.user_id:
        return "<script>function myFunction() {alert('You can only delete items that you created.');}</script><body onload='myFunction()'>"

    session.delete(itemToDelete)
    session.commit()
    flash('Item Successfully Deleted')
    return redirect(url_for('showCategories', category_id=category_id))

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        if 'username' in login_session:
            del login_session['username']

        if 'email' in login_session:
            del login_session['email']

        if 'picture' in login_session:
            del login_session['picture']

        if 'user_id' in login_session:
            del login_session['user_id']

        if 'provider' in login_session:
            del login_session['provider']

        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
