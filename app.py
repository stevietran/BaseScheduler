from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import collections
import json
from types import SimpleNamespace
from datetime import date, datetime, timedelta
import os
basedir = os.path.abspath(os.path.dirname(__file__))
import sqlite3
from sqlalchemy import text
import string
import random

unique = set()

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    global unique
    while True:
        value = ''.join(random.choice(chars) for _ in range(size))
        if value not in unique:
            unique.add(value)
            break
    return value

# global variables
app = Flask(__name__)
app.config["DEBUG"] = True
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, './dbTest.db')
app.config['SECRET_KEY'] = "random string"
session_options = {'autocommit': False, 'autoflush': False}
db = SQLAlchemy(app, session_options=session_options)
#db = SQLAlchemy(app)

# set dev = True to use preset data
#dev = False
dev = True

class CartonLineOrder(db.Model):
    __tablename__ = 'carton_line_order'
    Carton_Orders_Index = db.Column(db.Integer, primary_key = True)
    Carton_ID = db.Column(db.String(100))
    Robot_Station = db.Column(db.Integer)
    Setup_Time = db.Column(db.DateTime)  
    Start_Time = db.Column(db.DateTime)      
    End_Time = db.Column(db.DateTime)

    def __init__(self, id, station, setup, start, end):
        self.Carton_ID = id
        self.Robot_Station = station
        self.Setup_Time = setup
        self.Start_Time = start
        self.End_Time = end

class RecipeLineOrder(db.Model):
    __tablename__ = 'recipe_line_order'
    Recipes_Index = db.Column(db.Integer, primary_key = True, nullable=False, unique=True, autoincrement=True)
    Product_Type = db.Column(db.String(50))
    Setup_Time = db.Column(db.DateTime)  
    Start_Time = db.Column(db.DateTime)      
    End_Time = db.Column(db.DateTime)
    LHP1_ID = db.Column(db.String(50))
    LHP1_Ingredient = db.Column(db.String(50))
    LHP1_Quantity = db.Column(db.Float)   
    LHP2_ID = db.Column(db.String(50))
    LHP2_Ingredient = db.Column(db.String(50))
    LHP2_Quantity = db.Column(db.Float)   
    LHP3_ID = db.Column(db.String(50))
    LHP3_Ingredient = db.Column(db.String(50))
    LHP3_Quantity = db.Column(db.Float)   
    SHP1_ID = db.Column(db.String(50))
    SHP1_Ingredient = db.Column(db.String(50))
    SHP1_Quantity = db.Column(db.Float)   
    SHP2_ID = db.Column(db.String(50))
    SHP2_Ingredient = db.Column(db.String(50))
    SHP2_Quantity = db.Column(db.Float)
    SHP3_ID = db.Column(db.String(50))
    SHP3_Ingredient = db.Column(db.String(50))
    SHP3_Quantity = db.Column(db.Float)
    Pouch_Line_Order = db.relationship("PouchLineOrder", backref="recipe_line_order", lazy=True)  

class PouchLineOrder(db.Model):
    __tablename__ = 'pouch_line_order'
    Pouches_Index = db.Column(db.Integer, primary_key = True, nullable=False, unique=True, autoincrement=True)
    Pouch_ID = db.Column(db.String(50))
    Recipes_Index = db.Column(db.Integer, db.ForeignKey("recipe_line_order.Recipes_Index"), nullable = False)
    Product_Type = db.Column(db.String(50))
    Setup_Time = db.Column(db.DateTime)  
    Start_Time = db.Column(db.DateTime)      
    End_Time = db.Column(db.DateTime)

class Order(db.Model):
    __tablename__='order'
    Orders_Index = db.Column(db.Integer, primary_key=True)
    Order_ID = db.Column(db.String(50), unique=True)
    Order_date = db.Column(db.DateTime)
    Order_due_date = db.Column(db.DateTime)
    Order_production_date = db.Column(db.DateTime)
    Carton_Quantity = db.Column(db.Integer)
    Carton_Orders = db.relationship('CartonOrder', backref='order', lazy=True)

    def __init__(self, id, date, dueDate, prodDate, cartonQty):
        self.Order_ID = id
        self.Order_date = date
        self.Order_due_date = dueDate
        self.Order_production_date = prodDate
        self.Carton_Quantity = cartonQty

