import collections
from config import db
from models import CartonOrder, Order, CartonLineOrder
from datetime import datetime, timedelta
import json
from types import SimpleNamespace
from api_models import api, schedule, carton_order_list

def convert_DateTime(datetime_str):
    f = '%m-%d-%Y %H:%M:%S'
    return datetime.strptime(datetime_str, f)

def date_to_string(dateTimeObj):
    f = '%m-%d-%Y %H:%M:%S'
    return dateTimeObj.strftime(f)

def write_data(data):
    in_dict = json.loads(json.dumps(data), object_hook=lambda d: SimpleNamespace(**d))
    Orders = in_dict.Orders

    # DELETE all old data in Order, SKU and Carton table
    try:
        db.session.query(Order).delete()
        db.session.query(CartonOrder).delete()
        db.session.commit()
    except:
        db.session.rollback()

    for order in Orders:
        # create new order
        ord = Order(order.Order_ID, convert_DateTime(order.Order_date), convert_DateTime(order.Order_due_date), convert_DateTime(order.Order_production_date), order.Carton_Quantity)
        db.session.add(ord)
        
        Cartons = order.Carton_Orders
        for carton in Cartons:
            # create carton
            car = CartonOrder(carton.Carton_ID, carton.Carton_size, carton.SKU_Quantity, order.Order_ID)
            db.session.add(car)
            db.session.flush()
            db.session.commit()
    
    # DELETE all old data in CartonLineOrder table
    try:
        db.session.query(CartonLineOrder).delete()
        db.session.commit()
    except:
        db.session.rollback()  

def read_data():
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
    
    return carton_dict 

def run():
    # set production date to next date, starting at 8 am
    # prod_datetime = datetime.combine(date.today(), datetime.min.time()) + timedelta(days=1, hours=8)
    # print(prod_datetime)
    
    prod_datetime = datetime.today()

    # Retreive all order sorted by order due date
    orders = db.session.query(CartonOrder, Order).join(Order, CartonOrder.Order_ID == Order.Order_ID).order_by(Order.Order_due_date.asc()).all()
    
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
            current_cobot = 1     
    return