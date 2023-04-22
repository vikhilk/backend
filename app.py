from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
import os
from flask_cors import CORS, cross_origin
import json
import pandas as pd




# Init app
app = Flask(__name__)
app.app_context().push()
cors = CORS(app)
app.config['CORS_HEADERS'] = 'application/json'
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# Product Class/Model
class Quize(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  que = db.Column(db.String(200),unique=True)
  opt1 = db.Column(db.String(200))
  opt2 = db.Column(db.String(200))
  opt3 = db.Column(db.String(200))
  opt4 = db.Column(db.String(200))
  correct_ans = db.Column(db.String(200))

  def __init__(self, que, opt1, opt2, opt3,opt4,correct_ans):
    self.que = que
    self.opt1 = opt1
    self.opt2 = opt2
    self.opt3 = opt3
    self.opt4 = opt4
    self.correct_ans = correct_ans

# Product Schema
class QuizeSchema(ma.Schema):
  class Meta:
    fields = ('id', 'que', 'opt1', 'opt2', 'opt3','opt4','correct_ans')

# Init schema
Quize_schema = QuizeSchema()
Quizes_schema = QuizeSchema(many=True)


#Create a quiz

@app.route('/quize',methods=['POST'])

def add_quizes():
  que = request.json['que']
  opt1= request.json['opt1']
  opt2= request.json['opt2']
  opt3= request.json['opt3']
  opt4= request.json['opt4']
  correct_ans= request.json['correct_ans']

  new_quize = Quize(que,opt1,opt2,opt3,opt4,correct_ans)
  db.session.add(new_quize)
  db.session.commit()
  db.create_all()

  return Quize_schema.jsonify(new_quize)

#excel upload data into db

@app.route('/UploadExcel',methods=["POST"])
def submitExcelFile():
  quizes = []
  data = request.files['file']
  data.save(data.filename)
  df_excel = pd.ExcelFile(data.filename)
  list_of_dfs = []

  for sheet in df_excel.sheet_names:
    df = df_excel.parse(sheet)
    list_of_dfs.append(df)

  data = pd.concat(list_of_dfs,ignore_index=True)

  print(data)
  df_json = json.loads(data.to_json(orient="records"))

  print(df_json)
  for jsondata in df_json:
    que = jsondata['que']
    opt1= jsondata['opt1']
    opt2= jsondata['opt2']
    opt3= jsondata['opt3']
    opt4= jsondata['opt4']
    correct_ans= jsondata['correct_ans']

    new_quize = Quize(**jsondata)
    quizes.append(new_quize)
    print(new_quize)

  db.session.add_all(quizes)
  db.session.commit()

  [db.session.refresh(quizedata) for quizedata in quizes]

  return Quize_schema.jsonify(quizes)


@app.route('/quizes',methods=['GET'])
def get_quizes():
  all_quizes = Quize.query.all()
  result = Quize_schema.dump(all_quizes)
  return jsonify(result)





#login
class Login(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100))
  username = db.Column(db.String(200))
  password = db.Column(db.String(200))
  email = db.Column(db.String(200))
  role = db.Column(db.String(200))
  

  def __init__(self, name,username, password,email, role):
    self.name = name
    self.username = username
    self.password = password
    self.email = email
    self.role = role
    

# Product Schema
class LoginSchema(ma.Schema):
  class Meta:
    fields = ('id', 'name','username', 'password','email', 'role')

# Init schema
login_schema = LoginSchema()
logins_schema = LoginSchema(many=True)


# Create a User
@app.route('/user', methods=['POST'])

def add_user():
  name = request.json['name']
  username = request.json['username']
  password = request.json['password']
  email = request.json['email']
  role = request.json['role']

  new_user = Login(name,username, password,email,role)
  print(new_user)
  db.session.add(new_user)
  db.session.commit()

  return login_schema.jsonify(new_user)

# Get All Users
@app.route('/users', methods=['GET'])
def get_users():
  all_users = Login.query.all()
  result = logins_schema.dump(all_users)
  return jsonify(result)

# Get Single User
@app.route('/user/<id>', methods=['GET'])
def get_user(id):
  user = Login.query.get(id)
  return login_schema.jsonify(user)

#AdminDashboard Model

class AdminDashboard(db.Model):
  id=db.Column(db.Integer,primary_key=True)
  username = db.Column(db.String(200))
  marksGot = db.Column(db.Integer)
  correct_ans = db.Column(db.String(200))
  que_attempt = db.Column(db.String(200))
  email = db.Column(db.String(200))

  db.create_all()

  def __init__(self,username,marksGot,correct_ans,que_attempt,email):
    self.username = username
    self.marksGot = marksGot
    self.correct_ans = correct_ans
    self.que_attempt = que_attempt
    self.email = email

class AdminDashboardSchema(ma.Schema):
  class Meta:
    fields = ('id','username','marksGot','correct_ans','que_attempt','email')

admindashboard_schema = AdminDashboardSchema()
admindashboards_schema = AdminDashboardSchema(many=True)


@app.route('/admindata',methods=['POST'])

def admin_data():
  username = request.json['username']
  marksGot = request.json['marksGot']
  correct_ans = request.json['correct_ans']
  que_attempt = request.json['que_attempt']
  email = request.json['email']

  admin_table = AdminDashboard(username,marksGot,correct_ans,que_attempt,email)
  db.session.add(admin_table)
  db.session.commit()
  db.create_all()

  return admindashboard_schema.jsonify(admin_table)

@app.route('/admindata',methods=['GET'])
def get_admin_tbl():
  all_users_data = AdminDashboard.query.order_by(AdminDashboard.marksGot.desc())
  result = admindashboard_schema.dump(all_users_data)
  return jsonify(result)



# Run Server
if __name__ == '__main__':
  app.run(debug=True)

  db.session.query(Quize).delete()
  db.session.commit()