class CartonOrder(db.Model):
    __tablename__='carton'
    Carton_Orders_Index = db.Column(db.Integer, primary_key=True)
    Carton_ID = db.Column(db.String(50))
    Carton_size = db.Column(db.String(10))
    SKU_Quantity = db.Column(db.Integer)
    Order_ID = db.Column(db.String(50), db.ForeignKey('order.Order_ID'), nullable = False)

    SKU_List = db.relationship('Sku', backref='carton', lazy=True)
    
    def __init__(self, id, size, skuQty, orderId):
        self.Carton_ID = id
        self.Carton_size = size
        self.SKU_Quantity = skuQty
        self.Order_ID = orderId

class Sku(db.Model):
    __tablename__='sku'
    SKU_INDEX = db.Column(db.Integer, primary_key=True)
    SKU_ID = db.Column(db.String(50))
    SKU_Pouch_ID = db.Column(db.String(50))
    Carton_ID = db.Column(db.String(50), db.ForeignKey('carton.Carton_ID'), nullable = False)
    def __init__(self, ID, Pouch, carton):
        #self.SKU_INDEX = index
        self.SKU_ID = ID
        self.SKU_Pouch_ID = Pouch
        self.Carton_ID = carton

class Bom(db.Model):
    __tablename__='bom'
    BOMId = db.Column(db.Integer, primary_key=True)
    RecipeNo = db.Column(db.String(50))
    IngredientName = db.Column(db.String(50))
    Qty = db.Column(db.Float)
    IngredientType = db.Column(db.String(50))

class ProductList(db.Model):
    __tablename__='product_list'
    ProductId = db.Column(db.Integer, primary_key=True)
    RecipeNo = db.Column(db.String(50))
    ProductName = db.Column(db.String(50))
    ProductType = db.Column(db.String(50))
    ProductSize = db.Column(db.String(50))
    ProductCategory = db.Column(db.String(50))

class Hopper(db.Model):
    __tablename__='hopper'
    HopperId = db.Column(db.String(50), primary_key=True, nullable=False)
    Availability = db.Column(db.String(50), default="False", nullable=False)
    HopperType = db.Column(db.String(50))
    ProductType = db.Column(db.String(50))
    Used = db.Column(db.String(50), default="False")

def findHopperId(iType, hType, pType):
    if not iType:
        return None
    
    id = getHopperId(hType, pType)
    if not id:
        resetHopper(hType, pType)
        id = getHopperId(hType, pType)
    
    # update hopper status
    id = id[0]
    print("Hopper id {} utilised!".format(id))

    Hopper.query\
        .filter_by(HopperId=id)\
        .update(dict(Used = "True"))

    db.session.commit()
    
    return id
     
def getHopperId(hType, pType):
    id = db.session\
        .query(Hopper.HopperId)\
        .filter(Hopper.Availability == "True")\
        .filter(Hopper.HopperType == hType)\
        .filter(Hopper.Used == "False")\
        .filter(Hopper.ProductType == pType).first()

    return id

def resetHopper(hType, pType):
    # reset availablity
    Hopper.query\
        .filter_by(HopperType = hType)\
        .filter_by(ProductType = pType)\
        .update(dict(Used = "False"))
    
    db.session.commit()
    print("Hopper status reset!")

def post_row(conn, tablename, rec):
    keys = ','.join(rec.keys())
    # print(keys)
    question_marks = ','.join(list('?'*len(rec)))
    values = tuple(rec.values())
    # print(values)
    conn.execute('INSERT INTO '+tablename+' ('+keys+') VALUES ('+question_marks+')', values)

def convert_DateTime(datetime_str):
    f = '%m-%d-%Y %H:%M:%S'
    return datetime.strptime(datetime_str, f)

