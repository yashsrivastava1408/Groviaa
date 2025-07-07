# API Documentation

Welcome to the API documentation for your project. This guide provides details about available endpoints, their functionalities, parameters, and responses.

## Categories

### Get List of Categories

- **Endpoint:** `/categories`
- **Method:** `GET`
- **Summary:** Retrieve a list of all categories.
- **Responses:**
  - `200 OK`: Successful response

### Create a New Category

- **Endpoint:** `/categories`
- **Method:** `POST`
- **Summary:** Create a new category.
- **Parameters:**
  - `category` (body): Category data to be created
- **Responses:**
  - `201 Created`: Category created successfully
  - `404 Not Found`: Admin not found or unauthorized

<!-- ... Repeat the pattern for other category-related endpoints ... -->

## Products

### Get List of Products

- **Endpoint:** `/products`
- **Method:** `GET`
- **Summary:** Fetch a list of all products.
- **Responses:**
  - `200 OK`: Successful response

### Create a New Product

- **Endpoint:** `/products`
- **Method:** `POST`
- **Summary:** Add a new product.
- **Parameters:**
  - `product` (body): Product data to be created
- **Responses:**
  - `201 Created`: Product created successfully
  - `404 Not Found`: Admin not found or unauthorized

<!-- ... Repeat the pattern for other product-related endpoints ... -->

## Definitions

### CategoryInput

- **Type:** Object
- **Properties:**
  - `name` (string): Name of the category
  - `email` (string): Admin's email
  - `password` (string): Admin's password

<!-- ... Repeat the pattern for other definitions ... -->

## Sample Requests

```http
GET /categories

```

## Sample Response
```json
{
  "1": {
  "name": "Fruit",
  "image": "http://127.0.0.1:5000/static/assets/categories/fruit.jpg"
  },
  "2": {
  "name": "Vegetable",
  "image": "http://127.0.0.1:5000/static/assets/categories/vegetable.jpg"
  },
}
```
