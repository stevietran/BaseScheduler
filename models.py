from config import db

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
    
    def __init__(self, id, size, skuQty, orderId):
        self.Carton_ID = id
        self.Carton_size = size
        self.SKU_Quantity = skuQty
        self.Order_ID = orderId