def convert_Date(date_str):
    f = '%y%m%d'
    return datetime.strptime(date_str, f)

def date_to_string(dateTimeObj):
    f = '%m-%d-%Y %H:%M:%S'
    return dateTimeObj.strftime(f)

def runCartonOptimiser():
    # set production date to next date, starting at 8 am
    prod_datetime = datetime.combine(date.today(), datetime.min.time()) + timedelta(days=1, hours=8)
    print(prod_datetime)
    
    # Retreive all order sorted by order due date
    orders = db.session\
        .query(CartonOrder, Order)\
        .join(Order, CartonOrder.Order_ID == Order.Order_ID)\
        .order_by(Order.Order_due_date.asc()).all()
    
    #for order in orders:
    #    print(order[1].Order_due_date)
    
    # Alternatively assign job to each robot
    # Write to 'carton_line_order' table
    current_cobot = 1
    cobot1_time = prod_datetime
    cobot2_time = prod_datetime
    setup_time = 60
    op_time = 180
    
    for order_dict in orders:
        if current_cobot == 1:
            Setup_Time = cobot1_time
            Start_Time = cobot1_time + timedelta(seconds=setup_time)
            End_Time = Start_Time + timedelta(seconds=op_time)
            cobot1_time = End_Time
            order = CartonLineOrder(
                order_dict[0].Carton_ID, 
                current_cobot, 
                Setup_Time, 
                Start_Time, 
                End_Time
            )
        else:
            Setup_Time = cobot2_time
            Start_Time = cobot2_time + timedelta(seconds=setup_time)
            End_Time = Start_Time + timedelta(seconds=op_time)
            cobot2_time = End_Time
            order = CartonLineOrder(
                order_dict[0].Carton_ID, 
                current_cobot, 
                Setup_Time, 
                Start_Time, 
                End_Time
            )         
        #print(order.Start_Time)
        # add to database
        db.session.add(order)
        db.session.flush()
        db.session.commit()
        #print("Carton Order added!")
        if (current_cobot == 1):
            current_cobot = 2
        else:
            current_cobot = 1
    
    return 1

