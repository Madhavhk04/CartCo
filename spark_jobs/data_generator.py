import os
import csv
import random
from datetime import datetime, timedelta

def generate_datasets(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating products...")
    categories = {
        "Electronics": ("Smart Watch", "Wireless Earbuds", "Phone Charger", "Bluetooth Speaker", "Laptop Stand", "USB-C Hub", "Tablet Pen", "Power Bank"),
        "Apparel": ("Denim Jacket", "Cotton T-Shirt", "Running Shoes", "Woolen Socks", "Leather Belt", "Sunglasses", "Sports Hoodie", "Canvas Backpack"),
        "Home & Kitchen": ("Coffee Maker", "Air Fryer", "Blender", "Chef Knife", "Silicone Spatula", "Water Bottle", "Non-stick Pan", "Food Storage Set"),
        "Beauty & Personal Care": ("Face Wash", "Moisturizer", "Sunscreen", "Shampoo", "Hair Dryer", "Electric Toothbrush", "Lip Balm", "Body Wash"),
        "Sports & Outdoors": ("Yoga Mat", "Dumbbells", "Resistance Bands", "Camping Tent", "Sleeping Bag", "Bicycle Helmet", "Hiking Backpack", "Waterproof Jacket")
    }
    
    products = []
    product_price_map = {}
    for i in range(1, 1001):
        prod_id = f"PROD_{i:03d}"
        category = random.choice(list(categories.keys()))
        item_base = random.choice(categories[category])
        brand = random.choice(["Volt", "Nexa", "Apex", "Aero", "Prime", "Luxe", "Eco", "Terra"])
        product_name = f"{brand} {item_base}"
        
        cost_price = round(random.uniform(5.0, 150.0), 2)
        retail_price = round(cost_price * random.uniform(1.3, 2.2), 2)
        supplier = random.choice(["Global Distribution Inc.", "Apex Logistics", "EcoGroup Wholesale", "PrimeRetail Corp"])
        
        products.append({
            "product_id": prod_id,
            "product_name": product_name,
            "category": category,
            "cost_price": cost_price,
            "retail_price": retail_price,
            "supplier": supplier
        })
        product_price_map[prod_id] = (cost_price, retail_price)
        
    with open(os.path.join(output_dir, "products.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=products[0].keys())
        writer.writeheader()
        writer.writerows(products)
        
    print("Generating customers...")
    regions = ["North", "East", "West", "South", "Central"]
    first_names = ["Rahul", "Priya", "Amit", "Neha", "Vijay", "Anjali", "John", "Sarah", "Michael", "Emma", "David", "Sophia", "James", "Olivia", "Robert", "Isabella"]
    last_names = ["Sharma", "Verma", "Patel", "Singh", "Gupta", "Das", "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson"]
    
    customers = []
    start_date = datetime(2025, 1, 1)
    for i in range(1, 10001):
        cust_id = f"CUST_{i:05d}"
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        email = f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@example.com"
        phone = f"+91{random.randint(7000000000, 9999999999)}" if random.random() > 0.4 else f"+1{random.randint(2000000000, 9999999999)}"
        signup_date = (start_date + timedelta(days=random.randint(0, 500))).strftime("%Y-%m-%d")
        region = random.choice(regions)
        country = "India" if phone.startswith("+91") else random.choice(["USA", "Canada", "UK"])
        
        customers.append({
            "customer_id": cust_id,
            "first_name": fn,
            "last_name": ln,
            "email": email,
            "phone": phone,
            "signup_date": signup_date,
            "region": region,
            "country": country
        })
        
    with open(os.path.join(output_dir, "customers.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=customers[0].keys())
        writer.writeheader()
        writer.writerows(customers)
        
    print("Generating inventory...")
    inventory = []
    warehouses = ["WH-Mumbai", "WH-Delhi", "WH-Bangalore", "WH-Texas", "WH-London"]
    for p in products:
        p_id = p["product_id"]
        stock_on_hand = random.randint(10, 500)
        reserved_stock = random.randint(0, min(stock_on_hand, 50))
        restock_threshold = random.randint(15, 60)
        warehouse_location = random.choice(warehouses)
        last_updated = datetime.now() - timedelta(hours=random.randint(1, 48))
        
        inventory.append({
            "product_id": p_id,
            "stock_on_hand": stock_on_hand,
            "reserved_stock": reserved_stock,
            "warehouse_location": warehouse_location,
            "restock_threshold": restock_threshold,
            "last_updated": last_updated.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    with open(os.path.join(output_dir, "inventory.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=inventory[0].keys())
        writer.writeheader()
        writer.writerows(inventory)
        
    print("Generating orders (Shopify, Amazon, Flipkart)...")
    total_shopify = 40000
    total_amazon = 35000
    total_flipkart = 25000
    
    order_start_date = datetime(2025, 2, 1)
    
    print("- Shopify orders...")
    shopify_orders = []
    shopify_payment_methods = ["Credit Card", "PayPal", "UPI", "Gift Card", "Apple Pay"]
    shopify_fulfillment_states = ["fulfilled", "fulfilled", "fulfilled", "unfulfilled", "cancelled"]
    
    for i in range(1, total_shopify + 1):
        o_id = f"SH_{1000000 + i}"
        cust_id = f"CUST_{random.randint(1, 10000):05d}"
        prod_id = f"PROD_{random.randint(1, 1000):03d}"
        qty = random.randint(1, 5)
        _, retail = product_price_map[prod_id]
        
        delta_seconds = random.randint(0, 500 * 24 * 3600)
        o_date = order_start_date + timedelta(seconds=delta_seconds)
        
        discount = round(random.choice([0.0, 0.0, 0.0, 0.1, 0.15, 0.20]) * (retail * qty), 2)
        shipping_fee = round(random.choice([0.0, 5.0, 10.0]), 2)
        taxes = round((retail * qty - discount) * 0.18, 2)
        fulfillment = random.choice(shopify_fulfillment_states)
        refund_flag = 1 if fulfillment == "fulfilled" and random.random() < 0.04 else 0
        
        shopify_orders.append({
            "order_id": o_id,
            "customer_id": cust_id,
            "product_id": prod_id,
            "order_date": o_date.strftime("%Y-%m-%d %H:%M:%S"),
            "quantity": qty,
            "unit_price": retail,
            "discount": discount,
            "shipping_fee": shipping_fee,
            "taxes": taxes,
            "payment_method": random.choice(shopify_payment_methods),
            "fulfillment_status": fulfillment,
            "refund_flag": refund_flag
        })
        
    with open(os.path.join(output_dir, "shopify_orders.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=shopify_orders[0].keys())
        writer.writeheader()
        writer.writerows(shopify_orders)
        
    print("- Amazon orders...")
    amazon_orders = []
    amazon_cities = [("Mumbai", "MH"), ("Delhi", "DL"), ("Bangalore", "KA"), ("Seattle", "WA"), ("New York", "NY"), ("Houston", "TX")]
    ship_service_levels = ["Standard", "Expedited", "SecondDay"]
    
    for i in range(1, total_amazon + 1):
        o_id = f"AMZ-{random.randint(100, 999):03d}-{random.randint(1000000, 9999999):07d}-{random.randint(1000000, 9999999):07d}"
        cust_id = f"CUST_{random.randint(1, 10000):05d}"
        prod_id = f"PROD_{random.randint(1, 1000):03d}"
        qty = random.randint(1, 3)
        _, retail = product_price_map[prod_id]
        
        delta_seconds = random.randint(0, 500 * 24 * 3600)
        o_date = order_start_date + timedelta(seconds=delta_seconds)
        
        purchase_date = o_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        item_tax = round(retail * qty * 0.12, 2)
        shipping_price = round(random.choice([0.0, 0.0, 3.99, 5.99]), 2)
        gift_wrap_price = round(random.choice([0.0, 0.0, 0.0, 2.99]), 2)
        city, state = random.choice(amazon_cities)
        
        amazon_orders.append({
            "amazon_order_id": o_id,
            "customer_id": cust_id,
            "product_id": prod_id,
            "purchase_date": purchase_date,
            "quantity": qty,
            "item_price": retail,
            "shipping_price": shipping_price,
            "gift_wrap_price": gift_wrap_price,
            "item_tax": item_tax,
            "ship_service_level": random.choice(ship_service_levels),
            "ship_city": city,
            "ship_state": state
        })
        
    with open(os.path.join(output_dir, "amazon_orders.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=amazon_orders[0].keys())
        writer.writeheader()
        writer.writerows(amazon_orders)
        
    print("- Flipkart orders...")
    flipkart_orders = []
    flipkart_statuses = ["Delivered", "Delivered", "Delivered", "Returned", "Cancelled"]
    flipkart_payment_types = ["COD", "Prepaid"]
    
    for i in range(1, total_flipkart + 1):
        o_id = f"FLK{random.randint(1000000000000000, 9999999999999999)}"
        cust_id = f"CUST_{random.randint(1, 10000):05d}"
        prod_id = f"PROD_{random.randint(1, 1000):03d}"
        qty = random.randint(1, 4)
        _, retail = product_price_map[prod_id]
        
        delta_seconds = random.randint(0, 500 * 24 * 3600)
        o_date = order_start_date + timedelta(seconds=delta_seconds)
        
        order_timestamp = o_date.strftime("%d/%m/%Y %H:%M")
        
        discount_percent = random.choice([0, 0, 5, 10, 15, 20])
        delivery_charges = round(random.choice([0.0, 40.0, 50.0]), 2)
        
        flipkart_orders.append({
            "flipkart_order_id": o_id,
            "customer_id": cust_id,
            "product_id": prod_id,
            "order_timestamp": order_timestamp,
            "qty": qty,
            "price_per_unit": retail,
            "discount_percent": discount_percent,
            "delivery_charges": delivery_charges,
            "payment_type": random.choice(flipkart_payment_types),
            "order_status": random.choice(flipkart_statuses)
        })
        
    with open(os.path.join(output_dir, "flipkart_orders.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=flipkart_orders[0].keys())
        writer.writeheader()
        writer.writerows(flipkart_orders)
        
    print("All datasets generated successfully!")

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "data"
    generate_datasets(out)
