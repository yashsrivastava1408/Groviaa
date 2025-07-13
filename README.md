Grovia
Demo Video :movie_camera: 
Grovia is an e-commerce platform focused on environmentally friendly and sustainable products. This platform aims to connect consumers with products that have a positive impact on the environment.
Application Snapshots
<div class="carousel">
    <details> <summary>Admin's Dashboard</summary>
  <img src="https://raw.githubusercontent.com/namansehwal/Grovia/main/static/admin_page.png" alt="Image 1" width='80%'>
            </details>
 <details> <summary>Homepage</summary> <img src="https://raw.githubusercontent.com/namansehwal/Grovia/main/static/user.png" alt="Image 2"  width='80%'>   </details>
  <details><summary>Product Card</summary> <img src="https://raw.githubusercontent.com/namansehwal/Grovia/main/static/product.png" alt="Image 3"  width='80%'>   </details>
</div>
Table of Contents

Introduction
Features
Installation
Usage
Contributing
License

Introduction
Grovia is built with the goal of promoting eco-friendly products and practices. It provides a user-friendly interface for users to explore, search, and purchase products that align with sustainability values. Whether you're a conscious consumer or a seller of sustainable products, Grovia provides a platform to connect and contribute to a greener future.
Features

Product Listings: Browse through a wide range of sustainable products.
Search and Filters: Easily find products using search and filtering options.
User Accounts: Create and manage your account for a personalized experience.
Shopping Cart: Add and remove products from your cart before making a purchase.
Seller Dashboard: For sellers to manage their products and inventory.
Order History: Track your order history and delivery status.
AI Assistant: Intelligent shopping assistant to help find products and answer questions.

API Documentation
:rocket: Quick Start
Run the site locally
Installation
To set up Grovia locally, follow these steps:

Clone the repository:
bashgit clone https://github.com/namansehwal/Grovia.git
cd Grovia

Create a virtual environment:
bashpython3 -m venv venv

Activate the virtual environment:

On macOS and Linux:
bashsource venv/bin/activate

On Windows:
bashvenv\Scripts\activate



Install the required packages:
bashpip install -r requirements.txt

To run flask server:
bashpython application.py


:open_file_folder: What's inside?
A quick look at the folder structure of this project.
.
Grovia/
┣ static/
┃ ┣ assets/
┃ ┣ styles/
┣ templates/
┃ ┣ admin/
┃ ┣ login/
┃ ┗ user/
┣ admin_routes.py
┣ api.py
┣ api_methods.yaml
┣ application.py
┣ authentication.py
┣ database.sqlite3
┣ README.md
┣ requirements.txt
┣ user_routes.py
┗ vault.py
Contributing 🧑‍🤝‍🧑
If you'd like to contribute to the project, here are the steps:

Fork the Project.
Create your Feature Branch: git checkout -b feature/YourFeature
Commit your Changes: git commit -m 'Add some amazing feature'
Push to the Branch: git push origin feature/YourFeature
Open a Pull Request.

License 🏛️
This project is licensed under the MIT License.
Contact 🤙
Connect with the project creator for any questions or feedback:

Name: Naman Sehwal
Email: namansehwal@gmail.com
GitHub: @namansehwal
LinkedIn: Naman Sehwal

Feel free to explore the code and contribute to make this app even better! 😊