def scheduleRecipe(recipe, line_time):   
    # Recipe: ('Diabetic', 7, 'Powder')
    name = recipe[0]
    powderFlag = recipe[2] == "Powder"
    print("Powder Product?: {}".format(powderFlag))

    # Get ingredient qty
    ingredientList = db.session\
        .query(
            Sku.SKU_Pouch_ID,
            ProductList.ProductType,
            Bom.IngredientName,
            Bom.IngredientType,
            db.func.sum(Bom.Qty).label("TotalQty")
        )\
        .join(CartonOrder, CartonOrder.Carton_ID == Sku.Carton_ID, isouter = True)\
        .join(Order, Order.Order_ID == CartonOrder.Order_ID, isouter = True)\
        .join(ProductList, ProductList.RecipeNo == Sku.SKU_ID, isouter = True)\
        .join(Bom, Bom.RecipeNo == Sku.SKU_ID, isouter = True)\
        .filter(
            ProductList.ProductType == name
        )\
        .group_by(Bom.IngredientName)\
        .order_by(text("TotalQty desc"))

    # Query pouches
    pouchList = db.session\
        .query(
            Sku.SKU_Pouch_ID,
            Order.Order_due_date
        )\
        .join(CartonOrder, CartonOrder.Carton_ID == Sku.Carton_ID, isouter = True)\
        .join(Order, Order.Order_ID == CartonOrder.Order_ID, isouter = True)\
        .join(ProductList, ProductList.RecipeNo == Sku.SKU_ID, isouter = True)\
        .filter(
            ProductList.ProductType == name
        )\
        .order_by(Order.Order_due_date)
    number_pouches = pouchList.count()
    
    print("Number of pouches: {}".format(number_pouches))
    
    # define time variables
    setup_time = 2 # set-up time of one pouch is 3 second
    op_time = 10 # operation time of one pouch is 10 seconds
    buffer_time = 6 # buffer time of one pouch is 5 seconds
    recipe_setup = 240 # recipe set-up time
    recipe_op_time = (setup_time + op_time) + buffer_time * (number_pouches - 1) 

    recipeData = [name] # list of tuple ('ingredient_name', 'qty')
    
    ingredientDict = dict()
    ingredientDict['main'] = []
    ingredientDict['additive'] = []
    
    for item in ingredientList:
        # Schedule recipe to table hear
        ingredientDict[item[3]].append((item[2], item[4]))
    
    mainCount = len(ingredientDict['main'])
    for i in range(mainCount, 3):
        ingredientDict['main'].append((None, None))
    
    additiveCount = len(ingredientDict['additive'])
    
    for i in range(additiveCount, 3):
        ingredientDict['additive'].append((None, None))
    
    for item in ingredientDict['main']:
        recipeData.append(item)
    
    for item in ingredientDict['additive']:
        recipeData.append(item)

    print("recipe data: {}".format(recipeData))
    
    # update table
    conn = sqlite3.connect('dbTest.db', isolation_level=None)
    recipe=dict()
    recipe["Product_Type"] = recipeData[0]
    
    recipe["Setup_Time"] = line_time
    recipe["Start_Time"] = line_time + timedelta(seconds=recipe_setup)
    recipe["End_Time"] = line_time + timedelta(seconds=recipe_setup+recipe_op_time)
    
    recipe["LHP1_Ingredient"] = recipeData[1][0]
    recipe["LHP1_Quantity"] = recipeData[1][1]    
    recipe["LHP2_Ingredient"] = recipeData[2][0]
    recipe["LHP2_Quantity"] = recipeData[2][1]
    recipe["LHP3_Ingredient"] = recipeData[3][0]
    recipe["LHP3_Quantity"] = recipeData[3][1]
    
    recipe["SHP1_Ingredient"] = recipeData[4][0]
    recipe["SHP1_Quantity"] = recipeData[4][1]
    recipe["SHP2_Ingredient"] = recipeData[5][0]
    recipe["SHP2_Quantity"] = recipeData[5][1]
    recipe["SHP3_Ingredient"] = recipeData[6][0]
    recipe["SHP3_Quantity"] = recipeData[6][1]

    # if powderFlag: 
    if powderFlag:
        recipe["LHP1_ID"] = findHopperId(recipeData[1][0], "Large", "Powder")
        recipe["LHP2_ID"] = findHopperId(recipeData[2][0], "Large", "Powder")
        recipe["LHP3_ID"] = findHopperId(recipeData[3][0], "Large", "Powder")
        recipe["SHP1_ID"] = findHopperId(recipeData[4][0], "Small", "Powder")
        recipe["SHP2_ID"] = findHopperId(recipeData[5][0], "Small", "Powder")
        recipe["SHP3_ID"] = findHopperId(recipeData[5][0], "Small", "Powder")
    
    post_row(conn, 'recipe_line_order', recipe)   
    
    # get recipe index
    recipe_idx = db.session\
        .query(RecipeLineOrder.Recipes_Index)\
        .filter(RecipeLineOrder.Product_Type == name)
    
    pouch = dict()
    currentMachineTime = line_time + timedelta(seconds=recipe_setup)  
    for item in pouchList:
        pouch["Pouch_ID"] = item[0]
        pouch["Setup_Time"] = currentMachineTime
        pouch["Start_Time"] = currentMachineTime + timedelta(seconds=setup_time)
        pouch["End_Time"] = currentMachineTime + timedelta(seconds=setup_time+op_time)
        currentMachineTime += timedelta(seconds=buffer_time)
        pouch["Recipes_Index"] = recipe_idx[0][0]
        pouch["Product_Type"] = name
        post_row(conn, 'pouch_line_order', pouch) 
        #print(pouch)

