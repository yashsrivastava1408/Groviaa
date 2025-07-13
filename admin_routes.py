from flask import Flask, render_template, request, redirect, session, flash, url_for
from werkzeug.utils import secure_filename
from vault import User, Product, Category, update, Cart, agent, Order_Detail, Order_Items, func
from authentication import *
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'products')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        return filename
    return None

admin = agent.query(User).filter(User.admin == 1).first()

@app.route('/admin/manage_category/', methods=['POST', 'GET'])
def new_category():
    if 'admin' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        file = request.files.get('file')
        filename = save_image(file) if file else None
        agent.add(Category(name=name, image=filename))
        agent.commit()
        flash('Category added successfully.')
        return redirect('/admin/manage_category/')
    categories = agent.query(Category).all()
    return render_template('admin/manage_category.html', admin=admin, categories=categories)

@app.route('/admin/manage_category/delete/<int:cid>')
def category_delete(cid):
    if 'admin' not in session:
        return redirect(url_for('login'))
    agent.query(Category).filter(Category.id == cid).delete()
    agent.commit()
    flash('Category deleted successfully.')
    return redirect('/admin/manage_category/')

@app.route('/admin/manage_category/edit/<int:cid>', methods=['POST', 'GET'])
def category_edit(cid):
    if 'admin' not in session:
        return redirect(url_for('login'))
    category = agent.query(Category).filter(Category.id == cid).first()
    if request.method == 'POST':
        category.name = request.form['name']
        file = request.files.get('file')
        if file:
            filename = save_image(file)
            if filename:
                category.image = filename
        agent.commit()
        flash('Category updated successfully.')
        return redirect('/admin/manage_category/')
    categories = agent.query(Category).all()
    return render_template('admin/edit_category.html', category=category, categories=categories)

@app.route('/admin/new_product/', methods=['POST', 'GET'])
def new_product():
    if 'admin' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        category_obj = agent.query(Category).filter(Category.name == request.form['category']).first()
        new_product = Product(
            name=request.form['name'],
            category=request.form['category'],
            price=int(request.form['price']),
            quantity=int(request.form['quantity']),
            image=save_image(request.files.get('file')),
            category_id=category_obj.id if category_obj else None,
            description=request.form['description'],
            si_unit=request.form['si_unit'],
            best_before=request.form['best_before']
        )
        agent.add(new_product)
        agent.commit()
        flash('Product added successfully.')
        return redirect('/admin/new_product/')
    categories = agent.query(Category).all()
    return render_template('admin/new_product.html', categories=categories)

@app.route('/admin/product/edit/<int:pid>', methods=['POST', 'GET'])
def edit_product(pid):
    if 'admin' not in session:
        return redirect(url_for('login'))
    product = agent.query(Product).filter(Product.id == pid).first()
    categories = agent.query(Category).all()
    if request.method == 'POST':
        product.name = request.form['name']
        product.category = request.form['category']
        product.price = int(request.form['price'])
        product.quantity = int(request.form['quantity'])
        product.description = request.form['description']
        product.si_unit = request.form['si_unit']
        product.best_before = request.form['best_before']
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = save_image(file)
            if filename:
                product.image = filename
        agent.commit()
        flash('Product updated successfully.')
        return redirect('/admin/product_handler')
    return render_template('admin/edit_product.html', product=product, categories=categories)

@app.route('/admin')
@app.route('/admin/dashboard/')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    total_sales = sum([order.total for order in agent.query(Order_Detail).all()])
    total_earnings = round(total_sales * 0.25)
    total_user = len(agent.query(User).all()) - 1
    total_products = len(agent.query(Product).all())
    out_of_stock = len(agent.query(Product).filter(Product.quantity < 1).all())
    category = agent.query(Category).all()
    categoryname = [cat.name for cat in category]
    category_product_count = [len(agent.query(Product).filter(Product.category == cat.name).all()) for cat in category]
    top_products_query = agent.query(Order_Items.product_name, func.sum(Order_Items.quantity).label('total_quantity')).group_by(Order_Items.product_id).order_by(func.sum(Order_Items.quantity).desc()).limit(10)
    top_products = [item.product_name for item in top_products_query]
    top_quantity = [item.total_quantity for item in top_products_query]
    return render_template('admin/dashboard.html', total_sales=total_sales, total_earnings=total_earnings, total_user=total_user, total_products=total_products, polar_labels=categoryname, polar_values=category_product_count, top_products=top_products, top_quantity=top_quantity, out_of_stock=out_of_stock)

@app.route('/admin/userbase')
def userbase():
    if 'admin' not in session:
        return redirect(url_for('login'))
    users = agent.query(User).all()
    return render_template('admin/userbase.html', users=users)

@app.route('/admin/product_handler')
def admin_product_handler():
    if 'admin' not in session:
        return redirect(url_for('login'))
    product_list = agent.query(Product).all()
    return render_template('admin/product_handler.html', products=product_list)

if __name__ == '__main__':
    app.run(debug=True)