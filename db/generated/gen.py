from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random
from datetime import datetime
from tqdm import tqdm

# Configuration for the number of entries in each table
NUM_USERS = 2000
NUM_SELLERS = 100
NUM_PRODUCTS = 500
NUM_INVENTORY = 4000
NUM_SOLD_BY = 2000
NUM_REVIEWS = 2000

Faker.seed(0)
fake = Faker()

def get_csv_writer(filename):
    return csv.writer(open(filename, 'w'), dialect='unix')

def gen_users(num_users):
    writer = get_csv_writer('Users.csv')
    users = []  # Keep track of user IDs and their plaintext passwords for testing
    for uid in tqdm(range(num_users)):
        email = fake.unique.email()  # Ensure email is unique
        plaintext_password = f'password{uid}'  # Plaintext password for testing
        hashed_password = generate_password_hash(plaintext_password)  # Hashed password
        firstname = fake.first_name()
        lastname = fake.last_name()
        address = fake.address().replace("\n", ", ")  # Single-line address
        balance = round(random.uniform(0, 1000), 2)  # Random balance >= 0
        writer.writerow([uid, email, hashed_password, firstname, lastname, address, balance])
        users.append(uid)
    return users

def gen_sellers(user_ids, num_sellers):
    writer = get_csv_writer('Sellers.csv')
    sellers = random.sample(user_ids, num_sellers)  # Randomly select seller IDs from users
    for sid in sellers:
        writer.writerow([sid])  # Write seller ID
    return sellers

def gen_products(num_products):
    writer = get_csv_writer('Products.csv')
    product_ids = []  # Track product IDs
    for pid in tqdm(range(num_products), desc="Generating Products"):
        name = fake.unique.sentence(nb_words=2)[:-1]  # Unique name, strip trailing period
        description = fake.text(max_nb_chars=100)  # Random description
        available = True  # 70% chance of being available
        writer.writerow([pid, name, description, available])
        product_ids.append(pid)
    return product_ids

def gen_inventory(seller_ids, product_ids, num_entries):
    writer = get_csv_writer('Inventory.csv')
    inventory = {}  # Track inventory as a dictionary {(sid, pid): quantity}

    for _ in tqdm(range(num_entries), desc="Generating Inventory"):
        sid = random.choice(seller_ids)  # Select a seller
        pid = random.choice(product_ids)  # Select a product

        # Ensure (sid, pid) is unique
        if (sid, pid) not in inventory:
            quantity = random.randint(10, 500)  # Random inventory quantity
            inventory[(sid, pid)] = quantity
            writer.writerow([sid, pid, quantity])

    return inventory

def gen_sold_by(inventory, num_entries):
    writer = get_csv_writer('SoldBy.csv')
    sold_by = set()  # Track (sid, pid) pairs

    for _ in tqdm(range(num_entries), desc="Generating SoldBy"):
        sid, pid = random.choice(list(inventory.keys()))  # Choose from inventory
        max_quantity = inventory[(sid, pid)]  # Maximum quantity available in inventory

        # Ensure (sid, pid) is unique
        if (sid, pid) not in sold_by:
            quantity = random.randint(1, max_quantity)  # Quantity sold must be <= inventory
            price = round(random.uniform(5, 500), 2)  # Random price
            sold_by.add((sid, pid))  # Mark this (sid, pid) pair as used
            writer.writerow([sid, pid, quantity, price])

def gen_reviews(num_reviews):
    writer = get_csv_writer('Reviews.csv')
    review_ids = []

    for rid in tqdm(range(num_reviews), desc="Generating Reviews"):
        rating = random.randint(1, 5)  # Random rating between 1 and 5
        description = fake.text(max_nb_chars=100)  # Description text
        time_created = fake.date_time_this_decade()  # Timestamp for review
        writer.writerow([rid, rating, description, time_created])
        review_ids.append(rid)

    return review_ids

def gen_product_reviews_and_seller_reviews(review_ids, user_ids, product_ids, seller_ids):
    product_writer = get_csv_writer('ProductReviews.csv')
    seller_writer = get_csv_writer('SellerReviews.csv')
    used_product_pairs = set()  # Track (uid, pid) for uniqueness in ProductReviews
    used_seller_pairs = set()   # Track (uid, sid) for uniqueness in SellerReviews

    for rid in tqdm(review_ids, desc="Generating ProductReviews and SellerReviews"):
        uid = random.choice(user_ids)  # Select a random user for the review

        if random.choice([True, False]):  # Randomly decide if it's a product review
            # Generate ProductReview entry
            while True:
                pid = random.choice(product_ids)
                if (uid, pid) not in used_product_pairs:
                    used_product_pairs.add((uid, pid))
                    product_writer.writerow([rid, uid, pid])  # Write to ProductReviews.csv
                    break
        else:
            # Generate SellerReview entry
            while True:
                sid = random.choice(seller_ids)
                if (uid, sid) not in used_seller_pairs:
                    used_seller_pairs.add((uid, sid))
                    seller_writer.writerow([rid, uid, sid])  # Write to SellerReviews.csv
                    break


def gen_helpfulness(review_ids, user_ids):
    writer = get_csv_writer('Helpfulness.csv')
    used_pairs = set()  # Track (uid, rid) for uniqueness

    for rid in tqdm(review_ids, desc="Generating Helpfulness"):
        uid = random.choice(user_ids)
        if (uid, rid) not in used_pairs:
            used_pairs.add((uid, rid))
            value = random.choice([-1, 0, 1])  # Random feedback value
            writer.writerow([uid, rid, value])



user_ids = gen_users(NUM_USERS)  # Generate users
seller_ids = gen_sellers(user_ids, NUM_SELLERS)  # Generate sellers from users
product_ids = gen_products(NUM_PRODUCTS)  # Generate products
inventory = gen_inventory(seller_ids, product_ids, NUM_INVENTORY)
gen_sold_by(inventory, NUM_SOLD_BY)
review_ids = gen_reviews(NUM_REVIEWS)
gen_product_reviews_and_seller_reviews(review_ids, user_ids, product_ids, seller_ids)
gen_helpfulness(review_ids, user_ids)