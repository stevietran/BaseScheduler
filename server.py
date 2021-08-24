from flask import request
import config
from scheduler import run, write_data, read_data
from flask_restx import Resource
from api_models import api, schedule, carton_order_list

flask_app = config.app

db = config.db

name_space = api.namespace('schedule', description='Scheduler APIs')

@name_space.route("/")
class MainClass(Resource):
    @name_space.doc('Get a schedule')
    @name_space.expect(schedule)
    @name_space.marshal_with(carton_order_list, code=201)
    def post(self):
        req_data = request.get_json()
        
        # write request data to the database
        write_data(req_data)
        
        # run the scheduler
        run()
        
        # read output data then return
        res_dict = read_data()
        # print(res_dict)
        return res_dict

if __name__ == "__main__":
    flask_app.run(debug=True)