from typing import List

class CartonLineOrder:
	Carton_Orders_Index : int
    Carton_ID: str
    Robot_Station: int
    Setup_Time: str
    Start_Time: str    
    End_Time: str
	def __init__(self):
		

class CartonSchedule:
    Carton_Order_quantity : int
    Carton_Orders : List # (CartonLineOrder)

class Sku:
    def __init__(self, SKU_INDEX, SKU_ID, SKU_Pouch_ID):
        SKU_INDEX : int
        SKU_ID : str
        SKU_Pouch_ID : int

class CartonOrderDetail:
    Carton_Orders_Index : int
    Carton_ID : str
    Carton_size : str
    SKU_Quantity : int
    SKU_ID : List #(Sku)

class CartonOrder:
    Orders_Index : int
    Order_ID : str
    Order_date : str
    Order_due_date : str
    Order_production_date : str
    Carton_Quantity: int
    Carton_Orders: List #(CartonOrderDetail)

class CartonOrderList:
    Order_quantity : int
    Orders : List #(CartonOrder)

import json
from types import SimpleNamespace

out_json = {
	"Carton_Order_quantity": "2",
	"Carton_Orders":

	[
		{
			"Carton_Orders_Index":"1",
			"Carton_ID": "SO_10008_200611_002",
			"Robot_Station": "1",
			"Setup_Time": "04-01-2020  9:09:00 AM",
			"Start_Time": "04-01-2020  9:09:00 AM",
			"End_Time": "04-01-2020  9:14:00 AM"
		},
		
		{
			"Carton_Orders_Index":"2",
			"Carton_ID": "SO_10008_200611_001",
			"Robot_Station": "2",
			"Setup_Time": "04-01-2020  1:27:00 PM",
			"Start_Time": "04-01-2020  1:27:00 PM",
			"End_Time": "04-01-2020  1:32:00 PM"
		}
		
	]
}

in_json = {
	"Order_quantity": "1",
	"Orders":
	
	[
		{
			"Orders_Index":"1",
			"Order_ID": "SO_10001",
			"Order_date": "200608",
			"Order_due_date": "200611",
			"Order_production_date": "200611",

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
	]
}

out_dict = json.loads(json.dumps(out_json), object_hook=lambda d: SimpleNamespace(**d))
print(out_dict.Carton_Orders[0])
lineOrder = CartonLineOrder()
#out_obj = CartonSchedule(**out_dict)

""" 
in_dict = json.loads(json.dumps(in_json), object_hook=lambda d: SimpleNamespace(**d))
a = Sku(list(in_dict.Orders[0].Carton_Orders[0].SKU_ID[0]))
print(a) """