from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///account.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class statement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.String(500), nullable=False)
    pmeth = db.Column(db.String(200), nullable=False)
    ptype = db.Column(db.String(200), nullable=False)
    loan_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self)-> str:
        return f"{self.id} - {self.name}"

class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    email =db.Column(db.String(200), nullable=False)
    mno =db.Column(db.String(200), nullable=False)
    total_amount = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(200), nullable=False)

    def __repr__(self)-> str:
        return f"{self.id} - {self.name}"



@app.route('/',methods=['GET','POST'])
def hello_world():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mno = request.form['mno']
        amount = request.form['amount']
        ptype = request.form['ptype']
        pmeth = request.form['pmeth']
        statementdata = statement(name=name,amount=amount,pmeth=pmeth,ptype=ptype)
        userdata = user(username=name,email=email,mno=mno,total_amount=amount,status='Loaned')
        db.session.add(statementdata)
        db.session.add(userdata)
        db.session.commit()
        return redirect("/")
    alluser = user.query.all()
    return render_template("index.html", users=alluser)
@app.route('/delete/<int:id>',methods=['GET','POST'])
def delete(id):
    data = statement.query.filter_by(id=id).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(f"/user/{data.name}")


@app.route('/payment/<name>',methods=['GET','POST'])
def partial_pay(name):
    if request.method == 'POST':
        amount = request.form['amount']
        ptype = request.form['ptype']
        pmeth = request.form['pmeth']
        statementdata = statement(name=name,amount=amount,pmeth=pmeth,ptype=ptype)
        db.session.add(statementdata)
        db.session.commit()
        return redirect(f"/user/{name}")
    paydata = user.query.filter_by(username=name).first()
    return render_template("payment.html", paydata=paydata)

@app.route('/refresh/<name>')
def refresh(name):
    userstatement = statement.query.filter_by(name=name).all()
    credit = 0
    debit = 0
    for pay in userstatement:
        if pay.ptype == 'Credit':
            credit += int(pay.amount)
        elif pay.ptype == 'Debit':
            debit += int(pay.amount)
    total=debit-credit
    data = user.query.filter_by(username=name).first()
    data.total_amount = total
    db.session.add(data)
    db.session.commit()
    return redirect("/")

@app.route('/user/<name>',methods=['GET','POST'])
def users(name):
    userstatement = statement.query.filter_by(name=name).all()
    credit = 0
    debit = 0
    for pay in userstatement:
        if pay.ptype == 'Credit':
            credit += int(pay.amount)
        elif pay.ptype == 'Debit':
            debit += int(pay.amount)
    total = debit-credit
    users = user.query.filter_by(username=name).first()
    users.total_amount = total
    db.session.add(users)
    db.session.commit()
    return render_template("user.html",user=users,statement=userstatement,credit=credit,debit=debit)

if __name__ == '__main__':
    app.run(debug=True,port=3110)

