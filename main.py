from flask import Flask,render_template,request,redirect,flash,url_for,session
import sqlite3
conn=sqlite3.connect('anto.db')
print('opened database successfully')

app=Flask(__name__)
app.secret_key = '123'

con=sqlite3.connect("anto.db",check_same_thread=False)
con.execute("create table if not exists customer(pid integer primary key,username text,email text unique,password text,balance REAL DEFAULT 0)")
cur=con.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
            
        con=sqlite3.connect("anto.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from customer where username=? ",(username,))
        data=cur.fetchone()

        '''if data:
            session["username"]=data["username"]
            session["password"]=data["password"]
            return redirect("customer")'''
        
        if data is None:
            error1=("username does not exist")
            return render_template("index.html",error1=error1)
        
        elif data is not None and password not in data:
            error2=("password is wrong")
            return render_template("index.html",error2=error2)
        
        else:
            session["username"]=data["username"]
            session["password"]=data["password"]
            return redirect("customer")
            
            #flash("Username and Password Mismatch","danger")

    return redirect(url_for("index"))
    

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']

        with sqlite3.connect("anto.db") as con:
            cur=con.cursor()
            cur.execute("select * from customer where email=?",(email,))
            data=cur.fetchone()
        
            if data:
                error1=("email is already exist")
                return render_template("signup.html",error1=error1)
           
            con.execute("insert into customer(username,email,password) values(?,?,?)",(username,email,password))
            con.commit()
            
            
            flash('success!')
            return redirect('/')

            

    return render_template('signup.html')

@app.route('/customer',methods=["GET","POST"])
def customer():
    return render_template("customer.html")        

@app.route('/dblist')
def dblist():
    
    # con.row_factory=sqlite3.Row
   
    cur.execute("select * from customer")
    data=cur.fetchall()
    #print(data)
    return render_template('dblist.html',data=data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))



@app.route('/balance')
def balance():
    if 'username' in session:
        
        with sqlite3.connect("anto.db") as con:
            cur=con.cursor()
            cur.execute('SELECT * FROM customer WHERE username = ?', (session['username'],))
            user=cur.fetchone()

        return render_template('balance.html', user=user)
    else:
        return redirect('/')    

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        amount = float(request.form['amount'])

        with sqlite3.connect("anto.db") as con:
            cur=con.cursor()
            cur.execute('UPDATE customer SET balance = balance + ? WHERE username = ?', (amount, session['username']))
            con.commit()
        

        return redirect('/customer')
    
    return render_template('deposit.html')

@app.route('/withdrawal', methods=['GET', 'POST'])
def withdrawal():
    if request.method == 'POST':
        amount = float(request.form['amount'])

        with sqlite3.connect("anto.db") as con:
            cur=con.cursor()
            cur.execute('SELECT * FROM customer WHERE username = ?', (session['username'],))
            user=cur.fetchone()
            con.commit()

            if amount < user[4]:
                cur.execute('UPDATE customer SET balance = balance - ? WHERE username = ?', (amount, session['username']))
                con.commit()
            

                return redirect('/customer')
            else:
                error = 'Insufficient balance.'
                return render_template('withdrawal.html', error=error)
    
    return render_template('withdrawal.html')

app.run(debug=True)