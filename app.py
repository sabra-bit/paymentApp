from flask import Flask,redirect, render_template,request, session ,flash ,jsonify,Response,url_for
from datetime import datetime ,date,timedelta
import  sqlite3,cryptocode , json 

from fawryAPIcall import call
conn = sqlite3.connect("data.db")


app = Flask(__name__)
app.secret_key = 'anybetngan'
app.permanent_session_lifetime = timedelta(minutes=66731)
session_cookie_samesite=app.config["SESSION_COOKIE_SAMESITE"]

@app.route("/")
def routePage():
    # return render_template("home.html")
  return render_template("login.html")
@app.route("/signup")
def signupPage():
  return render_template("signup.html")

@app.route('/createUser', methods=['POST'])
def createUser():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    accounttype = request.form['accounttype']
    ip_address = request.remote_addr
    time = datetime.now()
    if not len(str(password))  > 8:
      flash('Password must be at least 8 characters long! and contain at least one letter! ')
      return redirect('/signup')
    
    
    conn = sqlite3.connect("data.db")

    c = conn.cursor()
    Data = c.execute("""SELECT * FROM Users""").fetchall()
    
    
    for data in Data:
        
        if email == data[1] :
          flash('choose anther email !')
          return redirect('/signup')
   
    
    time = datetime.now()
    c.execute("""INSERT INTO Users (username, password, name, roll , actiontime) VALUES (?, ?,?,?,?)""", (email, password, name, accounttype,str(time)))
    conn.commit()
    
    if accounttype == "Money Depositor":
        conn = sqlite3.connect("data.db")

        c = conn.cursor()
        c.execute(
                'insert into userPages (userName,pageName,urlPage) values(?,?,?);',
                (str(email),str('Home'),str('/user'))
                )
        
        c.execute(
                'insert into userPages (userName,pageName,urlPage) values(?,?,?);',
                (str(email),str('Child'),str('/child'))
                )
        c.execute(
                'insert into userPages (userName,pageName,urlPage) values(?,?,?);',
                (str(email),str('View Transaction'),str('/viewtransaction'))
                )
        conn.commit()
    elif accounttype == 'Merchant':
        conn = sqlite3.connect("data.db")

        c = conn.cursor()
        c.execute(
                'insert into userPages (userName,pageName,urlPage) values(?,?,?);',
                (str(email),str('Merchant'),str('/merchant'))
                )
        
        c.execute(
                'insert into userPages (userName,pageName,urlPage) values(?,?,?);',
                (str(email),str('View Transaction'),str('/viewtransaction'))
                )
        conn.commit()
      
    flash('Congratulations, you are now a registered user!')
    
    return redirect('/')
    

@app.route('/auth', methods=['POST'])
def auth():

    user = request.form['username']
    password = request.form['password']
    ip_address = request.remote_addr
    time = datetime.now()
    # to add login info
    conn = sqlite3.connect("data.db")

    c = conn.cursor()
    Data = c.execute("""SELECT * FROM Users""").fetchall()
    
    flag = False
    for data in Data:
        
        if user ==data[1] and password==data[2]:
            session['username'] =user
            session['name'] =data[3]
            session['role'] =data[4]
            session['password'] = data[2]
            flag = True
            break;
    c.close()
    if flag and session.get('role') == "admin":
        return redirect('/admin')
    elif session.get('role') == "Money Depositor" :
        return redirect('/user')
    elif session.get('role') == "Merchant" :
        ip_address = request.remote_addr
        conn = sqlite3.connect("data.db")

        c = conn.cursor()
        IP = c.execute("SELECT * FROM Network").fetchall()
        flagIP = False
        for ip in IP:
            if ip_address == ip[1] or ip[1] == "0.0.0.0":
                flagIP = True
        
        if not flagIP:
            session.pop("username",None)
            session.pop("role",None)
            session.pop("name",None)
            session.pop("password",None)
            flash('Invalid Location')
            return redirect("/")
        return redirect('/merchant')    
    else:
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Data = c.execute("""SELECT * FROM Children""").fetchall()
        flag = False
        for data in Data:
            print(data)
            if user ==data[2] and password==data[4]:
                
                session['username'] =data[2]
                session['name'] =data[3]
                session['role'] ='child'
                session['password'] = data[4]
                flag = True
                break;
        if flag and session.get('role') == 'child':
            return redirect('/childuser')  
        flash('bad usename or password')
        return redirect("/")

