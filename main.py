from flask import Flask, json,redirect,render_template,flash,request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user
from flask.globals import request,session
from flask.helpers import url_for
from werkzeug.security import generate_password_hash,check_password_hash
from flask_mail import Mail




#mydatabase connection
local_server=True
app=Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key="nethravathib"

with open('/DBMS PROJECT/backend/config.json','r') as c:
    params=json.load(c)["params"]

app.config.update (
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
     )
mail = Mail(app)

#this is for getting the unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'


#app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:password@localhost/databasename'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/placement'
db=SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    return student.query.get(int(user_id)) or companyuser.query.get(int(user_id)) or student.query.get(int(user_id))

class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String[30])

class student(UserMixin, db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String[20],unique=True)
    password=db.Column(db.String[1000])
    email=db.Column(db.String[50])

class companyuser(UserMixin, db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    ccode=db.Column(db.String[20],unique=True)
    email=db.Column(db.String[50]) 
    password=db.Column(db.String[1000])  

class companydata(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    ccode=db.Column(db.String(20),unique=True)
    cname=db.Column(db.String(100))
    cemail=db.Column(db.String(100))
    no_jobs=db.Column(db.Integer)
    job_title=db.Column(db.String(100))
    skills_required=db.Column(db.String(100))

class trig(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    ccode=db.Column(db.String(20),unique=True)
    no_jobs=db.Column(db.Integer)
    job_title=db.Column(db.String(100))
    querys=db.Column(db.String(50))
    date=db.Column(db.String(50))


class applyingjob(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True)
    ccode=db.Column(db.String(100))
    jobtype=db.Column(db.String(100))
    studentname=db.Column(db.Integer)
    studentaddress=db.Column(db.String(100))
    usn=db.Column(db.String(100)) 
    cgpa=db.Column(db.Integer)    
     


@app.route("/")
def home():
    return render_template("/index.html")

@app.route("/trigers")
def trigers():
    query=trig.query.all()
    return render_template("/trigers.html",query=query)    

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        Username=request.form.get('username')
        password=request.form.get('password')
        email=request.form.get('email')
        #print(username,password,email)
        encpassword=generate_password_hash(password)
        Student=student.query.filter_by(username=Username).first()
        emailuser=student.query.filter_by(email=email).first()
        if Student or emailuser :
            flash("Email or username is already taken","warning")
            return render_template("/studentsignup.html")

        new_user=db.engine.execute(f"INSERT INTO `student` (`username`,`password`,`email`) VALUES('{Username}','{encpassword}','{email}')")
        flash("SignUp success,Please Login","success")
        return render_template("/studentlogin.html")
   
    return render_template("/studentsignup.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))

@app.route('/adminlogout')
def adminlogout():
    session.pop('user')
    flash("you are logout admin","primary")
    return redirect('/admin')

@app.route('/addcomuser',methods=['POST','GET'])
def addcomuser(): 
    

    if('user' in session and session['user']==params['user'] ):
        
        if request.method=="POST":
            ccode=request.form.get('ccode')
            email=request.form.get('email')
            password=request.form.get('password')
            encpassword=generate_password_hash(password)
            ccode=ccode.upper()
            emailuser=companyuser.query.filter_by(email=email).first()

            if emailuser :
               flash("Email already taken","warning")
               
            db.engine.execute(f"INSERT INTO `companyuser` (`ccode`,`email`,`password`) VALUES('{ccode}','{email}','{encpassword}')")
           

            mail.send_message('PLACEMENT MANAGEMENT SYSTEM',sender=params['gmail-user'],recipients=[email],body=f"Welcome thanks for choosing us\nYour login credentials are:\n Email Address:{email}\nPassword:{password}\n\n\n company code:{ccode}\n\n\n Do not share your password\n\n Thank you...  ")
            flash("Data sent and inserted successfully","success")
            return render_template("addcomuser.html")
    else:
        flash("Login and Try Again","warning")
        return redirect('/admin')
    return render_template("addcomuser.html")    

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        Username=request.form.get('username')
        password=request.form.get('password')
        Student=student.query.filter_by( username = Username).first()

        if Student and check_password_hash(Student.password,password):
            login_user(Student)
            flash("Login success","info")
            return render_template("/index.html")
        else:
            flash("invalid credentials","danger")
            return render_template("/studentlogin.html")
            
    return render_template("/studentlogin.html")

@app.route('/companylogin',methods=['POST','GET'])
def companylogin():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=companyuser.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","info")
            return render_template("/index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("/companylogin.html")

    return render_template("/companylogin.html")        

@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method=="POST":
        Username=request.form.get('username')
        password=request.form.get('password')
        if ( Username==params['user'] and password==params['password'] ):
            session['user']=Username
            flash("login success","info")
            return render_template("/addcomuser.html")
        else:
            flash("invalid credentials","danger")
           
    return render_template("/admin.html")

@app.route("/addcompanyinfo",methods=['POST','GET'])
def addcompanyinfo():
 
   email= current_user.email
   posts=companyuser.query.filter_by(email=email).first()
   code=posts.ccode
   postsdata=companydata.query.filter_by(ccode=code).first()
   
   if request.method=="POST":
        ccode=request.form.get('ccode')
        cname=request.form.get('cname')
        cemail=request.form.get('cemail')
        njobs=request.form.get('no_jobs')
        title=request.form.get('job_title')
        skills=request.form.get('skills_required')
        ccode=ccode.upper()
        cuser=companyuser.query.filter_by(ccode=ccode).first()
        cduser=companydata.query.filter_by(ccode=ccode).first()
        if cduser:
          flash("Data is already Present you can update it..","primary")
          return render_template("/companydata.html")
        if cuser:
            db.engine.execute(f"INSERT INTO `companydata` ( `ccode`,`cname`,`cemail`,`no_jobs`,`job_title`,`skills_required` ) VALUES('{ccode}','{cname}','{cemail}','{njobs}','{title}','{skills}' ) ")
            flash("Data is added","primary")
        else:
            flash("Company code doesnt exists","warning")
   
   return render_template("/companydata.html",postsdata=postsdata)

@app.route("/cedit/<string:id>",methods=['POST','GET'])
@login_required
def cedit(id):
  if request.method=="POST":
        ccode=request.form.get('ccode')
        cname=request.form.get('cname')
        cemail=request.form.get('cemail')
        njobs=request.form.get('no_jobs')
        title=request.form.get('job_title')
        skills=request.form.get('skills_required')
        ccode=ccode.upper()
        db.engine.execute(f"UPDATE `companydata` SET `ccode`='{ccode}' ,`cname`='{cname} ' ,`cemail`='{cemail} ',`no_jobs`='{njobs} ' ,`job_title`='{title} ' ,`skills_required`='{skills} ' WHERE `companydata`.`id`={id}  ")
        flash("Slot Updated","info")
        return redirect("/addcompanyinfo")

  posts=companydata.query.filter_by(id=id).first()
  return render_template("cedit.html",posts=posts)

@app.route("/cdelete/<string:id>",methods=['POST','GET'])
@login_required
def cdelete(id):
    db.engine.execute(f"DELETE FROM `companydata` WHERE `companydata`.`id` = {id} ")
    flash("Data Deleted","danger")
    return redirect("/addcompanyinfo")

@app.route("/adetails",methods=['GET'])
@login_required
def adetails():
    code=current_user.username
    print(code)
    data=applyingjob.query.filter_by(username=code).first()
   
    return render_template("/details.html",data=data)
    

@app.route("/jobapplication",methods=['POST','GET'])
@login_required
def jobapplication():
    query=db.engine.execute(f"SELECT * FROM `companydata` ")
    if request.method=="POST":
        username=request.form.get('username')
        ccode=request.form.get('ccode')
        jobtype=request.form.get('jobtype')
        sname=request.form.get('studentname')
        saddress=request.form.get('studentaddress')
        usn=request.form.get('usn')
        cgpa=request.form.get('cgpa')
        check2=companydata.query.filter_by(ccode=ccode).first()
        if not check2:
            flash("company code not exists","warning")
            
        code=ccode
        dbb=db.engine.execute(f"SELECT * FROM `companydata` WHERE `companydata`.`ccode`='{code}' ")
        for d in dbb:
          seat=d.no_jobs
          print(seat)
          ar=companydata.query.filter_by(ccode=code).first()
          ar.no_jobs=seat-1
          db.session.commit()

        check=companydata.query.filter_by(ccode=ccode).first()
        if(seat>0 and check):
            res=applyingjob(username=username,ccode=ccode,jobtype=jobtype,studentname=sname,studentaddress=saddress,usn=usn,cgpa=cgpa)
            db.session.add(res)
            db.session.commit()
            flash("job is applied kindly visit for further procedure ","success")
        else:
            flash("something went wrong","danger")    
    return render_template("/applyingjob.html",query=query)


# testing whether db is connected or not
@app.route("/test")

def test():
    #em=current_user.email
    #print(em)
    try:
      a=Test.query.all()
      print(a)      
      return f'my db is connected {a.name}'
         
    except Exception as e:
        print(e)
        return f'my db is not connected {e}'    




app.run(debug=True)

