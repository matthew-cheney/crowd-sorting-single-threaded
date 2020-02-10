from crowdsorting import db
from crowdsorting.app_resources import DBHandler

dbHandler = DBHandler.DBHandler()

dbHandler.create_user("Luke", "Skywalker", "powerconverters@gmail.com", "l20")
dbHandler.create_user("Leia", "Skywalker", "incommand@gmail.com", "l21")
dbHandler.create_user("Han", "Solo", "nevertellmetheodds@byu.edu", "h20")
dbHandler.create_user("Chewbacce", "TheWookie", "walkingcarpet@byu.edu", "c20")
dbHandler.create_user("Obi-wan", "Kenobi", "dontrememberanydroids@gmail.com", "o20")
