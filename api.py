from flask_restful import Resource
from flask import request, jsonify
from vault import agent, Product, Category, User
import vault
import json


class CategoryAPI(Resource):
    def get(self, category_id=None):
        if category_id:
            category = agent.query(Category).filter(Category.id == category_id).first()
            if category:
                return {
                    "name": category.name,
                    "image": "http://127.0.0.1:5000/static/assets/categories/"
                    + category.image,
                }, 200
            else:
                return {"message": "Category not found"}, 404
        else:
            category = agent.query(Category).all()
            if category:
                result = {}
                for cat in category:
                    result[cat.id] = {
                        "name": cat.name,
                        "image": "http://127.0.0.1:5000/static/assets/"
                        + cat.image,
                    }

                return result

    def post(self):
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        image = "/static/temp.jpg"
        admin = (
            agent.query(User)
            .filter(User.email == email)
            .filter(User.password == password)
            .first()
        )
        if admin and admin.admin == 1:
            add_category = Category(name=name, image=image)
            agent.add(add_category)
            agent.commit()
            return {"message": "Category created successfully"}, 201
        else:
            return {"message": "Admin not found"}, 404

    def put(self, category_id):
        category = agent.query(Category).filter(Category.id == category_id).first()
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        admin = (
            agent.query(User)
            .filter(User.email == email)
            .filter(User.password == password)
            .first()
        )
        if admin and admin.admin == 1:
            if category:
                category.name = name
                agent.commit()
                return {"message": "Category name changed"}, 201
            else:
                return {"message": "Category not found"}, 404
        else:
            return {"message": "Not authorized"}

    def delete(self, category_id):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        admin = (
            agent.query(User)
            .filter(User.email == email)
            .filter(User.password == password)
            .first()
        )
        if admin and admin.admin == 1:
            try:
                agent.query(Category).filter(Category.id == category_id).delete()
                agent.flush()
                agent.commit()
                return {"message": "Category deleted"}, 201
            except:
                return {"message": "Category not found"}, 404
        else:
            return {"message": "Not authorized"}


class ProductAPI(Resource):
    def get(self, product_id=None):
        agent.flush()
        if product_id:
            product = agent.query(Product).filter(Product.id == product_id).first()

            if product:
                return {
                    "name": product.name,
                    "image": "http://127.0.0.1:5000/static/assets/"
                    + product.image,
                    "quantity": product.quantity,
                    "price": product.price,
                    "cat": product.category,
                }, 200
            else:
                return {"message": "product not found"}, 404
        else:
            product = agent.query(Product).all()
            if product:
                result = dict()
                for pro in product:
                    result[pro.id] = {
                        "name": pro.name,
                        "image": "http://127.0.0.1:5000/static/assets/"
                        + pro.image,
                        "quantity": pro.quantity,
                        "price": pro.price,
                        "cat": pro.category,
                    }
                return result

    def post(self):
        agent.flush()
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        image = "/static/temp.jpg"
        quantity = data.get("quantity")
        price = data.get("price")
        category = data.get("category")
        category_id = data.get("category_id")
        description = data.get("description")
        si_unit = data.get("si_unit")   
        admin = (
            agent.query(User)
            .filter(User.email == email)
            .filter(User.password == password)
            .first()
        )
        if admin and admin.admin == 1:
            add_product = Product(
                name=name, image=image, quantity=quantity, price=price, category=category, category_id=category_id, description=description, si_unit=si_unit
            )
            agent.add(add_product)
            agent.commit()
            return {"message": "product created successfully"}, 201
        else:
            return {"message": "Admin not found"}, 404

    def put(self, product_id):
        agent.flush()
        product = agent.query(Product).filter(Product.id == product_id).first()
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        image = data.get("image")
        quantity = data.get("quantity")
        price = data.get("price")
        category = data.get("category")
        category_id = data.get("category_id")
        description = data.get("description")
        si_unit = data.get("si_unit")
        admin = (
            agent.query(User)
            .filter(User.email == email)
            .filter(User.password == password)
            .first()
        )
        if admin and admin.admin == 1:
            if product:
                product.name = name
                product.image = image
                product.quantity = quantity
                product.price = price
                product.category = category
                product.category_id = category_id
                product.description = description
                product.si_unit = si_unit
                
                agent.commit()
                return {"message": "Product Updated Successfully!!"}, 201
            else:
                return {"message": "product not found"}, 404
        else:
            return {"message": "Not authorized, invalid credentials provided!!!"}

    def delete(self, product_id):
        agent.flush()
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        admin = (
            agent.query(User)
            .filter(User.email == email)
            .filter(User.password == password)
            .first()
        )
        if admin and admin.admin == 1:
            try:
                agent.query(Product).filter(Product.id == product_id).delete()
                agent.commit()
                return {"message": "Product deleted successfully!"}, 201
            except Exception as e:
                return {"message": f"product not found,{e}"}, 404
            
        else:
            return {"message": "Not authorized, invalid credentials provided!!!"}
