import config
from flask_restx import Api, fields
from werkzeug.middleware.proxy_fix import ProxyFix

config.app.wsgi_app = ProxyFix(config.app.wsgi_app)
# Read the swagger.yml file to configure the endpoints
api = Api(app = config.app, 
            version = "1.0", 
		    title = "Scheduler Web API", 
		    description = "This site is a prototype API for Scheduling")

cartons = api.model('cartons', {
    'Carton_Orders_Index': fields.String(required=True, description='index of carton'),
    'Carton_ID': fields.String(required=True, description='id of carton'),
    'Carton_size': fields.String(required=True, description='size of carton'),
    'SKU_Quantity': fields.String(required=True, description='number of sku ')
})

orders = api.model('orders', {
    'Orders_Index': fields.String(required=True, description='index of order'),
    'Order_ID': fields.String(required=True, description='order id'),
    'Order_date': fields.String(required=True, description='order date'),
    'Order_due_date': fields.String(required=True, description='order due date'),
    'Order_production_date': fields.String(required=True, description='production date'),
    'Carton_Quantity': fields.String(required=True, description='numbers of cartons'),
    'Carton_Orders' : fields.List(fields.Nested(cartons))
})

schedule = api.model('schedule', {
    'Order_quantity': fields.String(required=True, description='Number of orders'),
    'Orders': fields.List(fields.Nested(orders))
})

carton_order = api.model('carton_order', {
    'Carton_Orders_Index': fields.String(required=True, description='index of carton'),
    'Carton_ID': fields.String(required=True, description='carton id'),
    'Robot_Station': fields.String(required=True, description='robot id'),
    'Setup_Time': fields.String(required=True, description='set up time'),
    'Start_Time': fields.String(required=True, description='start time'),
    'End_Time': fields.String(required=True, description='end time'),
})

carton_order_list = api.model('carton_order_list', {
    'Carton_Order_Quantity': fields.String(required=True, description='Number of cartons'),
    'Carton_Orders': fields.List(fields.Nested(carton_order))
})
