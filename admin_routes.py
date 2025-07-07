from flask import Flask, render_template, request, redirect
from vault import User, Product, Category, update ,Cart, agent, Order_Detail, Order_Items,func
from werkzeug.utils import secure_filename
from application import app


import os
from authentication import *

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'webp'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def image(filename):
        file = filename
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if filename:
            image = '/static/products' + filename
        return filename    



admin = agent.query(User).filter(User.admin == 1).first()



@app.route('/admin/manage_category/', methods=['POST', 'GET'])
def new_category():
    if 'admin' not in session:
        return render_template('login/login.html')
    else:
        if request.method == 'GET':
            # Fetch all categories and display them on the page
            return render_template('admin/manage_category.html', admin=admin, categories=agent.query(Category).all())
        
        if request.method == 'POST':
        # Get category information from the form data
            name = request.form['name']
            file = request.files['file']
            filename = None
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if filename:
                image = '/static/' + filename

            # Create a new category and add it to the database
            agent.add(Category(name=name, image=filename))
            agent.commit()
            return redirect('/admin/manage_category/')

    
        

@app.route('/admin/manage_category/delete/<int:cid>', methods=['POST', 'GET'])
def category_delete(cid):
    if request.method == 'GET':
        # Delete the category with the given ID from the database
        agent.query(Category).filter(Category.id == cid).delete()
        agent.commit()
        return redirect('/admin/manage_category/')

@app.route('/admin/manage_category/edit/<int:cid>', methods=['POST', 'GET'])
def category_edit(cid):
    if request.method == 'POST':
        # Update the category with the given ID with the new data from the form
        agent.query(Category).filter(Category.id == cid).update({
            Category.name: request.form['name']
            
        })
        agent.commit()
        return redirect('/admin/manage_category/')
    elif request.method == 'GET':
        # Fetch the category with the given ID and display it for editing
        category = agent.query(Category).filter(Category.id == cid).first()
        return render_template('admin/edit_category.html', category=category, categories=agent.query(Category).all())

@app.route('/admin/new_product/', methods=['POST', 'GET'])
def new_product():
    if request.method == 'POST':
        new_product = Product(
            name=request.form['name'],
            category=request.form['category'],
            price=int(request.form['price']),
            quantity=int(request.form['quantity']),
            image=image(request.files['file']),
            category_id= (agent.query(Category).filter(Category.name == request.form['category']).first()).id,
            description=request.form['description'],
            si_unit=request.form['si_unit'],
            best_before=request.form['best_before']
        )
        agent.add(new_product)
        agent.commit()

        return redirect('/admin/new_product/')
    if 'admin' not in session:
        return render_template('login/login.html')
    else:
        categories = agent.query(Category).all()
        return render_template('admin/new_product.html', categories=categories)

@app.route('/admin/product/edit/<int:pid>')
def edit_product(pid):
        category = agent.query(Category).all()
        product = agent.query(Product).filter(Product.id == pid).first()
        return render_template('admin/edit_product.html', product=product, categories=category)

 
@app.route('/admin')   
@app.route('/admin/dashboard/', methods=['POST', 'GET'])
def dashboard():
    if 'admin' not in session:
        return render_template('login/login.html')
    else:
        total_sales = agent.query(Order_Detail).all()
        total_sales = sum([total_sales[i].total for i in range(len(total_sales))])
        total_earnings = round(total_sales*0.25)
        total_user = len(agent.query(User).all())-1
        total_products = len(agent.query(Product).all())
        out_of_stock = len(agent.query(Product).filter(Product.quantity < 1).all())
        category = agent.query(Category).all()
        categoryname = []
        category_product_count = []
        top_products = agent.query(Order_Items.product_name,func.sum(Order_Items.quantity).label('total_quantity')).group_by(Order_Items.product_id).order_by(func.sum(Order_Items.quantity).desc()).limit(10)
        agent.close()
        t_products = [product.product_name for product in top_products]
        t_quantity = [product.total_quantity for product in top_products]
        for i in range(len(category)):
            categoryname.append(category[i].name)
            category_product_count.append(len(agent.query(Product).filter(Product.category == category[i].name).all()))
        
        return render_template('admin/dashboard.html', total_sales=total_sales, total_earnings=total_earnings , total_user=total_user, total_products=total_products, polar_labels=categoryname, polar_values=category_product_count, top_products=t_products, top_quantity=t_quantity, out_of_stock=out_of_stock)

@app.route('/admin/userbase')
def userbase():
    if 'admin' not in session:
        return render_template('login/login.html')
    else:
        users = agent.query(User).all()
        return render_template('admin/userbase.html', users=users)

@app.route('/admin/product_handler')
def admin_category():
    if 'admin' not in session:
        return render_template('login/login.html')
    else:
        product_list = agent.query(Product).all()
        return render_template('admin/product_handler.html', products=product_list)
