- Standard Project
    - https://gitlab.oit.duke.edu/gk122/mini-amazon

- Team Name
    - Temu from Wish

- Team Members
    - Giyoung Kim: Products Guru, Social Guru
    - Graham Hairston: Sellers Guru
    - Jason Ren: Users Guru
    - Orhan Khan: Carts Guru

- Other Help
    - Skeleton Code Provided by COMPSCI 316 Professor and TAs
    - Assistance for frontend aspects of website from ChatGPT

MS4:
Link to Video: https://drive.google.com/file/d/1XDRh5EynVOx-bTJcS281CZ9uI3Y53SPc/view?usp=sharing
Location of code to populate database: db/generated/gen.py

MS3:
Giyoung Kim: Created API endpoints for Products and Social
Graham Hairston: Created API endpoint for Sellers
Orhan Kahn: Created API endpoint for Carts
Jason Ren: Created API endpoint for Users
Collectively, we also worked on the frontend components of the website, such as implementing a working search bar and cart as well as displaying product pages. 

Locations of  API endpoints: 
In models folder: 
Social Guru - reviews.py: get_recent_reviews
Sellers Guru - inventory.py: get_inventory
Products Guru - product.py: get_k_expensive
Carts Guru - purchase.py: get_cart
Users Guru - purchase.py: get_all_by_uid_since
Controllers inventories.py, carts.py, index.py, and products.py are most relevant here. Also look at base.html, cart.html, index.html, and stock.html for frontend implementations. 

Link to Video: https://drive.google.com/file/d/10qttq_tC0Od3xSVu-WuC7ITFsRGutIJN/view?usp=sharing


Other files we modified: 
models folder: 
user.py: modified register function to have a way to indicate whether one is a seller when registering
product.py: included functions to enable functionality for search bar and product pages
categories.py: indicate the category of products (work in progress)
templates folder: 
Most html files: For improving aesthetics of website and implementation of product pages, search bar, product cards, etc. 
db folder: 
For creation of relations, we modified create.sql
Used synthetic data to test relation constraints and code. Created csv files in the data folder, then modified load.sql accordingly

Current Relations:
Relations for Entities: Users, Sellers, Products, Tags, Categories, Purchases, Reviews (ProductReviews, SellerReviews)
Relations for Relationships: CreatedProduct, IsTagged, SoldBy, CategoryOf, Inventory