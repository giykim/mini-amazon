from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random
from datetime import datetime, timedelta

# Configuration for number of entries in each table
NUM_USERS = 100
NUM_PRODUCTS = 2000
NUM_PURCHASES = 2500
NUM_TAGS = 100
NUM_CATEGORIES = 50
NUM_REVIEWS = 500
NUM_SELLER_REVIEWS = 300
NUM_HELPFULNESS = 700

Faker.seed(0)
fake = Faker()

def get_csv_writer(filename):
    return csv.writer(open(filename, 'w'), dialect='unix')

def gen_users(num_users):
    writer = get_csv_writer('Users.csv')
    for uid in range(1, num_users + 1):
        profile = fake.profile()
        email = profile['mail']
        password = generate_password_hash(f'password{uid}')
        firstname, lastname = profile['name'].split()[0], profile['name'].split()[-1]
        address = fake.address().replace("\n", ", ")
        balance = round(random.uniform(0, 1000), 2)
        writer.writerow([uid, email, password, firstname, lastname, address, balance])
    return list(range(1, num_users + 1))  # Return list of user IDs

def gen_sellers(user_ids):
    writer = get_csv_writer('Sellers.csv')
    seller_ids = random.sample(user_ids, len(user_ids) // 2)  # Half of the users are sellers
    for sid in seller_ids:
        writer.writerow([sid])
    return seller_ids

def gen_products(num_products):
    writer = get_csv_writer('Products.csv')
    available_pids = []
    for pid in range(1, num_products + 1):
        name = fake.unique.sentence(nb_words=4)[:-1]
        description = fake.text(max_nb_chars=100)
        available = fake.boolean(chance_of_getting_true=70)
        if available:
            available_pids.append(pid)
        writer.writerow([pid, name, description, available])
    return available_pids

def gen_created_product(user_ids, product_ids):
    writer = get_csv_writer('CreatedProduct.csv')
    for pid in product_ids:
        uid = random.choice(user_ids)
        writer.writerow([pid, uid])

def gen_tags(num_tags):
    writer = get_csv_writer('Tags.csv')
    tags = [fake.unique.word() for _ in range(num_tags)]
    for tag_name in tags:
        writer.writerow([tag_name])
    return tags

def gen_is_tagged(product_ids, tags):
    writer = get_csv_writer('IsTagged.csv')
    for pid in product_ids:
        tag_name = random.choice(tags)
        writer.writerow([pid, tag_name])

def gen_sold_by(product_ids, seller_ids):
    writer = get_csv_writer('SoldBy.csv')
    for pid in product_ids:
        sid = random.choice(seller_ids)
        quantity = random.randint(1, 100)
        price = round(random.uniform(5, 500), 2)
        writer.writerow([sid, pid, quantity, price])

def gen_purchases(user_ids, product_ids, seller_ids, num_purchases):
    writer = get_csv_writer('Purchases.csv')
    for _ in range(num_purchases):
        uid = random.choice(user_ids)
        pid = random.choice(product_ids)
        sid = random.choice(seller_ids)
        quantity = random.randint(1, 5)
        time_purchased = fake.date_time_this_decade()
        writer.writerow([uid, pid, sid, time_purchased, quantity])

def gen_reviews(num_reviews):
    writer = get_csv_writer('Reviews.csv')
    for rid in range(1, num_reviews + 1):
        rating = random.randint(1, 5)
        description = fake.text(max_nb_chars=100)
        time_created = fake.date_time_this_decade()
        writer.writerow([rid, rating, description, time_created])
    return list(range(1, num_reviews + 1))  # Return list of review IDs

def gen_product_reviews(review_ids, user_ids, product_ids):
    writer = get_csv_writer('ProductReviews.csv')
    for rid in review_ids:
        uid = random.choice(user_ids)
        pid = random.choice(product_ids)
        writer.writerow([rid, uid, pid])

def gen_seller_reviews(review_ids, user_ids, seller_ids):
    writer = get_csv_writer('SellerReviews.csv')
    for rid in random.sample(review_ids, len(seller_ids)):
        uid = random.choice(user_ids)
        sid = random.choice(seller_ids)
        writer.writerow([rid, uid, sid])

def gen_categories(num_categories):
    writer = get_csv_writer('Categories.csv')
    categories = [fake.unique.word() for _ in range(num_categories)]
    for cid, category_name in enumerate(categories, 1):
        writer.writerow([cid, category_name])
    return list(range(1, num_categories + 1))  # Return list of category IDs

def gen_category_of(product_ids, category_ids):
    writer = get_csv_writer('CategoryOf.csv')
    for pid in product_ids:
        cid = random.choice(category_ids)
        writer.writerow([pid, cid])

def gen_inventory(product_ids, seller_ids):
    writer = get_csv_writer('Inventory.csv')
    for pid in product_ids:
        sid = random.choice(seller_ids)
        quantity = random.randint(1, 100)
        writer.writerow([sid, pid, quantity])

def gen_helpfulness(review_ids, user_ids):
    writer = get_csv_writer('Helpfulness.csv')
    for rid in review_ids:
        uid = random.choice(user_ids)
        value = random.choice([-1, 0, 1])
        writer.writerow([uid, rid, value])

# Generate data for all tables
user_ids = gen_users(NUM_USERS)
seller_ids = gen_sellers(user_ids)  # Use user IDs to create seller records
product_ids = gen_products(NUM_PRODUCTS)
gen_created_product(user_ids, product_ids)
tags = gen_tags(NUM_TAGS)
gen_is_tagged(product_ids, tags)
gen_sold_by(product_ids, seller_ids)
gen_purchases(user_ids, product_ids, seller_ids, NUM_PURCHASES)
review_ids = gen_reviews(NUM_REVIEWS)
gen_product_reviews(review_ids, user_ids, product_ids)
gen_seller_reviews(review_ids, user_ids, seller_ids)
category_ids = gen_categories(NUM_CATEGORIES)
gen_category_of(product_ids, category_ids)
gen_inventory(product_ids, seller_ids)
gen_helpfulness(review_ids, user_ids)
