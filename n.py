from flask import Flask, render_template, request, json,session,redirect
from flaskext.mysql import MySQL
from flask_mail import Mail, Message
from random import choice
from string import ascii_lowercase
from random import randint
import hashlib,time

mysql = MySQL()

app = Flask(__name__)
app.config['SECRET_KEY']='thisissecret'
mail=Mail(app)

#email config
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'himanshu.sindhwani@ebizontek.com'
app.config['MAIL_PASSWORD'] = 'hhh9917178530'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'admin123'
app.config['MYSQL_DATABASE_DB'] = 'random'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# index page showing login page
@app.route('/')
def main():
    session['logged_in']=False
    return render_template('login.html')

# sign up page
@app.route('/signup')
def showSignUp():
    return render_template('signup.html')

# backend function to enter the user details into database
@app.route('/sign', methods=['POST', 'GET'])
def sign():
        _name = request.form['inputname']
        _email = request.form['inputemail']
        _password = request.form['inputpassword']
        _pas = hashlib.sha224(_password.encode('utf-8')).hexdigest() #converting password into md5 equivalent
        print("inside login.")

        # validate the received values
        if _name and _email and _password:

            # All Good, let's call MySQL

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("select * from users where email='"+_email+"'")
            conn.commit()
            d=cursor.fetchall()

            #check whether the email is allready registered or not

            if len(d)==0:
                session['edit'] = "Registered successfully!"
                session['url'] = '/'
                con = mysql.connect()
                cursor2=con.cursor()
                cursor2.execute("insert into users(name,email,password) values('"+_name+"','"+_email+"','"+_pas+"')")
                con.commit()
                return render_template("alert.html")

            else:
             session['edit'] = "Email allready exist!"
             session['url'] = '/signup'
             return render_template("alert.html")

        else:
            return json.dumps({'html': '<span>Enter the required fields</span>'})


# Backend function for logging the user in

@app.route('/login',methods=['POST','GET'])
def login():
    time_start = time.time();
    if session['logged_in']==True:
        return render_template('welcome2.html')
    else:
        conn = mysql.connect()
        cursor = conn.cursor()
        email = request.form["email"]
        passw = request.form["password"]
        pas=hashlib.sha224(passw.encode('utf-8')).hexdigest()
        cursor.execute("select name,email,password from users where email='" + email + "' and password='" + pas + "'")
        user = cursor.fetchone()
        if (user):
            session['logged_in'] = True
            session['user'] = user[0]
            session['email'] = user[1]
            session['password'] = user[2]
            time_end=time.time()
            session['time']=time_end-time_start
            return render_template('welcome2.html')
        else:
            session['edit']="Wrong Username/password"
            session['url']="/"
            return render_template('alert.html')

#route to add multiple users in one time

@app.route('/add')
def add():
    conn = mysql.connect()
    cursor = conn.cursor()
    t=''
    count=0
    time_start = time.time()
    p={}
    for i in range(1,101):
        j=''.join(choice(ascii_lowercase) for p in range(randint(1,20)))  #random email generated
        k=''.join(choice(ascii_lowercase) for q in range(randint(1,12)))  #random name generated
        d={i:[j+"@gmail.com",i]}
        p.update(d)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("select uid from users where email='"+ j +"@gmail.com" + "'") # check for collision of email
        conn.commit()
        d = cursor.fetchall()
        if len(d) == 0:
            if (i == 100):
                s = "('" + k + "','" + j + "@gmail.com','" + hashlib.sha224(str(i).encode('utf-8')).hexdigest() + "');"
            else:
                s = "('" + k + "','" + j + "@gmail.com','" + hashlib.sha224(str(i).encode('utf-8')).hexdigest() + "'),"

            t = t + s
        else :
            count=count+1

    print(c)

    session['d']=d
    cursor.execute("insert into users(name,email,password) values "+ t +" ")
    conn.commit()
    time_end = time.time()
    time_net = time_end - time_start
    with open("inserttime.txt","a") as f:
        f.write("time taken to insert "+str(time_net)+"\n")
    return 'ok'