@app.route('/childuser', methods=['POST','GET'])
def childuser():
    if ( session.get('role') == "child" ) and request.method == 'GET':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'Home')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return redirect('/')
        amount = c.execute("SELECT * FROM Children where childEmail = ?  ;",([session['username']])).fetchall()[0][5]
        print(amount)
        return render_template("childUser.html",name = session['name'] ,email= session['username'],Pages =Pages ,amount=amount)
    
    elif ( session.get('role') == "child" ) and request.method == 'POST':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'Home')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return redirect('/')
        amount = c.execute("SELECT * FROM Children where childEmail = ?  ;",([session['username']])).fetchall()[0][5]
        print(amount)
        data =json.loads(request.data)
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS Transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        FromT TEXT NOT NULL,
        ToT TEXT NOT NULL,
        cardNumber TEXT NOT NULL,
        CVV TEXT NOT NULL,
        expierDate TEXT NOT NULL,
        value REAL NOT NULL,
        transactionType TEXT NOT NULL,
        actionTime TEXT NOT NULL
        )""")
        conn.commit()
        conn = sqlite3.connect("data.db")
        time1 = datetime.now()
        time3 = time1.strftime("%H:%M:%S")
        time3 = datetime.strptime(time3, "%H:%M:%S")
        time2 = datetime.strptime(data['creationTime'], "%H:%M:%S")
        thirty_minutes = timedelta(minutes=30)
        print(data )
        if (time3 < time2 ) and ((time3 - time2) > thirty_minutes):
            flash('Invalid QR Code.')
            return 'done'
        if float(data['value']) > float(amount):
            flash('insufficient fund.')
            return 'done'
        
        c = conn.cursor()
        c.execute("""INSERT INTO Transactions (FromT, ToT, cardNumber, CVV , expierDate,value,transactionType,actionTime) 
                    VALUES (?, ?, ?, ? , ?,?,?,?)"""
                    , (str(data['childEmail']), str(data['mercent']), "merchent payment",  "000",  "000",  str(data['value']),'Local Transaction',str(time1)))
        c.execute("UPDATE  Children  SET [value] =  [value] - ?   WHERE childEmail = ?",[(str(data['value'])),(str(data['childEmail']))])
        conn.commit()
        flash('Payment done Successfully.')
        return 'done'
    else:
        flash('requested page not found')
        return redirect('/')

@app.route('/merchant', methods=['POST','GET'])
def merchant():
    if ( session.get('role') == "Merchant" ) and request.method == 'GET':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'Merchant')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return redirect('/')
        return render_template("merchant.html",name = session['name'] ,email= session['username'],Pages =Pages)
    else:
        flash('requested page not found')
        return redirect('/')
    

@app.route('/tailor', methods=['POST','GET'])
def tailor():
    if ( session.get('role') == "Merchant" ) and request.method == 'GET':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'Tailor')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return redirect('/')
        return render_template("tailor.html",name = session['name'] ,email= session['username'],Pages =Pages)
    if ( session.get('role') == "Merchant" ) and request.method == 'POST':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'Tailor')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return redirect('/')
        data =json.loads(request.data)
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS Transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        FromT TEXT NOT NULL,
        ToT TEXT NOT NULL,
        cardNumber TEXT NOT NULL,
        CVV TEXT NOT NULL,
        expierDate TEXT NOT NULL,
        value REAL NOT NULL,
        transactionType TEXT NOT NULL,
        actionTime TEXT NOT NULL
        )""")
        conn.commit()
        conn = sqlite3.connect("data.db")
        time = datetime.now()
        print(data)
        c = conn.cursor()
        c.execute("""INSERT INTO Transactions (FromT, ToT, cardNumber, CVV , expierDate,value,transactionType,actionTime) 
                    VALUES (?, ?, ?, ? , ?,?,?,?)"""
                    , (str(data['mercent']), str(data['childEmail']), "manual transfer",  "000",  "000",  str(data['value']),'Local Transaction',str(time)))
        c.execute("UPDATE  Children  SET [value] =  [value] + ?   WHERE childEmail = ?",[(str(data['value'])),(str(data['childEmail']))])
        conn.commit()
        flash('Transaction done Successfully.')
        return 'done'
        
    else:
        flash('requested page not found')
        return redirect('/')
    
    