def runRecipeOptimiser():
    # combine recipe as powder/liquid
    
    recipeList = db.session.query(
            ProductList.ProductType, db.func.count(Sku.SKU_Pouch_ID).label('Total'), ProductList.ProductCategory
        )\
        .join(ProductList, ProductList.RecipeNo == Sku.SKU_ID, isouter = True)\
        .filter(
            ProductList.ProductCategory == "Liquid" or 
            ProductList.ProductCategory == "Powder"
        )\
        .group_by(ProductList.ProductType)\
        .order_by(text("total desc"))    
    
    prod_datetime = datetime.today()
    for row in recipeList.all():
        print("Recipe: {0}".format(row))
        scheduleRecipe(row, prod_datetime)

def runScheduler():
    # TODO: schedule by due_date
    # Hardcode carton output
    out_json = { "Carton_Order_quantity": "2",
	"Carton_Orders":[
		{
			"Carton_Orders_Index":"1",
			"Carton_ID": "SO_10008_200611_001",
			"Robot_Station": "2",
			"Setup_Time": "04-01-2020 1:27:00",
			"Start_Time": "04-01-2020 1:27:00",
			"End_Time": "04-01-2020 1:32:00"
		},
        {
			"Carton_Orders_Index":"2",
			"Carton_ID": "SO_10008_200611_002",
			"Robot_Station": "1",
			"Setup_Time": "04-01-2020 1:32:00",
			"Start_Time": "04-01-2020 1:32:00",
			"End_Time": "04-01-2020 1:35:00"
		}
        ]
    }
    
    out_dict = json.loads(json.dumps(out_json), object_hook=lambda d: SimpleNamespace(**d))
    
    carton_orders = out_dict.Carton_Orders
    #print(carton_orders)
    
    # Query all carton order
    #CartonOrder.query.
    
    runCartonOptimiser()
    
    """
    # Write to 'carton_line_order' table
    for order_dict in carton_orders:
        order = CartonLineOrder(order_dict.Carton_ID, order_dict.Robot_Station, convert_DateTime(order_dict.Setup_Time), convert_DateTime(order_dict.Start_Time), convert_DateTime(order_dict.End_Time))
        #print(order.Start_Time)
        db.session.add(order)
        db.session.flush()
        db.session.commit()
        #print("Carton Order added!")


    rows = CartonLineOrder.query.all()
    for row in rows:
        print(row.Setup_Time)
    """ 

    # Hard code pouch list

    # Hard code recipe list
       
    return

def runSchedulerBTM():
    # TODO: 1 cobot is broken down, schedule for robot 2 only
    
    # set production date to next date, starting at 8 am
    # prod_datetime = datetime.combine(date.today(), datetime.min.time()) + timedelta(days=1, hours=8)
    # print(prod_datetime)
    
    prod_datetime = datetime.today()

    # Retreive all order sorted by order due date
    orders = db.session.query(CartonOrder, Order).join(Order, CartonOrder.Order_ID == Order.Order_ID).order_by(Order.Order_due_date.asc()).all()
    
    # Alternatively assign job to each robot
    # Write to 'carton_line_order' table
    current_cobot = 2
    cobot1_time = prod_datetime
    cobot2_time = prod_datetime
    setup_time = 60
    op_time = 180
    
    for order_dict in orders:
        if current_cobot == 1:
            Setup_Time = cobot1_time
            Start_Time = cobot1_time + timedelta(seconds=setup_time)
            End_Time = Start_Time + timedelta(seconds=op_time)
            cobot1_time = End_Time
            order = CartonLineOrder(order_dict[0].Carton_ID, current_cobot, Setup_Time, Start_Time, End_Time)
        else:
            Setup_Time = cobot2_time
            Start_Time = cobot2_time + timedelta(seconds=setup_time)
            End_Time = Start_Time + timedelta(seconds=op_time)
            cobot2_time = End_Time
            order = CartonLineOrder(order_dict[0].Carton_ID, current_cobot, Setup_Time, Start_Time, End_Time)         
        #print(order.Start_Time)
        # add to database
        db.session.add(order)
        db.session.flush()
        db.session.commit()
        #print("Carton Order added!")
        if (current_cobot == 1):
            current_cobot = 2
        else:
            current_cobot = 2     
    return