@app.route('/testlogin')
def testlogin():
    t1 = time.time();
    conn = mysql.connect()
    cursor = conn.cursor()
    for i in range(1,len(session['d'])):
        email = session['d'][i][0]
        passw = session['d'][i][1]
        pas = hashlib.sha224(passw.encode('utf-8')).hexdigest()
        cursor.execute("select name,email,password from users where email='" + email + "' and password='" + pas + "'")
        conn.commit()
    t1= time.time()
    time_net=t2-t1

# function to logout the user

@app.route('/logout')
def logout():
    if session['logged_in']:
        session['logged_in']=False
        return redirect('/')
    else:
        return "not logged in!"

# function to edit name of user

@app.route('/name',methods=['GET','POST'])
def name():
    new_name=request.form['nm']
    conn=mysql.connect()
    cursor=conn.cursor()
    u=cursor.execute("update users set name='"+new_name+"' where email='"+session['email']+"' and password='"+session['password']+"' ")
    conn.commit()
    if u:
        session['edit']="name changed successfully !"
        session['user']=new_name
        session['url'] = 'login'
        return render_template('alert.html')
    else:
        return "error"

# edit email of user

@app.route('/email',methods=['GET','POST'])
def email():
    new_mail=request.form['em']
    conn=mysql.connect()
    cursor=conn.cursor()
    u=cursor.execute("update users set email='"+new_mail+"' where email='"+session['email']+"' and password='"+session['password']+"' ")
    conn.commit()
    if u:
        session['edit']="email changed successfully !"
        session['email']=new_mail
        session['url'] = 'login'
        return render_template('alert.html')
    else:
        return "same email entered"

# edit password of user

@app.route('/password',methods=['GET','POST'])
def password():
    new_pass=request.form['pass']
    new_pass=hashlib.sha224(new_pass.encode('utf-8')).hexdigest()
    conn=mysql.connect()
    cursor=conn.cursor()
    u=cursor.execute("update users set password='"+new_pass+"' where email='"+session['email']+"' and password='"+session['password']+"' ")
    conn.commit()
    if u:
        session['edit']="password changed successfully !"
        session['password']=new_pass
        session['url'] = 'login'
        return render_template('alert.html')
    else:
        return "same password repeated"

#forgot Password link
@app.route('/forgot')
def forgot():
    return render_template('forgot.html')

# send mail link to reset the password in case of forgot the pasword

@app.route('/mail',methods=['GET','POST'])
def mailing():
    e=request.form['em']
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("select uid from users where email='"+e+"'")
    conn.commit()
    em=cursor.fetchone()
    if em:
        msg = Message('Hello', sender='himanshu.sindhwani@ebizontek.com', recipients=[e])
        msg.body = "click on this link to reset password: http://localhost:5003/reset?id="+str(em[0])
        mail.send(msg)
        session['edit'] = "Check your email!"
        session['url'] = "/"
        return render_template("alert.html")
    else:
        session['edit']="This email does not belong to any account"
        session['url']="/forgot"
        return render_template("alert.html")

#reset password pasge

@app.route('/reset')
def reset():
    session['anonymous']=request.args.get('id',None)
    return render_template('reset.html')

#backend for password reset

@app.route('/re',methods=['GET','POST'])
def re():
    new_pass=request.form['pass']
    conn=mysql.connect()
    cursor=conn.cursor()
    new_pass=hashlib.sha224(new_pass.encode('utf-8')).hexdigest()
    c=cursor.execute('update users set password="'+new_pass+'" where uid='+session["anonymous"]+' ')
    conn.commit()
    if c :
        session['edit']='password updated successfully'
        session['url']='/'
        return render_template("alert.html")
    else:
        return "error"

#run the python script

if __name__ == "__main__":
    app.run(port=5004,debug=True)