@app.route("/logOut")
def Logout():
    name = session['name']
    session.pop("username",None)
    session.pop("role",None)
    session.pop("name",None)
    # session.pop("Pages",None)
    flash(name + ' logout')
    return redirect('/')
@app.route('/admin', methods=['POST' ,'GET'])
def usersData():
    if session.get('role') == "admin" and request.method == 'GET':
        conn = sqlite3.connect("data.db")

        c = conn.cursor()
        Data = c.execute("""SELECT * FROM Users""").fetchall()
        c.execute("""CREATE TABLE IF NOT EXISTS Pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        urlPage TEXT NOT NULL,
        pageName TEXT NOT NULL
        )""")
        Page = c.execute("SELECT * FROM Pages").fetchall()
        return render_template("usersData.html",name = session['name'] , Data=Data ,Page=Page)
    elif session.get('role') == "admin" and request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        conn = sqlite3.connect("data.db")

        c = conn.cursor()
        Data = c.execute("""SELECT * FROM Users WHERE username = ?""", ([email])).fetchall()
        print(Data)
        if Data:
            flash('type another email ')
            return redirect('/admin')
        else:
            time = datetime.now()
       
            c.execute("""INSERT INTO Users (username, password, name, roll, actiontime) VALUES (?, ?,?,?,?)""", (email, password, name, role,str(time)))
            conn.commit()
            flash('user added successfully ')
            return redirect('/admin')
    else:
        flash('requested page not found')
        return redirect('/')
@app.route('/Network', methods=['POST' ,'GET'])
def Network():
    if session.get('role') == "admin" and request.method == 'GET':
        conn = sqlite3.connect("data.db")

        c = conn.cursor()
        
        c.execute("""CREATE TABLE IF NOT EXISTS Network (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        IP TEXT NOT NULL
        )""")
        Data = c.execute("SELECT * FROM Network").fetchall()
        conn.commit()
        return render_template("network.html",name = session['name'], Data=Data)
    elif session.get('role') == "admin" and request.method == 'POST':
        data =json.loads(request.data)
        if data['ActionType'] == 'delete':
            conn = sqlite3.connect("data.db")

            c = conn.cursor()
            c.execute("DELETE FROM Network WHERE IP = ?",[(str(data['ip']))])
            conn.commit()
            flash('IP deleted')
            return 'Done'
        elif data['ActionType'] == 'add':
            conn = sqlite3.connect("data.db")

            c = conn.cursor()
            Data = c.execute("SELECT * FROM Network WHERE IP = ?",[(str(data['ip']))]).fetchall()
            conn.commit()
            if not Data:
                c.execute("""INSERT INTO Network (IP) VALUES (?)""", [(str(data['ip']))])
                conn.commit()
                
                flash('IP add')
            else:
                flash('IP exist')
            return 'Done'
    else:
        flash('requested page not found')
        return redirect('/')