def updateMasterData():
    conn = sqlite3.connect('dbTest.db', isolation_level=None)
    
    data = json.load(open('response.json',))
    bomData = data["BOMs"]
    for row in bomData:
        post_row(conn, 'bom', row)

    productData = data["ProductList"] 
    for row in productData:
        post_row(conn, 'product_list', row)
    
    # Hopper
    data = json.load(open('hopper.json',))
    hopperData = data["Hopper"]
    for row in hopperData:
        post_row(conn, 'hopper', row)

    conn.close()

    # if dev, load a preset data
    if dev:
        in_json = json.load(open('input.json'))
        in_dict = json.loads(json.dumps(in_json), object_hook=lambda d: SimpleNamespace(**d))
        Orders = in_dict.Orders
        
        # DELETE all old data in Order, SKU and Carton table
        try:
            db.session.query(Order).delete()
            db.session.query(CartonOrder).delete()
            db.session.query(Sku).delete()
            db.session.commit()
        except:
            db.session.rollback()

        for order in Orders:
            # create new order
            ord = Order(order.Order_ID, convert_Date(order.Order_date), convert_Date(order.Order_due_date), convert_Date(order.Order_production_date), order.Carton_Quantity)
            db.session.add(ord)
            #db.session.flush()
            #db.session.commit()
            Cartons = order.Carton_Orders
            for carton in Cartons:
                # create carton
                car = CartonOrder(carton.Carton_ID, carton.Carton_size, carton.SKU_Quantity, order.Order_ID)
                db.session.add(car)
                #db.session.flush()
                #db.session.commit()
                Skus = carton.SKU_ID
                for sku in Skus:
                    # create sku
                    sk = Sku(sku.SKU_ID, sku.SKU_Pouch_ID, car.Carton_ID)
                    db.session.add(sk)
                db.session.flush()
                db.session.commit()

@app.route('/', methods=['GET'])
def home():
    return "<h1>HPL Scheduler</h1><p>This site is a prototype API for HPL Scheduling.</p>"

