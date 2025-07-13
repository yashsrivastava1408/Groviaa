from flask import Flask, render_template, request, redirect, session, jsonify, flash
from application import app
from vault import agent, User, Product, Category, update, Cart, Order_Detail, Order_Items
from authentication import *
from functools import wraps
import difflib
import re

# ---------- Decorator for Login Required ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return render_template('login/login.html')
        return f(*args, **kwargs)
    return decorated_function

# ---------- Home ----------
@app.route('/')
@app.route('/home')
@login_required
def home():
    user = agent.query(User).filter(User.id == session['user']).first()
    categories = agent.query(Category).order_by(Category.id.desc()).all()
    products = agent.query(Product).order_by(Product.id.desc()).all()
    recent_products = agent.query(Product).order_by(Product.id.desc()).limit(5).all()
    return render_template('user/index.html', user=user, categories=categories, products=products, recent_products=recent_products)

# ---------- Category Page ----------
@app.route('/category/')
@login_required
def category():
    categories = agent.query(Category).all()
    user = agent.query(User).filter(User.id == session['user']).first()
    return render_template('user/category.html', categories=categories, user=user)

# ---------- Profile Page ----------
@app.route('/profile/<int:pid>')
@login_required
def profile(pid):
    if session['user'] != pid:
        flash("You can only view your own profile.", "danger")
        return redirect('/home')
    user = agent.query(User).filter(User.id == pid).first()
    return render_template('user/profile.html', user=user)

# ---------- View/Add Product ----------
@app.route('/product/<int:pid>', methods=['POST', 'GET'])
@login_required
def product(pid):
    if request.method == 'POST':
        new_cart = Cart(
            user_id=session['user'],
            product_id=request.form['product_id'],
            product_name=request.form['product_name'],
            quantity=int(request.form['quantity']),
            price=int(request.form['price'])
        )
        agent.add(new_cart)
        agent.commit()
        flash('Product added to cart!', 'success')
        return redirect(f'/product/{pid}')
    else:
        item = agent.query(Product).filter(Product.id == pid).first()
        if not item:
            return render_template('404.html')
        return render_template('user/buy.html', product=item)

# ---------- Cart ----------
@app.route('/cart/<int:pid>')
@login_required
def cart(pid):
    if session['user'] != pid:
        flash("You can only view your own cart.", "danger")
        return redirect('/home')
    products = agent.query(Cart).filter(Cart.user_id == pid).all()
    total = sum([p.price * p.quantity for p in products])
    return render_template('user/cart.html', cart_items=products, total=total, user_id=pid)

# ---------- Delete from Cart ----------
@app.route('/cart/del/<int:cid>')
@login_required
def car_delete(cid):
    agent.query(Cart).filter(Cart.cart_id == cid).delete()
    agent.commit()
    flash('Item removed from cart.', 'info')
    return redirect('/cart/' + str(session['user']))

# ---------- Place Order ----------
@app.route('/cart/place_order/<int:pid>', methods=['POST'])
@login_required
def place_order(pid):
    new_order = Order_Detail(user_id=int(request.form['user_id']), total=int(request.form['total']))
    agent.add(new_order)
    agent.commit()

    cart = agent.query(Cart).filter(Cart.user_id == pid).all()
    for item in cart:
        new_order_item = Order_Items(
            user_id=session['user'],
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            amount=item.price,
            product_price=item.price,
            product_name=item.product_name
        )
        product = agent.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.quantity -= item.quantity
        agent.add(new_order_item)
    agent.commit()

    agent.query(Cart).filter(Cart.user_id == pid).delete()
    agent.commit()
    flash('Your order has been placed successfully!', 'success')
    return redirect('/home')

# ---------- View Orders ----------
@app.route('/orders/<int:pid>')
@login_required
def my_orders(pid):
    if session['user'] != pid:
        flash("Unauthorized access to orders.", "danger")
        return redirect('/home')
    orders = agent.query(Order_Detail).filter(Order_Detail.user_id == pid).all()
    return render_template('user/orders.html', orders=orders)

