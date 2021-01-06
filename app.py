import flask
from flask_sqlalchemy import SQLAlchemy
import collections
import json
from types import SimpleNamespace
from datetime import datetime
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# global variables
app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, './dbTest.db')
app.config['SECRET_KEY'] = "random string"
session_options = {'autocommit': False, 'autoflush': False}
db = SQLAlchemy(app, session_options=session_options)

def convert_DateTime(datetime_str):
    f = '%m-%d-%Y %H:%M:%S'
    return datetime.strptime(datetime_str, f)

def date_to_string(dateTimeObj):
    f = '%m-%d-%Y %H:%M:%S'
    return dateTimeObj.strftime(f)

def runScheduler():
    # TODO: schedule by due_date
    # Hardcode output
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
		}]}
    
    out_dict = json.loads(json.dumps(out_json), object_hook=lambda d: SimpleNamespace(**d))
    carton_orders = out_dict.Carton_Orders
    #print(carton_orders)
    
    # Write to 'carton_line_order' table
    for order_dict in carton_orders:
        order = CartonLineOrder(order_dict.Carton_ID, order_dict.Robot_Station, convert_DateTime(order_dict.Setup_Time), convert_DateTime(order_dict.Start_Time), convert_DateTime(order_dict.End_Time))
        #print(order.Start_Time)
        db.session.add(order)
        db.session.flush()
        db.session.commit()
        #print("Carton Order added!")

    """
    rows = CartonLineOrder.query.all()
    for row in rows:
        print(row.Setup_Time)
    """    
    return

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

class Order(db.Model):
    __tablename__='order'
    Orders_Index = db.Column(db.Integer, primary_key=True)
    Order_ID = db.Column(db.String(50))
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

@app.route('/', methods=['GET'])
def home():
    return "<h1>HPL Scheduler</h1><p>This site is a prototype API for HPL Scheduling.</p>"

@app.route('/schedule', methods=['GET'])
def runSchedule():   
    # Write sent request body
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

    in_dict = json.loads(json.dumps(in_json), object_hook=lambda d: SimpleNamespace(**d))
    Orders = in_dict.Orders
    for order in Orders:
        # create new order
        ord = Order(order.Order_ID, convert_DateTime(order.Order_date), convert_DateTime(order.Order_due_date), convert_DateTime(order.Order_production_date), order.Carton_Quantity)
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
  
    # DELETE all old data
    try:
        num_rows_deleted = db.session.query(CartonLineOrder).delete()
        db.session.commit()
    except:
        db.session.rollback()
    
    # Run Scheduler
    runScheduler()
    
    # Prepare output
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

    return json.dumps(orders_list)

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    app.run(debug = True)