@app.route('/schedule', methods=['GET'])
def runSchedule():   
    req_data = request.get_json()
    # print(req_data)
    
    # Write sent request body to a table
    in_json = {
	"Order_quantity": "1",
	"Orders":
	[
		{
			"Orders_Index":"1",
			"Order_ID": "SO_10001",
			"Order_date": "04-01-2020 00:00:00",
			"Order_due_date": "05-01-2020 00:00:00",
			"Order_production_date": "04-01-2020 00:00:00",

			"Carton_Quantity": "1",
	
			"Carton_Orders":
			[
				{
					"Carton_Orders_Index": "1",
					"Carton_ID": "SO_10001_200611_001",
					"Carton_size": "S",

					"SKU_Quantity": "3",
					"SKU_ID":
					[
						{
							"SKU_INDEX": "1",
							"SKU_ID": "90000002",
							"SKU_Pouch_ID": "0" 
						},
				
						{
							"SKU_INDEX": "2",
							"SKU_ID": "90000002", 
							"SKU_Pouch_ID": "0"
						}, 

						{
							"SKU_INDEX": "3", 
							"SKU_ID": "20PE03befL001AA", 
							"SKU_Pouch_ID": "SO_10001_200611_001_01"
						}
					]
				}
			]
		}
	]}
    in_dict = json.loads(json.dumps(req_data), object_hook=lambda d: SimpleNamespace(**d))
    Orders = in_dict.Orders
    
    # DELETE all old data in Order, SKU and Carton table
    try:
        db.session.query(Order).delete()
        db.session.query(CartonOrder).delete()
        db.session.query(Sku).delete()
        db.session.commit()
    except:
        db.session.rollback()

    for order in Orders:
        # create new order
        ord = Order(order.Order_ID, convert_Date(order.Order_date), convert_Date(order.Order_due_date), convert_Date(order.Order_production_date), order.Carton_Quantity)
        db.session.add(ord)
        #db.session.flush()
        #db.session.commit()
        Cartons = order.Carton_Orders
        for carton in Cartons:
            # create carton
            car = CartonOrder(carton.Carton_ID, carton.Carton_size, carton.SKU_Quantity, order.Order_ID)
            db.session.add(car)
            #db.session.flush()
            #db.session.commit()
            Skus = carton.SKU_ID
            for sku in Skus:
                # create sku
                sk = Sku(sku.SKU_ID, sku.SKU_Pouch_ID, car.Carton_ID)
                db.session.add(sk)
            db.session.flush()
            db.session.commit()
  
    # DELETE all old data in CartonLineOrder table
    try:
        num_rows_deleted = db.session.query(CartonLineOrder).delete()
        db.session.commit()
    except:
        db.session.rollback()
    
    # Run Scheduler for Carton orders
    runScheduler()
    
    # Prepare output matched with output requirement
    # Carton orders
    rows = CartonLineOrder.query.all()
    orders_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['Carton_Orders_Index'] = row.Carton_Orders_Index
        d['Carton_ID'] = row.Carton_ID
        d['Robot_Station'] = row.Robot_Station
        d['Setup_Time'] = date_to_string(row.Setup_Time)
        d['Start_Time'] = date_to_string(row.Start_Time)
        d['End_Time'] = date_to_string(row.End_Time)
        orders_list.append(d)
    
    carton_dict = collections.OrderedDict()
    carton_dict['Carton_Order_Quantity'] = len(orders_list)
    carton_dict['Carton_Orders'] = orders_list

    # Recipe orders
    recipe_dict = collections.OrderedDict()
    recipe_dict['Recipe_Quantity'] = 'None'
    recipe_dict['Recipes'] = 'None'

    # Pouch orders
    pouch_dict = collections.OrderedDict()
    pouch_dict['Pouch_Quantity'] = 'None'
    pouch_dict['Pouches'] = 'None'   

    # final response
    res_dict = collections.OrderedDict()
    res_dict["Recipe_Set"] = recipe_dict
    res_dict["Pouch_Set"] = pouch_dict
    res_dict["Carton_Set"] = carton_dict
    
    return json.dumps(res_dict)

