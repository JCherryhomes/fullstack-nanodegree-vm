from flask import Flask, render_template, redirect, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

# DBSession = sessionmaker(bind=engine)
# session = DBSession()
 
#Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}
restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]

#Fake Menu Items
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}

@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurants/JSON')
def showRestaurantJSON():
    return jsonify(restaurants=restaurants)

# Task 1: Create route for newMenuItem function here
@app.route('/restaurant/new', methods = ['GET', 'POST'])
def newRestaurant(restaurant_id):
    if request.method == 'GET':
        return render_template('newRestaurant.html')

    if request.method == 'POST':
        # get new restaurant data from request
        redirect('/restaurants')
    # return 'This page will be for making a new restaurant';

@app.route('/restaurant/<int:restaurant_id>/edit', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):    
    if request.method == 'GET':
    # restaurant = session.query(Restaurant).filter_by(restaurant_id).one()
        return render_template('editRestaurant.html', restaurant=restaurant)
    
    if request.method == 'POST':
        redirect('/restaurants')

@app.route('/restaurant/<int:restaurant_id>/delete', methods = ['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    if request.method == 'GET':
    # return 'This page will be for deleting restaurant %s' % restaurant_id
    # restaurant = session.query(Restaurant).filter_by(restaurant_id).one()
        return render_template('deleteRestaurant.html', restaurant=restaurant)
    if request.method == 'POST':
            redirect('/restaurants')

@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    # return 'This page is the menu for restaurant %s' % restaurant_id
    # restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    # items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items=items)

@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def showMenuJSON(restaurant_id):
    # return 'This page is the menu for restaurant %s' % restaurant_id
    # restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    # items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return jsonify(items=items)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def showMenuItemJSON(restaurant_id, menu_id):
    # return 'This page is the menu for restaurant %s' % restaurant_id
    # restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    # items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return jsonify(item=item)

# Task 2: Create route for editMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/menu/new', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'GET':
        # return 'This page is for making a new menu item for restaurant %s' % restaurant_id
        # restaurant = session.query(Restaurant).filter_by(restaurant_id).one()
        return render_template('newMenuItem.html', restaurant=restaurant)

    if request.method == 'POST':
        redirect('/restaurants/%s/menu' % restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    if request.method == 'GET':
        # return 'This page is for editing menu item %s' % menu_id
        # restaurant = session.query(Restaurant).filter_by(restaurant_id).one()
        # menuItem = session.query(MenuItem).filter_by(restaurant_id, menu_id).one()
        return render_template('editMenuItem.html', restaurant=restaurant, menuItem=item)
    if request.method == 'POST':
        redirect('/restaurants/%s/menu' % restaurant_id)

# Task 3: Create a route for deleteMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if reqeust.method == 'GET':
        # return 'This page is for deleting menu item %s' % menu_id
        # restaurant = session.query(Restaurant).filter_by(restaurant_id).one()
        # menuItem = session.query(MenuItem).filter_by(restaurant_id, menu_id).one()
        return render_template('deleteMenuItem.html', restaurant=restaurant, menuItem=item)

    if request.method == 'POST':
        redirect('/restaurants/%s/menu' % restaurant_id)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
