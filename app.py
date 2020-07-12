from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from send_email import send_email
from sqlalchemy.sql import func


app=Flask(__name__)
#the first app.config is for local postgresql. it was tested before deploying it on live DB
#app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:postgres123@localhost/height_collector'
app.config['SQLALCHEMY_DATABASE_URI']='postgres://laoxqpvtujozvg:6e2402dc15b78ccf280973bed3a4318c93c68007b184f00ca81843c18e5a4ce2@ec2-54-152-175-141.compute-1.amazonaws.com:5432/ddiui9bukd9fuk?sslmode=require'
db=SQLAlchemy(app)
#we gotta create  this database in heroku addons. then in the heroku python window
#e.g. >>from app import db >> db.create_all() >>exit()
class Data(db.Model):
    __tablename__="data"
    id=db.Column(db.Integer, primary_key=True)
    email_=db.Column(db.String(120), unique=True)
    height_=db.Column(db.Integer)
    
    def __init__(self, email_, height_):
        self.email_=email_
        self.height_=height_
    


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/success", methods=['POST'])
def success():
    if request.method=='POST':
        email=request.form["email_name"]
        height=request.form["height_name"]
        #to be able to add rows with SQLALchemy we should point to the SQLAlchemy object
        #which is db in this case.
        if db.session.query(Data).filter(Data.email_==email).count()==0:   #this line says we input the email only if its unique and not available in db
            data=Data(email,height) # create object instance of Data class
            db.session.add(data)
            db.session.commit()
            average_height=db.session.query(func.avg(Data.height_)).scalar()
            average_height=round(average_height,1)
            count=db.session.query(Data.height_).count()
            send_email(email, height, average_height, count)
            return render_template("success.html")
    return render_template("index.html", 
    text="Seems like we've got something from that email address already!")

if __name__=='__main__':
    app.debug=True
    app.run()