@app.route('/scheduleBTM', methods=['GET'])
def runScheduleBTM():   
    req_data = request.get_json()
    # print(req_data)
    in_dict = json.loads(json.dumps(req_data), object_hook=lambda d: SimpleNamespace(**d))
    Orders = in_dict.Orders
    
    # DELETE all old data in Order, SKU and Carton table
    try:
        db.session.query(Order).delete()
        db.session.query(CartonOrder).delete()
        db.session.query(Sku).delete()
        db.session.commit()
    except:
        db.session.rollback()

    for order in Orders:
        # create new order
        ord = Order(order.Order_ID, convert_Date(order.Order_date), convert_Date(order.Order_due_date), convert_Date(order.Order_production_date), order.Carton_Quantity)
        db.session.add(ord)
        #db.session.flush()
        #db.session.commit()
        Cartons = order.Carton_Orders
        for carton in Cartons:
            # create carton
            car = CartonOrder(carton.Carton_ID, carton.Carton_size, carton.SKU_Quantity, order.Order_ID)
            db.session.add(car)
            #db.session.flush()
            #db.session.commit()
            Skus = carton.SKU_ID
            for sku in Skus:
                # create sku
                sk = Sku(sku.SKU_ID, sku.SKU_Pouch_ID, car.Carton_ID)
                db.session.add(sk)
            db.session.flush()
            db.session.commit()
  
    # DELETE all old data in CartonLineOrder table
    try:
        db.session.query(CartonLineOrder).delete()
        db.session.query(RecipeLineOrder).delete()
        db.session.query(PouchLineOrder).delete()
        db.session.commit()
    except:
        db.session.rollback()
    
    # Run Scheduler for Carton orders and recipes
    runSchedulerBTM() # only cobot 2
    runRecipeOptimiser()

    # Prepare output matched with output requirement
    # Carton orders
    rows = CartonLineOrder.query.all()
    orders_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['Carton_Orders_Index'] = row.Carton_Orders_Index
        d['Carton_ID'] = row.Carton_ID
        d['Robot_Station'] = row.Robot_Station
        d['Setup_Time'] = date_to_string(row.Setup_Time)
        d['Start_Time'] = date_to_string(row.Start_Time)
        d['End_Time'] = date_to_string(row.End_Time)
        orders_list.append(d)
    
    carton_dict = collections.OrderedDict()
    carton_dict['Carton_Order_Quantity'] = len(orders_list)
    carton_dict['Carton_Orders'] = orders_list

    # Recipe orders changed
    # Recipe orders
    rows = RecipeLineOrder.query.all()
    recipes_list = []
    for row in rows:
        d = collections.OrderedDict()
        d["Recipes_Index"] = row.Recipes_Index
        d["Product_Type"] = row.Product_Type
        d["Setup_Time"] = date_to_string(row.Setup_Time)
        d["Start_Time"] = date_to_string(row.Start_Time)
        d["End_Time"] = date_to_string(row.End_Time)
        d["Large_Hopper_Position_1"] = {
            "LHP1_ID": row.LHP1_ID,
            "LHP1_Ingredient": row.LHP1_Ingredient,
            "LHP1_Quantity": row.LHP1_Quantity
        }
        d["Large_Hopper_Position_2"] = {
            "LHP2_ID": row.LHP2_ID,
            "LHP2_Ingredient": row.LHP2_Ingredient,
            "LHP2_Quantity": row.LHP2_Quantity
        }        
        d["Large_Hopper_Position_3"] = {
            "LHP3_ID": row.LHP3_ID,
            "LHP3_Ingredient": row.LHP3_Ingredient,
            "LHP3_Quantity": row.LHP3_Quantity
        }        
        d["Small_Hopper_Position_1"] = {
            "SHP1_ID": row.SHP1_ID,
            "SHP1_Ingredient": row.SHP1_Ingredient,
            "SHP1_Quantity": row.SHP1_Quantity
        }
        d["Small_Hopper_Position_2"] = {
            "SHP2_ID": row.SHP2_ID,
            "SHP2_Ingredient": row.SHP2_Ingredient,
            "SHP2_Quantity": row.SHP2_Quantity
        }        
        d["Small_Hopper_Position_3"] = {
            "SHP3_ID": row.SHP3_ID,
            "SHP3_Ingredient": row.SHP3_Ingredient,
            "SHP3_Quantity": row.SHP3_Quantity
        }        
        recipes_list.append(d)

    recipe_dict = collections.OrderedDict()
    recipe_dict['Recipe_Quantity'] = len(recipes_list)
    recipe_dict['Recipes'] = recipes_list

    # Pouch orders changed
    # Pouch orders
    rows = PouchLineOrder.query.all()
    pouches_list = []
    for row in rows:
        d = collections.OrderedDict()
        d["Pouches_Index"] = row.Pouches_Index
        d["Pouch_ID"] = row.Pouch_ID
        d["Recipes_Index"] = row.Recipes_Index
        d["Product_Type"] = row.Product_Type
        d["Setup_Time"] = date_to_string(row.Setup_Time)
        d["Start_Time"] = date_to_string(row.Start_Time)
        d["End_Time"] = date_to_string(row.End_Time)
        pouches_list.append(d)
    
    pouch_dict = collections.OrderedDict()
    pouch_dict['Pouch_Quantity'] = len(pouches_list)
    pouch_dict['Pouches'] = pouches_list  

    # final response
    res_dict = collections.OrderedDict()
    res_dict["Recipe_Set"] = recipe_dict
    res_dict["Pouch_Set"] = pouch_dict
    res_dict["Carton_Set"] = carton_dict
    
    return json.dumps(res_dict)

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    updateMasterData()
    app.run(debug = True)