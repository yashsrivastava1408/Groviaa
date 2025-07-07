from flask import Flask, render_template, request, redirect, session, flash
from application import app
from vault import User, agent, Category, Product
import vault

@app.route('/login', methods=['POST'])
def login_post():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        validation = agent.query(User).filter(User.email == email).filter(User.password == password).all()

        if len(validation) == 1:
            session['user'] = validation[0].id
            return redirect('/home')
        flash('Invalid Credentials')
        return render_template('login/login.html', popup=True)
    return redirect('/')

@app.route('/register', methods=['POST', 'GET'])
def signup():
    
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        phone_number = request.form['phone_number']
        
        user = User(username,email,password,address,phone_number)
        agent.add(user)
        agent.commit()
        
        validation = agent.query(User).filter(User.email == email).filter(User.password == password).all()
        session['user'] = validation[0].id
        return redirect('/home')
    elif request.method == 'GET':
        return render_template('login/register.html')    

@app.route('/admin_login', methods=['POST', 'GET'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        validation = agent.query(User).filter(User.email == email).filter(User.password == password).first()
        
        if validation:
            if  validation.admin == 1:
                session['admin'] = validation.id
                print('admin validated')
                return redirect('/admin')
        return render_template('login/admin_login.html', popup=True)
    else:
        return render_template('login/admin_login.html')
         
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('admin', None)
    return redirect('/')

@app.route('/testing')
def testing():
    return render_template('user/index.html', user=agent.query(User).filter(User.id == 2).first(), categories=agent.query(Category).all(), products=agent.query(Product).all())
 

