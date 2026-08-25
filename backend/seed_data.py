import os
import random
import time
from datetime import timedelta
from neo4j import GraphDatabase
from neo4j.exceptions import IncompleteCommit, ServiceUnavailable, SessionExpired
from dotenv import load_dotenv
from faker import Faker

load_dotenv()
fake = Faker()

URI = os.getenv("COGNODB_URI")
USER = os.getenv("COGNODB_USER")
PASSWORD = os.getenv("COGNODB_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

NUM_VISITORS = 60
NUM_PRODUCTS = 20
BATCH_SIZE = 100          # rows per UNWIND batch
MAX_RETRIES = 5
RETRY_BACKOFF_SECONDS = 3

PRODUCT_NAMES = [
    "Wireless Headphones", "Running Shoes", "Smart Watch", "Backpack",
    "Coffee Maker", "Bluetooth Speaker", "Yoga Mat", "Desk Lamp",
    "Water Bottle", "Sunglasses", "Laptop Stand", "Phone Case",
    "Electric Kettle", "Office Chair", "Wireless Mouse", "Notebook Set",
    "Table Lamp", "Travel Pillow", "Fitness Tracker", "Portable Charger",
]

PAGES = [
    {"url": "/", "title": "Home", "category": "landing"},
    {"url": "/blog", "title": "Blog", "category": "blog"},
    {"url": "/products", "title": "All Products", "category": "listing"},
    {"url": "/product/1", "title": "Wireless Headphones", "category": "product"},
    {"url": "/product/2", "title": "Running Shoes", "category": "product"},
    {"url": "/product/3", "title": "Smart Watch", "category": "product"},
    {"url": "/product/4", "title": "Backpack", "category": "product"},
    {"url": "/product/5", "title": "Coffee Maker", "category": "product"},
    {"url": "/cart", "title": "Cart", "category": "cart"},
    {"url": "/checkout", "title": "Checkout", "category": "checkout"},
    {"url": "/confirmation", "title": "Order Confirmed", "category": "confirmation"},
    {"url": "/about", "title": "About Us", "category": "info"},
    {"url": "/contact", "title": "Contact", "category": "info"},
]
REFERRERS = ["google", "direct", "instagram", "facebook", "email", "twitter"]
DEVICE_TYPES = ["desktop", "mobile", "tablet"]
EVENT_TYPES = ["add_to_cart", "signup", "purchase"]

def run_with_retry(session, work_func, *args, **kwargs):
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return session.execute_write(work_func, *args, **kwargs)
        except (IncompleteCommit, ServiceUnavailable, SessionExpired, OSError) as e:
            last_error = e
            wait = RETRY_BACKOFF_SECONDS * attempt
            print(f"  [retry {attempt}/{MAX_RETRIES}] connection issue ({e.__class__.__name__}), "
                  f"waiting {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"Failed after {MAX_RETRIES} retries") from last_error


def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def clear_db(tx):
    tx.run("MATCH (n) DETACH DELETE n")

def batch_create_pages(tx, rows):
    tx.run(
        """
        UNWIND $rows AS row
        MERGE (p:Page {page_id: row.page_id})
        SET p.url = row.url, p.title = row.title, p.category = row.category
        RETURN count(p) AS created
        """,
        rows=rows
    )


def batch_create_products(tx, rows):
    tx.run(
        """
        UNWIND $rows AS row
        CREATE (pr:Product {
            product_id: row.product_id, name: row.name,
            category: row.category, price: row.price
        })
        RETURN count(pr) AS created
        """,
        rows=rows
    )


def batch_create_visitors(tx, rows):
    tx.run(
        """
        UNWIND $rows AS row
        CREATE (v:Visitor {
            visitor_id: row.visitor_id, first_seen: row.first_seen,
            device_type: row.device_type, country: row.country
        })
        RETURN count(v) AS created
        """,
        rows=rows
    )


def batch_create_sessions(tx, rows):
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (v:Visitor {visitor_id: row.visitor_id})
        CREATE (s:Session {
            session_id: row.session_id, started_at: row.started_at,
            ended_at: row.ended_at, referrer_source: row.referrer_source
        })
        CREATE (v)-[:STARTED_SESSION]->(s)
        RETURN count(s) AS created
        """,
        rows=rows
    )


def batch_add_page_views(tx, rows):
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (s:Session {session_id: row.session_id})
        MATCH (p:Page {page_id: row.page_id})
        CREATE (s)-[:VIEWED {timestamp: row.timestamp, duration_seconds: row.duration_seconds}]->(p)
        RETURN count(*) AS created
        """,
        rows=rows
    )


def batch_add_next_links(tx, rows):
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (p1:Page {page_id: row.prev_page_id})
        MATCH (p2:Page {page_id: row.page_id})
        CREATE (p1)-[:NEXT {sequence_number: row.sequence_number, session_id: row.session_id}]->(p2)
        RETURN count(*) AS created
        """,
        rows=rows
    )


def batch_add_events(tx, rows):
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (s:Session {session_id: row.session_id})
        CREATE (e:Event {event_id: row.event_id, type: row.event_type, timestamp: row.timestamp})
        CREATE (s)-[:TRIGGERED {timestamp: row.timestamp}]->(e)
        RETURN count(e) AS created
        """,
        rows=rows
    )


def batch_link_event_products(tx, rows):
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (e:Event {event_id: row.event_id})
        MATCH (pr:Product {product_id: row.product_id})
        CREATE (e)-[:RELATED_TO]->(pr)
        RETURN count(*) AS created
        """,
        rows=rows
    )


def batch_add_purchases(tx, rows):
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (v:Visitor {visitor_id: row.visitor_id})
        MATCH (pr:Product {product_id: row.product_id})
        CREATE (v)-[:PURCHASED {timestamp: row.timestamp, amount: row.amount}]->(pr)
        RETURN count(*) AS created
        """,
        rows=rows
    )


