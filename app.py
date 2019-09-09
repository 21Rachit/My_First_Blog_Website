from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug import secure_filename
from flask_mail import Mail
import json
import os
app=Flask(__name__)

local_server=True
with open("first.json","r") as c:
    params=json.load(c)['params']
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER']=r'C:\Users\RACHIT\Desktop\chain'
app.secret_key='super-secret-key'
app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT='465',
        MAIL_USE_SSL=True,
        MAIL_USERNAME=params['username'],
        MAIL_PASSWORD=params['pass']
        
        )
mail=Mail(app)
db = SQLAlchemy(app)


class Contact(db.Model):
    serial = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(120), unique=True)
    message = db.Column(db.String(120), unique=True)
    date = db.Column(db.String(120), unique=True, nullable=True)
 
class Login(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True,nullable=True)
    password = db.Column(db.String(120), unique=True)
    
class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True)
    slug = db.Column(db.String(120), unique=True)
    content = db.Column(db.String(120), unique=True)
    img_file=db.Column(db.String(120), unique=True)
    date = db.Column(db.String(120), unique=True, nullable=True)
    
    
@app.route("/",methods=['GET','POST'])
def index():
    if(request.method=='POST'):
        email=request.form.get('email1');
        pass1=request.form.get('pass1');
        
        if(email==params['username'] and pass1==params['pass']):
            posts=Posts.query.all()
            session['user']=email
            return render_template("admin.html",params=params,posts=posts)
        else:
            return render_template("homepage.html",params=params)


            
    
    return render_template("homepage.html",params=params)

@app.route("/home")
def home():
    posts=Posts.query.filter_by().all()
    return render_template("index.html",params=params,posts=posts)

@app.route("/delete/<string:sno>", methods=['GET','POST'])
def delete(sno):
    if('user' in session and session['user']==params['username']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/home')
        
    


@app.route("/edit/<string:sno>", methods=['GET','POST'])
def edit(sno):
    if(request.method=='POST'):
        title=request.form.get('title');
        slug=request.form.get('slug');
        content=request.form.get('content');
        img_file=request.form.get('img');
        date=datetime.now();
        if(sno=='0'):
            entry=Posts(sno=sno,title=title,slug=slug,content=content,img_file=img_file,date=date)# we are putting sno of this new post =0 which is not possible since it is auto increement
            db.session.add(entry)
            db.session.commit()
        else:
            post=Posts.query.filter_by(sno=sno).first()
            post.title=request.form.get('title');
            post.slug=request.form.get('slug');
            post.content=request.form.get('content');
            post.img_file=request.form.get('img');
            post.date=datetime.now();
            db.session.commit()
            return redirect('/admin')

            
    post=Posts.query.filter_by(sno=sno).first()      # but surprisingly it was able to find post with sno=0 in our post
    return render_template("edit.html", params=params,post=post,sno=sno)

@app.route("/about")
def about():
    return render_template("about.html", params=params)

 

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/')

@app.route("/uploader", methods=['GET','POST'])
def uploader():
    if('user' in session and session['user']==params['username']):
        if(request.method=="POST"):
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Upload Successfully Done"

@app.route("/admin",methods=['GET','POST'])
def dashboard():
    posts=Posts.query.all()
    return render_template("admin.html",params=params,posts=posts)

@app.route("/layout")
def layout():
    return render_template("layout.html", params=params)

@app.route("/post")
def post12():
    return render_template("post.html",params=params)

@app.route("/post/<string:post_slug>",methods=['GET'])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template("post1.html",params=params,post=post)

@app.route("/contact",methods=['GET','POST'])
def contact():
    if(request.method=='POST'):
        name=request.form.get('name1')
        email=request.form.get('email1')
        phone=request.form.get('phone1')
        message=request.form.get('message1')
        
        entry=Contact(name=name,email=email,phone=phone,message=message,date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        
        mail.send_message('New message from'+name,
                          sender=email,
                          recipients=[params['username']],
                          body=message+"\n"+phone
                          )
        
    return render_template("contact.html", params=params)

@app.route("/bam")
def again():
    return "hello shreya how are you "
if __name__ == '__main__':
    app.run(port = 3000,debug=True)
