from flask import Flask, render_template, request, redirect, session, jsonify, flash
from application import app
from vault import agent, User, Product, Category, update, Cart, Order_Detail, Order_Items
from authentication import *
from functools import wraps

import difflib


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
@app.route('/ordered_products/<int:oid>')
@login_required
def ordered_products(oid):
    products = agent.query(Order_Items).filter(Order_Items.order_id == oid).all()
    order = agent.query(Order_Detail).filter(Order_Detail.id == oid).first()
    return render_template('user/ordered_products.html', items=products, order=order, user_id=session['user'], cart_items=order)

# ---------- Search ----------
@app.route('/search', methods=['POST', 'GET'])
@app.route('/search/<string:search_value>', methods=['GET'])
@login_required
def search(search_value=None):
    if request.method == 'POST':
        search_value = request.form['search']

    if not search_value:
        return redirect('/home')

    user = agent.query(User).filter(User.id == session['user']).first()
    categories = agent.query(Category).filter(Category.name.ilike(f"%{search_value}%")).all()
    products = agent.query(Product).filter(Product.name.ilike(f"%{search_value}%")).all()

    return render_template('user/search.html', user=user, categories=categories, products=products, sv=search_value)

# ---------- AI Assistant (Enhanced with Comprehensive Commands) ----------
@app.route('/ai-assistant', methods=['POST'])
@login_required
def ai_assistant():
    message = request.json.get('message', '').lower()
    action = None
    user = agent.query(User).filter(User.id == session['user']).first()
    name = user.name if user else "there"
    
    # Default fallback response
    reply = f"Hi {name}, I'm here to assist you. You can ask about products, offers, cart, or say 'help' for more options."
    
    # === FRUITS ===
    if any(word in message for word in ["apple", "apples"]):
        apple = agent.query(Product).filter(Product.name.ilike('%apple%')).first()
        if apple:
            reply = f"Yes {name}, we have fresh apples available at ₹{apple.price} per kg. Redirecting you to the product page now."
            action = f"/product/{apple.id}"
        else:
            reply = f"Sorry {name}, apples are currently out of stock. Would you like to explore other fruits?"
    
    elif any(word in message for word in ["banana", "bananas"]):
        banana = agent.query(Product).filter(Product.name.ilike('%banana%')).first()
        if banana:
            reply = f"Fresh bananas are available at ₹{banana.price} per dozen, {name}. Taking you there now!"
            action = f"/product/{banana.id}"
        else:
            reply = f"Bananas are out of stock, {name}. How about some other tropical fruits?"
    
    elif any(word in message for word in ["orange", "oranges"]):
        orange = agent.query(Product).filter(Product.name.ilike('%orange%')).first()
        if orange:
            reply = f"Juicy oranges at ₹{orange.price} per kg, {name}. Perfect for fresh juice!"
            action = f"/product/{orange.id}"
        else:
            reply = f"Oranges are temporarily unavailable, {name}. Try our citrus alternatives!"
    
    elif any(word in message for word in ["mango", "mangoes"]):
        mango = agent.query(Product).filter(Product.name.ilike('%mango%')).first()
        if mango:
            reply = f"Sweet mangoes are in season at ₹{mango.price} per kg, {name}!"
            action = f"/product/{mango.id}"
        else:
            reply = f"Mangoes are out of season, {name}. Check back during summer!"
    
    elif any(word in message for word in ["grapes", "grape"]):
        grape = agent.query(Product).filter(Product.name.ilike('%grape%')).first()
        if grape:
            reply = f"Fresh grapes available at ₹{grape.price} per kg, {name}. Perfect for snacking!"
            action = f"/product/{grape.id}"
        else:
            reply = f"Grapes are currently unavailable, {name}. Try our berry selection!"
    
    elif any(word in message for word in ["fruit", "fruits"]):
        reply = f"We have a wonderful selection of fresh fruits, {name}! Let me show you what's available."
        action = "/category/fruits"
    
    # === VEGETABLES ===
    elif any(word in message for word in ["tomato", "tomatoes"]):
        tomato = agent.query(Product).filter(Product.name.ilike('%tomato%')).first()
        if tomato:
            reply = f"Fresh tomatoes at ₹{tomato.price} per kg, {name}. Essential for cooking!"
            action = f"/product/{tomato.id}"
        else:
            reply = f"Tomatoes are out of stock, {name}. How about some other cooking essentials?"
    
    elif any(word in message for word in ["onion", "onions"]):
        onion = agent.query(Product).filter(Product.name.ilike('%onion%')).first()
        if onion:
            reply = f"Quality onions available at ₹{onion.price} per kg, {name}. A kitchen staple!"
            action = f"/product/{onion.id}"
        else:
            reply = f"Onions are temporarily out of stock, {name}. Check our other vegetables!"
    
    elif any(word in message for word in ["potato", "potatoes"]):
        potato = agent.query(Product).filter(Product.name.ilike('%potato%')).first()
        if potato:
            reply = f"Fresh potatoes at ₹{potato.price} per kg, {name}. Perfect for any meal!"
            action = f"/product/{potato.id}"
        else:
            reply = f"Potatoes are currently unavailable, {name}. Try our root vegetable alternatives!"
    
    elif any(word in message for word in ["carrot", "carrots"]):
        carrot = agent.query(Product).filter(Product.name.ilike('%carrot%')).first()
        if carrot:
            reply = f"Crunchy carrots at ₹{carrot.price} per kg, {name}. Great for health!"
            action = f"/product/{carrot.id}"
        else:
            reply = f"Carrots are out of stock, {name}. How about some other colorful vegetables?"
    
    elif any(word in message for word in ["vegetable", "vegetables", "veggies", "greens"]):
        reply = f"Looking for fresh vegetables? You're at the right place, {name}. Let me show you what's available."
        action = "/category/vegetables"
    
    # === DAIRY PRODUCTS ===
    elif any(word in message for word in ["milk", "dairy"]):
        milk = agent.query(Product).filter(Product.name.ilike('%milk%')).first()
        if milk:
            reply = f"Fresh milk available at ₹{milk.price} per liter, {name}. Daily essential!"
            action = f"/product/{milk.id}"
        else:
            reply = f"Milk is out of stock, {name}. Check our dairy alternatives!"
    
    elif any(word in message for word in ["cheese", "paneer"]):
        cheese = agent.query(Product).filter(Product.name.ilike('%cheese%')).first()
        if cheese:
            reply = f"Fresh cheese/paneer at ₹{cheese.price}, {name}. Perfect for cooking!"
            action = f"/product/{cheese.id}"
        else:
            reply = f"Cheese/paneer is unavailable, {name}. Try our other dairy products!"
    
    elif any(word in message for word in ["yogurt", "curd", "dahi"]):
        yogurt = agent.query(Product).filter(Product.name.ilike('%yogurt%')).first()
        if yogurt:
            reply = f"Fresh yogurt/curd at ₹{yogurt.price}, {name}. Great for digestion!"
            action = f"/product/{yogurt.id}"
        else:
            reply = f"Yogurt/curd is out of stock, {name}. Check our dairy section!"
    
    # === GRAINS & CEREALS ===
    elif any(word in message for word in ["rice", "basmati"]):
        rice = agent.query(Product).filter(Product.name.ilike('%rice%')).first()
        if rice:
            reply = f"Premium rice available at ₹{rice.price} per kg, {name}. Staple food!"
            action = f"/product/{rice.id}"
        else:
            reply = f"Rice is out of stock, {name}. Try our grain alternatives!"
    
    elif any(word in message for word in ["wheat", "atta", "flour"]):
        wheat = agent.query(Product).filter(Product.name.ilike('%wheat%')).first()
        if wheat:
            reply = f"Fresh wheat flour/atta at ₹{wheat.price} per kg, {name}. Essential for bread!"
            action = f"/product/{wheat.id}"
        else:
            reply = f"Wheat flour is unavailable, {name}. Check our grain section!"
    
    elif any(word in message for word in ["grain", "grains", "cereal", "cereals"]):
        reply = f"We have a variety of grains and cereals, {name}. Let me show you our selection."
        action = "/category/grains"
    
    # === SPICES & SEASONINGS ===
    elif any(word in message for word in ["spice", "spices", "masala"]):
        reply = f"We have an extensive spice collection, {name}. Perfect for authentic cooking!"
        action = "/category/spices"
    
    elif any(word in message for word in ["salt", "pepper"]):
        salt = agent.query(Product).filter(Product.name.ilike('%salt%')).first()
        if salt:
            reply = f"Basic seasonings like salt available at ₹{salt.price}, {name}. Kitchen essentials!"
            action = f"/product/{salt.id}"
        else:
            reply = f"Basic seasonings are available, {name}. Check our spice section!"
    
    # === BEVERAGES ===
    elif any(word in message for word in ["tea", "coffee", "beverage"]):
        tea = agent.query(Product).filter(Product.name.ilike('%tea%')).first()
        if tea:
            reply = f"Premium tea/coffee at ₹{tea.price}, {name}. Perfect for your daily brew!"
            action = f"/product/{tea.id}"
        else:
            reply = f"Tea/coffee selection available, {name}. Check our beverage section!"
    
    elif any(word in message for word in ["juice", "drink"]):
        reply = f"Fresh juices and drinks available, {name}. Stay hydrated!"
        action = "/category/beverages"
    
    # === SNACKS & PACKAGED FOODS ===
    elif any(word in message for word in ["snack", "snacks", "chips"]):
        reply = f"Variety of snacks and chips available, {name}. Perfect for munching!"
        action = "/category/snacks"
    
    elif any(word in message for word in ["biscuit", "biscuits", "cookies"]):
        biscuit = agent.query(Product).filter(Product.name.ilike('%biscuit%')).first()
        if biscuit:
            reply = f"Delicious biscuits at ₹{biscuit.price}, {name}. Great with tea!"
            action = f"/product/{biscuit.id}"
        else:
            reply = f"Biscuits and cookies available, {name}. Check our snack section!"
    
    # === PERSONAL CARE ===
    elif any(word in message for word in ["soap", "shampoo", "personal care"]):
        reply = f"Personal care products available, {name}. Take care of yourself!"
        action = "/category/personal-care"
    
    # === HOUSEHOLD ITEMS ===
    elif any(word in message for word in ["detergent", "cleaning", "household"]):
        reply = f"Household cleaning products available, {name}. Keep your home sparkling!"
        action = "/category/household"
    
    # === SHOPPING ACTIONS ===
    elif any(word in message for word in ["buy", "purchase", "shop"]):
        reply = f"Great! Let me take you to our product categories where you can explore and buy items you like, {name}."
        action = "/category"
    
    elif any(word in message for word in ["cart", "basket", "bag"]):
        reply = f"Sure {name}, opening your cart so you can review your items or proceed to checkout."
        action = f"/cart/{session['user']}"
    
    elif any(word in message for word in ["checkout", "pay", "payment"]):
        reply = f"Ready to checkout, {name}? Let me take you to complete your purchase."
        action = "/checkout"
    
    elif any(word in message for word in ["wishlist", "favorites", "saved"]):
        reply = f"Here are your saved items, {name}. Ready to add them to cart?"
        action = "/wishlist"
    
    # === OFFERS & DISCOUNTS ===
    elif any(word in message for word in ["offer", "offers", "discount", "deal", "deals", "sale"]):
        reply = f"You're in luck, {name}! Today we're offering 10% off on all green vegetables and 15% off on dairy products. Check them out now!"
        action = "/offers"
    
    elif any(word in message for word in ["coupon", "promo", "code"]):
        reply = f"Use code FRESH10 for 10% off on fruits and vegetables, {name}!"
    
    # === SEARCH & BROWSE ===
    elif any(word in message for word in ["search", "find", "look for"]):
        reply = f"What are you looking for, {name}? You can search for any product or browse categories."
        action = "/search"
    
    elif any(word in message for word in ["category", "categories", "section"]):
        reply = f"Here are all our product categories, {name}. What interests you today?"
        action = "/category"
    
    elif any(word in message for word in ["fresh", "organic", "quality"]):
        reply = f"We pride ourselves on fresh, quality products, {name}. Check our premium organic section!"
        action = "/category/organic"
    
    # === ACCOUNT & ORDERS ===
    elif any(word in message for word in ["order", "orders", "history"]):
        reply = f"Here's your order history, {name}. Want to reorder something?"
        action = "/orders"
    
    elif any(word in message for word in ["account", "profile", "settings"]):
        reply = f"Manage your account settings here, {name}."
        action = "/account"
    
    elif any(word in message for word in ["address", "delivery", "shipping"]):
        reply = f"Manage your delivery addresses here, {name}. We deliver fresh groceries to your doorstep!"
        action = "/address"
    
    # === HELP & SUPPORT ===
    elif any(word in message for word in ["help", "assist", "support"]):
        reply = f"""I'm your shopping assistant, {name}! Here's what I can help you with:
        
        🛒 Products: Ask about fruits, vegetables, dairy, grains, spices, snacks
        💰 Offers: Ask about deals, discounts, coupons
        🛍️ Shopping: Cart, checkout, wishlist, orders
        📱 Account: Profile, addresses, settings
        🔍 Browse: Categories, search, recommendations
        
        Just tell me what you need!"""
    
    elif any(word in message for word in ["contact", "phone", "email"]):
        reply = f"Need to contact us, {name}? Call us at 1800-GROCERY or email support@grocery.com"
    
    # === RECOMMENDATIONS ===
    elif any(word in message for word in ["recommend", "suggestion", "popular", "bestseller"]):
        reply = f"Here are today's popular items, {name}: Fresh apples, organic vegetables, premium rice, and dairy combo packs!"
        action = "/recommendations"
    
    elif any(word in message for word in ["new", "latest", "arrivals"]):
        reply = f"Check out our latest arrivals, {name}! Fresh seasonal produce just came in."
        action = "/new-arrivals"
    
    # === QUANTITY & PRICING ===
    elif any(word in message for word in ["price", "cost", "rate", "how much"]):
        reply = f"Prices vary by product, {name}. Browse categories to see current rates, or ask about specific items!"
        action = "/category"
    
    elif any(word in message for word in ["kg", "liter", "dozen", "pack"]):
        reply = f"We sell items in various quantities, {name}. Check product pages for available sizes and bulk discounts!"
    
    # === GREETINGS ===
    elif any(word in message for word in ["hello", "hi", "hey", "good morning", "good evening"]):
        reply = f"Hello {name}! Welcome to our grocery store. How can I help you shop today?"
    
    elif any(word in message for word in ["thank", "thanks"]):
        reply = f"You're welcome, {name}! Happy to help you with your grocery shopping."
    
    elif any(word in message for word in ["bye", "goodbye", "see you"]):
        reply = f"Goodbye {name}! Come back soon for fresh groceries and great deals!"
    
    # === SPECIAL COMMANDS ===
    elif any(word in message for word in ["today", "daily", "fresh today"]):
        reply = f"Today's fresh arrivals, {name}: Seasonal fruits, farm-fresh vegetables, and daily dairy products!"
        action = "/daily-fresh"
    
    elif any(word in message for word in ["combo", "bundle", "package"]):
        reply = f"Great value combo packs available, {name}! Save more with our bundled offers."
        action = "/combos"
    
    elif any(word in message for word in ["bulk", "wholesale", "quantity"]):
        reply = f"Need bulk quantities, {name}? We offer wholesale prices for large orders!"
        action = "/bulk-orders"
            # === SPECIAL COMMANDS ===
    elif any(word in message for word in ["combo", "bundle", "package"]):
        reply = f"Great value combo packs available, {name}! Save more with our bundled offers."
        action = "/combos"

    # === FINAL FALLBACK: Dynamic Product Matching ===
    if not action:
        product_match = agent.query(Product).filter(Product.name.ilike(f"%{message}%")).first()
        if product_match:
            reply = f"Yes {name}, we have {product_match.name} available at ₹{product_match.price}. Redirecting you to the product page now."
            action = f"/product/{product_match.id}"

    return jsonify({'reply': reply, 'action': action})

    
    return jsonify({'reply': reply, 'action': action})