def batch_link_returning_sessions(tx, rows):
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (s1:Session {session_id: row.prev_session_id})
        MATCH (s2:Session {session_id: row.next_session_id})
        CREATE (s1)-[:RETURNED_AS {days_gap: row.days_gap}]->(s2)
        RETURN count(*) AS created
        """,
        rows=rows
    )

def run_batched(session, label, work_func, rows):
    if not rows:
        return
    batches = list(chunked(rows, BATCH_SIZE))
    for idx, batch in enumerate(batches, start=1):
        print(f"  {label}: batch {idx}/{len(batches)} ({len(batch)} rows)")
        run_with_retry(session, work_func, batch)

def seed():
    with driver.session() as db:
        print("Clearing existing data...")
        run_with_retry(db, clear_db)

        print("Preparing pages...")
        page_rows = [
            {"page_id": f"page_{i}", "url": p["url"], "title": p["title"], "category": p["category"]}
            for i, p in enumerate(PAGES, start=1)
        ]
        run_batched(db, "pages", batch_create_pages, page_rows)

        print("Preparing products...")
        product_ids = [f"prod_{i}" for i in range(1, NUM_PRODUCTS + 1)]
        product_rows = [
            {
                "product_id": pid,
                "name": PRODUCT_NAMES[i % len(PRODUCT_NAMES)],
                "category": random.choice(["electronics", "apparel", "home", "accessories"]),
                "price": round(random.uniform(10, 500), 2),
            }
            for i, pid in enumerate(product_ids)
        ]
        run_batched(db, "products", batch_create_products, product_rows)

        print("Preparing visitors, sessions, page views, events...")
        visitor_rows = []
        session_rows = []
        page_view_rows = []
        next_link_rows = []
        event_rows = []
        event_product_rows = []
        purchase_rows = []
        returning_session_rows = []

        for i in range(1, NUM_VISITORS + 1):
            visitor_id = f"visitor_{i}"
            first_seen = fake.date_time_between(start_date="-60d", end_date="-30d")
            visitor_rows.append({
                "visitor_id": visitor_id,
                "first_seen": first_seen.isoformat(),
                "device_type": random.choice(DEVICE_TYPES),
                "country": fake.country(),
            })

            num_sessions = random.randint(1, 4)
            session_ids_for_visitor = []
            session_start_time = first_seen

            for s in range(num_sessions):
                session_id = f"{visitor_id}_session_{s + 1}"
                session_start_time += timedelta(days=random.randint(1, 10))
                session_end_time = session_start_time + timedelta(minutes=random.randint(2, 30))

                session_rows.append({
                    "session_id": session_id,
                    "visitor_id": visitor_id,
                    "started_at": session_start_time.isoformat(),
                    "ended_at": session_end_time.isoformat(),
                    "referrer_source": random.choice(REFERRERS),
                })
                session_ids_for_visitor.append(session_id)

                path_length = random.randint(2, 6)
                current_time = session_start_time
                prev_page_id = None
                visited_page_ids = random.sample(range(1, len(PAGES) + 1), min(path_length, len(PAGES)))

                for seq, page_num in enumerate(visited_page_ids, start=1):
                    page_id = f"page_{page_num}"
                    duration = random.randint(5, 180)
                    page_view_rows.append({
                        "session_id": session_id,
                        "page_id": page_id,
                        "timestamp": current_time.isoformat(),
                        "duration_seconds": duration,
                    })
                    if prev_page_id:
                        next_link_rows.append({
                            "prev_page_id": prev_page_id,
                            "page_id": page_id,
                            "sequence_number": seq,
                            "session_id": session_id,
                        })
                    prev_page_id = page_id
                    current_time += timedelta(seconds=duration)

                # Randomly trigger an event
                if random.random() < 0.5:
                    event_id = f"{session_id}_event_1"
                    event_type = random.choice(EVENT_TYPES)
                    chosen_product = random.choice(product_ids)
                    event_rows.append({
                        "event_id": event_id,
                        "session_id": session_id,
                        "event_type": event_type,
                        "timestamp": current_time.isoformat(),
                    })
                    if event_type in ("add_to_cart", "purchase"):
                        event_product_rows.append({
                            "event_id": event_id,
                            "product_id": chosen_product,
                        })
                    if event_type == "purchase":
                        purchase_rows.append({
                            "visitor_id": visitor_id,
                            "product_id": chosen_product,
                            "timestamp": current_time.isoformat(),
                            "amount": round(random.uniform(10, 500), 2),
                        })

            for idx in range(len(session_ids_for_visitor) - 1):
                returning_session_rows.append({
                    "prev_session_id": session_ids_for_visitor[idx],
                    "next_session_id": session_ids_for_visitor[idx + 1],
                    "days_gap": random.randint(1, 10),
                })

        run_batched(db, "visitors", batch_create_visitors, visitor_rows)
        run_batched(db, "sessions", batch_create_sessions, session_rows)
        run_batched(db, "page views", batch_add_page_views, page_view_rows)
        run_batched(db, "NEXT links", batch_add_next_links, next_link_rows)
        run_batched(db, "events", batch_add_events, event_rows)
        run_batched(db, "event->product links", batch_link_event_products, event_product_rows)
        run_batched(db, "purchases", batch_add_purchases, purchase_rows)
        run_batched(db, "returning sessions", batch_link_returning_sessions, returning_session_rows)

        print("Seeding complete!")


if __name__ == "__main__":
    seed()
    driver.close()