@app.route('/editDeletePage', methods=['POST' ,'GET'])
def editDeletePage():
    if session.get('role') == "admin" and request.method == 'POST':
        data =json.loads(request.data)
        conn = sqlite3.connect("data.db")

        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS userPages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userName TEXT NOT NULL,
        urlPage TEXT NOT NULL,
        pageName TEXT NOT NULL
        )""")
        
        
        if data['ActionType'] == 'delete':
            c.execute("DELETE FROM userPages WHERE [userName] = ? and [pageName] = ?",[(str(data['userName'])),(str(data['PageName']))])
            conn.commit()
            
            return 'page deleted'
        elif data['ActionType'] == 'add':
            print(data['PageName'])
            Data = c.execute(
            'SELECT * FROM userPages where userName = ? and pageName = ?',
            ((str(data['userName'])),(str(data['PageName'])))
            ).fetchall()
            if (str(data['PageName'])) == "":
                return"page not selected"
            if Data:
                return "page exist"
            else:
                
                c.execute(
                'insert into userPages (userName,pageName,urlPage) values(?,?,?);',
                (str(data['userName']),str(data['PageName']),str(data['URL']))
                )
                conn.commit()
            
                return 'page added'
        elif data['ActionType'] == 'view':
            time = datetime.now()
            data = c.execute(
            'SELECT [pageName] FROM userPages where userName = ?',
            ([str(data['userName'])])
            ).fetchall()
            conn.commit()
            print(data)
            return str(data).replace(']', '').replace('[', '').replace(',)', '').replace('(', '')
        else:
            flash('requested page not found')
            return redirect('/')
    else:
        flash('requested page not found')
        return redirect('/')



@app.route('/editDeleteUser', methods=['POST' ,'GET'])
def updateDeleteUser():
    if session.get('role') == "admin" and request.method == 'POST':
        data =json.loads(request.data)
        conn = sqlite3.connect("data.db")

        c = conn.cursor()
        if data['ActionType'] == 'delete':
            c.execute("DELETE FROM Users WHERE id = ?",[(str(data['userId']))])
            conn.commit()
            flash('user deleted')
            return 'Done'
        elif data['ActionType'] == 'edit':
            c.execute("UPDATE  Users  SET [name] = ? ,[passWord] = ?  WHERE id = ?",[(str(data['name'])),(str(data['password'])),(str(data['userId']))])
            conn.commit()
            flash('user updated')
            return 'Done'
        else:
            flash('requested page not found')
            return redirect('/')
    else:
        flash('requested page not found')
        return redirect('/')
@app.route('/Transition', methods=['GET'])
def Transition():
    if session.get('role') == "admin" and request.method == 'GET':
        conn = sqlite3.connect("data.db")
        
        c = conn.cursor()
        Data = c.execute(
            'SELECT * FROM transactions '
            ).fetchall()
        return render_template("Transition.html",name = session['name'], Data=Data)

@app.route('/user', methods=['POST','GET'])
def UserApp():
    if (session.get('role') == "Money Depositor" or session.get('role') == "Money Depositor" ) and request.method == 'GET':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'Home')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return redirect('/')
        return render_template("home.html",name = session['name'] ,email= session['username'],Pages =Pages)
    else:
        flash('requested page not found')
        return redirect('/')
    
@app.route('/child', methods=['POST','GET'])
def child():
    if (session.get('role') == "Money Depositor" ) and request.method == 'GET':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'Child')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return redirect('/')
        
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS Children (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent TEXT NOT NULL,
        childEmail TEXT NOT NULL,
        childName TEXT NOT NULL,
        childPassword TEXT NOT NULL,
        value REAL NOT NULL
        )""")
        Data = c.execute("""SELECT * FROM Children WHERE parent = ?  """, ([session['username']])).fetchall()
        
        return render_template("child.html",name = session['name'] ,email= session['username'],Pages =Pages ,Data=Data)
    else:
        flash('requested page not found')
        return redirect('/')  
    
 

