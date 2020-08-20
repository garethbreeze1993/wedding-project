To run the application first of all git clone the repository

Then create a virtual environment and run pip install - r requirements.txt to get all dependencies for the project

Next run the migrations for the database. By python manage.py migrate
Running this adds the items from the products.json file into the database as well.

Create a super user with the python manage.py createsuperuser command

Unittests are run with the python manage.py test command

Then run python manage.py runserver to run the project. Go on the admin screen localhost:8000/admin and log in with the superuser details.
Then go back to localhost:8000 to view the project

On the homepage is the list of items you can click on the items to get a more detailed view of the product
or click the add to cart button. This adds the item to the cart.

On the checkout screen is all the products in the cart the user can either remove the product or purchase whatever is in the cart.

On the purchased screen is a breakdown of each order the user has made with each item in there and the quantity of each.
A date for the order is also on the screen.

The generate report screen has a list of items in the checkout screen and also how many items have been ordered and the quantity of each.

Improvements I would have made:
Add a CI script which everytime a commit was made check all the unittests pass and all code is PEP 8 compliant. Before been accepted.

Make changes to the frontend to be more aesthetically pleasing.

Add API endpoints so a user can interact with the application without a web browser and possible interaction with a mobile app frontend

Authentication would create a login screen so user can sign up and login without needing to create a superuser.

Finally would look at upgrading the database from the basic sqllite database to either postgresql/mysql.

