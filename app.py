from flask import Flask, jsonify, render_template, Response
from threading import Thread
from flask_restful import Resource, Api
from flask_cors import CORS
import xlrd
import requests
import os

app = Flask(__name__)
api = Api(app)
CORS(app)


def run():
  app.run(host='0.0.0.0', port=8888)


class Empty(Resource):

  def __init__(self):
    pass

  def get(self):
    return {"Hello": "World"}


class Info(Resource):

  def __init__(self):
    self.fileName = self.request_salaries()

  def get(self, school, lastName, job, fte):
    # School Name: column 2
    # FTE: column 3
    # Annual Salary and benefits: column 5 + 7
    # Job Title: column 9
    # Name: column 10

    wb = xlrd.open_workbook(self.fileName)
    sheet = wb.sheet_by_index(0)

    matches = []
    for row_idx in range(1, sheet.nrows):
      row = sheet.row_values(row_idx)

      if (school == 'Default' or school.lower() in row[2].lower()) and \
      (fte == 'all' or row[3] == float(fte)) and \
      (job == 'all' or job.lower() in row[9].lower()) and \
      (lastName == 'Default' or lastName.lower() in row[10].lower()):
        matches.append((row[2], row[3], row[5], row[7], row[9], row[10]))

    return jsonify(matches)

  def request_salaries(self):
    url = "https://www.cps.edu/about/finance/employee-position-files/"
    response = str(requests.get(url).content)

    #find most recent salary file
    file_start_pos = response.find(
      "globalassets/cps-pages/about-cps/finance/employee-position-files/")

    file_end_pos = response.find(".xls", file_start_pos) + 4  # add 4 to include ".xls"

    file_url = "https://www.cps.edu/" + response[file_start_pos:file_end_pos]

    file_name = response[file_start_pos + 65:file_end_pos]

    #download file
    if not os.path.isfile(file_name):
      r = requests.get(file_url)
      with open(file_name, 'wb') as f:
        f.write(r.content)

    return file_name


#api endpoint
api.add_resource(Empty, '/')
api.add_resource(
  Info, '/<string:school>/<string:lastName>/<string:job>/<string:fte>')

if __name__ == '__main__':
  t = Thread(target=run)
  t.start()