@app.route('/viewtransaction', methods=['POST','GET'])
def viewtransaction():
    if (session.get('role') == "Money Depositor" or session.get('role') == "Merchant" or session.get('role') == "child" ) and request.method == 'GET':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'View Transaction')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return redirect('/')
        
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS Transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                FromT TEXT NOT NULL,
                ToT TEXT NOT NULL,
                cardNumber TEXT NOT NULL,
                CVV TEXT NOT NULL,
                expierDate TEXT NOT NULL,
                value REAL NOT NULL,
                transactionType TEXT NOT NULL,
                actionTime TEXT NOT NULL
                )""")
        Data = c.execute("""SELECT * FROM Transactions WHERE FromT  = ? or ToT  = ?  """, (session['username'] ,session['username'] )).fetchall()
        
        return render_template("Transaction.html",name = session['name'] ,email= session['username'],Pages =Pages ,Data=Data)
    else:
        flash('requested page not found')
        return redirect('/') 
    
    
    
    
      
@app.route('/parentAPI', methods=['POST','GET'])
def parent():
    if (session.get('role') == "Money Depositor" ) and request.method == 'POST':
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        Pages = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ?  ;",([session['username']])).fetchall()
        pageAutherization = c.execute("SELECT urlPage ,pageName FROM userPages where userName = ? and pageName = ? ;",(session['username'],'Child')).fetchall()
        if not pageAutherization:
            flash('requested page not found')
            return "Not Allowed"
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS Children (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent TEXT NOT NULL,
        childEmail TEXT NOT NULL,
        childName TEXT NOT NULL,
        childPassword TEXT NOT NULL,
        value REAL NOT NULL
        )""")
        
        data =json.loads(request.data)
        
        if data['ActionType'] == 'addChild':
            c = conn.cursor()
            Data = c.execute("""SELECT * FROM Children WHERE parent = ? and childEmail = ? """, (str(data['parent']),str(data['childEmail']))).fetchall()
            
            if Data:
                flash('already exist.')
                return 'done'
            c.execute("""INSERT INTO Children (parent, childEmail, childName, childPassword , value) VALUES (?, ?,?,?,?)""", (str(data['parent']), str(data['childEmail']), str(data['childName']),  str(data['childPassword']),0.0))
            
            c.execute(
                    'insert into userPages (userName,pageName,urlPage) values(?,?,?);',
                    (str(data['childEmail']),str('Home'),str('/childuser'))
                    )
            
            c.execute(
                    'insert into userPages (userName,pageName,urlPage) values(?,?,?);',
                    (str(data['childEmail']),str('View Transaction'),str('/viewtransaction'))
                    )
            conn.commit()
            
            conn.commit()
            
            flash('Child Added Successfully.')
            return 'done'
        if data['ActionType'] == 'ViewChaild':
            c = conn.cursor()
            Data = c.execute("""SELECT * FROM Transactions WHERE FromT = ? or ToT = ? """, (str(data['childEmail']),str(data['childEmail']))).fetchall()
            

            return jsonify(Data)
        if data['ActionType'] == 'PAY':
            
            try:
                conn = sqlite3.connect("data.db")
                c = conn.cursor()
                c.execute("""CREATE TABLE IF NOT EXISTS Transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                FromT TEXT NOT NULL,
                ToT TEXT NOT NULL,
                cardNumber TEXT NOT NULL,
                CVV TEXT NOT NULL,
                expierDate TEXT NOT NULL,
                value REAL NOT NULL,
                transactionType TEXT NOT NULL,
                actionTime TEXT NOT NULL
                )""")
                conn.commit()
                response  = call(data['CardNumber'] , data['ExpiryDate'].split("/")[1]  , data['ExpiryDate'].split("/")[0] , data['CVV'] , data['value'] )
                print(json.loads(response.text)['statusDescription'])
                if json.loads(response.text)['statusDescription'] == 'Operation done successfully':
                    
                    conn = sqlite3.connect("data.db")
                    time = datetime.now()
                    print(data)
                    c = conn.cursor()
                    c.execute("""INSERT INTO Transactions (FromT, ToT, cardNumber, CVV , expierDate,value,transactionType,actionTime) 
                              VALUES (?, ?, ?, ? , ?,?,?,?)"""
                              , (str(data['parent']), str(data['childEmail']), str(data['CardNumber']),  str(data['CVV']),  str(data['ExpiryDate']),  str(data['value']),'Bank Transaction',str(time)))
                    c.execute("UPDATE  Children  SET [value] =  [value] + ?   WHERE childEmail = ?",[(str(data['value'])),(str(data['childEmail']))])
                    conn.commit()
                    flash('Transaction done Successfully.')
                    return 'done'
                else:
                    flash('Transaction failed or insufficient fund.')
                    
                    return 'done'
            except:
                flash('Transaction failed try again later.')
                    
                return 'done' 
            # c = conn.cursor()
            # Data = c.execute("""SELECT * FROM Children WHERE parent = ? and childEmail = ? """, (str(data['parent']),str(data['childEmail']))).fetchall()
            
            # if Data:
            #     flash('already exist')
            #     return 'done'
            # c.execute("""INSERT INTO Children (parent, childEmail, childName, childPassword , value) VALUES (?, ?,?,?,?)""", (str(data['parent']), str(data['childEmail']), str(data['childName']),  str(data['childPassword']),0.0))
            # conn.commit()
            
            
        
        
        
            
        flash('requested page not found')
        return 'done'
    else:
        flash('requested page not found')
        return "Not Allowed"


if __name__ == "__main__":
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    Table = c.execute(f"""SELECT name FROM sqlite_master WHERE type='table' AND name='Users';""").fetchall()
    if Table:
        print(f"Table user exists")
    else:
        print(f"Table user does not exist")
        c.execute("""CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        roll TEXT NOT NULL,
        actiontime TEXT NOT NULL
        )""")
        time = datetime.now()
        c.execute("""INSERT INTO Users (username, password, name, roll , actiontime) VALUES (?, ?,?,?,?)""", ("armada@test.com", "123", "sabra", "admin",str(time)))
        conn.commit()
    c.close()  
    
    
    
    app.run(debug=True)