# ---------- Ordered Products ----------
@app.route('/ai-assistant', methods=['POST'])
@login_required
def ai_assistant():
    message = request.json.get('message', '').lower()
    user = agent.query(User).filter(User.id == session['user']).first()
    name = user.name if user else "there"
    reply = f"Hi {name}, how can I assist you?"
    action = None

    selected_product = session.get('selected_product')

    # Step 1: If user already selected a product and now giving quantity

    if selected_product:
    # ✅ Step 1: Convert number words to digits
     word_to_num = {
        "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8",
        "nine": "9", "ten": "10"
    }

    # ✅ Step 2: Replace number words in message (safely using word boundaries)
     for word, digit in word_to_num.items():
        message = re.sub(rf"\b{word}\b", digit, message)

    # ✅ Step 3: Remove extra units like 'can', 'packet', etc.
     message = re.sub(r"(packet|packets|can|cans|kg|kgs|gms|grams|items|units)", "", message)

    # ✅ Step 4: Extract quantity
     match = re.search(r'(\d+)', message)
     if match:
        qty = int(match.group(1))
        product = agent.query(Product).filter(Product.id == selected_product['id']).first()
        if product:
            new_cart = Cart(
                user_id=session['user'],
                product_id=product.id,
                product_name=product.name,
                quantity=qty,
                price=product.price
            )
            agent.add(new_cart)
            agent.commit()
            session.pop('selected_product', None)
            reply = f"Added {qty} x {product.name} to your cart, {name}."
            action = f"/cart/{user.id}"
            return jsonify({'reply': reply, 'action': action})



    # Step 2: Detect product name and redirect
    # Step 2: Detect product name and redirect
    # Step 2: Detect product name and redirect
    all_products = agent.query(Product).all()
    for product in all_products:
        pname = product.name.lower()
        if pname in message or any(word in pname.split() for word in message.split()):
            session['selected_product'] = {
               'id': product.id,
               'name': product.name,
               'price': product.price
            }
            reply = f"Taking you to the {product.name} page. The price is ₹{product.price} per {product.si_unit.lower()}."
            action = f"/product/{product.id}"
            return jsonify({'reply': reply, 'action': action})

@app.route('/ordered_products/<int:oid>')
@login_required
def ordered_products(oid):
    order = agent.query(Order_Detail).filter(Order_Detail.id == oid).first()
    if not order:
        flash("Order not found.", "danger")
        return redirect('/orders/' + str(session['user']))
    if order.user_id != session['user']:
        flash("Unauthorized access to this order.", "danger")
        return redirect('/orders/' + str(session['user']))

    ordered_items = agent.query(Order_Items).filter(Order_Items.order_id == oid).all()
    return render_template('user/ordered_products.html', order=order, ordered_items=ordered_items)





    # Step 3: General commands
    if "cart" in message:
        reply = f"Here is your cart, {name}."
        action = f"/cart/{user.id}"

    elif "orders" in message:
        reply = f"Showing your orders, {name}."
        action = f"/orders/{user.id}"

    elif "profile" in message:
        reply = f"Opening your profile, {name}."
        action = f"/profile/{user.id}"

    elif "logout" in message:
        reply = f"Logging you out, {name}."
        action = "/logout"

    elif "apply coupon" in message or "coupon" in message or "code" in message:
        if "Grovia25" in message:
            reply = "Coupon Grovia25 applied successfully! You got 25% off."
            action = "apply_coupon"
        else:
            reply = "Invalid coupon code."

    elif "place order" in message:
        cart = agent.query(Cart).filter(Cart.user_id == user.id).all()
        if cart:
            total = sum([item.price * item.quantity for item in cart])
            new_order = Order_Detail(user_id=user.id, total=total)
            agent.add(new_order)
            agent.commit()

            for item in cart:
                order_item = Order_Items(
                    user_id=user.id,
                    order_id=new_order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    amount=item.price,
                    product_price=item.price,
                    product_name=item.product_name
                )
                agent.add(order_item)

                product = agent.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    product.quantity -= item.quantity

            agent.commit()
            agent.query(Cart).filter(Cart.user_id == user.id).delete()
            agent.commit()
            reply = "Your order has been placed successfully!"
            action = f"/orders/{user.id}"
        else:
            reply = "Your cart is empty. Please add some items first."

    elif "remove" in message and "item" in message:
        ordinals = {
            "first": 0, "second": 1, "third": 2, "fourth": 3, "fifth": 4,
            "sixth": 5, "seventh": 6, "eighth": 7, "ninth": 8, "tenth": 9
        }
        found = None
        for word, index in ordinals.items():
            if word in message:
                found = index
                break

        cart_items = agent.query(Cart).filter(Cart.user_id == user.id).all()
        if found is not None and found < len(cart_items):
            item_to_remove = cart_items[found]
            agent.delete(item_to_remove)
            agent.commit()
            reply = f"Removed {item_to_remove.product_name} from your cart."
        else:
            reply = "Sorry, I couldn't identify which item to remove."

    elif "set" in message or "change" in message:
        cart_items = agent.query(Cart).filter(Cart.user_id == user.id).all()
        for item in cart_items:
            if item.product_name.lower() in message:
                qmatch = re.search(r'(\d+)', message)
                if qmatch:
                    item.quantity = int(qmatch.group(1))
                    agent.commit()
                    reply = f"Updated {item.product_name} to {item.quantity} in your cart."
                    return jsonify({'reply': reply})
        reply = "Sorry, I couldn't identify which item to update."
    elif "show coupon" in message or "available coupons" in message:
       reply = "Here are some available coupons: Grovia25, SAVE20, FRESH5, GET10."
       action = "show_coupons"


    return jsonify({'reply': reply, 'action': action})
    

@app.route('/recommendations')
@login_required
def recommendations():
    user = agent.query(User).filter(User.id == session['user']).first()
    recommended_products = agent.query(Product).order_by(Product.id.desc()).limit(6).all()
    return render_template('user/recommendations.html', user=user, products=recommended_products)
    