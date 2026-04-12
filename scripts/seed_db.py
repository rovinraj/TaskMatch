"""
seed_db.py — Seeds the taskmatch database with sample data from Python.
Use this if LOAD DATA LOCAL INFILE is not available.

Usage:
    python scripts/seed_db.py
"""

import os
import sys
import mysql.connector
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'taskmatch'),
    'charset': 'utf8mb4',
}


def seed():
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()

    pw = generate_password_hash('password123')

    # ── USERS ──
    users = [
        (1, 'Jordan Smith', 'jordan@email.com', '+1 (972) 555-0142', pw, 'client'),
        (2, 'Marcus Rivera', 'marcus@email.com', '+1 (972) 555-0201', pw, 'provider'),
        (3, 'Sandra Chen', 'sandra@email.com', '+1 (972) 555-0302', pw, 'provider'),
        (4, 'James Thornton', 'james@email.com', '+1 (972) 555-0403', pw, 'provider'),
        (5, 'Diane Kim', 'diane@email.com', '+1 (972) 555-0504', pw, 'provider'),
        (6, 'Tony Bellucci', 'tony@email.com', '+1 (972) 555-0605', pw, 'provider'),
        (7, 'Amara Lewis', 'amara@email.com', '+1 (972) 555-0706', pw, 'provider'),
        (8, 'David Martinez', 'david@email.com', '+1 (972) 555-0807', pw, 'client'),
        (9, 'Emily Watson', 'emily@email.com', '+1 (972) 555-0908', pw, 'client'),
        (10, 'Admin User', 'admin@taskmatch.com', '+1 (972) 555-0000', pw, 'admin'),
        (11, 'Robert Jackson', 'robert@email.com', '+1 (972) 555-1101', pw, 'provider'),
        (12, 'Maria Garcia', 'maria@email.com', '+1 (972) 555-1202', pw, 'provider'),
        (13, 'Kevin Brown', 'kevin@email.com', '+1 (972) 555-1303', pw, 'client'),
        (14, 'Lisa Nguyen', 'lisa@email.com', '+1 (972) 555-1404', pw, 'provider'),
        (15, 'Chris Davis', 'chris@email.com', '+1 (972) 555-1505', pw, 'provider'),
    ]
    cur.executemany(
        "INSERT INTO users (user_id, name, email, phone, password_hash, role) VALUES (%s,%s,%s,%s,%s,%s)",
        users
    )
    print(f"  Inserted {len(users)} users")

    # ── LOCATIONS ──
    locations = [
        (1, 1, 'Richardson', 'TX', '75080'),
        (2, 2, 'Richardson', 'TX', '75080'),
        (3, 3, 'Plano', 'TX', '75024'),
        (4, 4, 'Dallas', 'TX', '75201'),
        (5, 5, 'Richardson', 'TX', '75082'),
        (6, 6, 'Allen', 'TX', '75013'),
        (7, 7, 'Frisco', 'TX', '75034'),
        (8, 8, 'McKinney', 'TX', '75070'),
        (9, 9, 'Plano', 'TX', '75025'),
        (10, 10, 'Richardson', 'TX', '75080'),
        (11, 11, 'Garland', 'TX', '75040'),
        (12, 12, 'Irving', 'TX', '75060'),
        (13, 13, 'Richardson', 'TX', '75081'),
        (14, 14, 'Dallas', 'TX', '75204'),
        (15, 15, 'Plano', 'TX', '75023'),
    ]
    cur.executemany(
        "INSERT INTO locations (location_id, user_id, city, state, zip_code) VALUES (%s,%s,%s,%s,%s)",
        locations
    )
    print(f"  Inserted {len(locations)} locations")

    # ── SERVICE CATEGORIES ──
    categories = [
        (1, 'Plumbing'), (2, 'Electrical'), (3, 'HVAC'), (4, 'Handyman'),
        (5, 'Appliance Repair'), (6, 'Roofing'), (7, 'Pest Control'),
        (8, 'Landscaping'), (9, 'Carpentry'), (10, 'Painting'),
    ]
    cur.executemany(
        "INSERT INTO service_categories (category_id, category_name) VALUES (%s,%s)",
        categories
    )
    print(f"  Inserted {len(categories)} categories")

    # ── PROVIDER PROFILES ──
    providers = [
        (1, 2, '15 yrs specializing in residential leak detection, pipe repair, and emergency drain services. Licensed & insured.', 75.00, True, 4.90),
        (2, 3, 'Certified electrician with 12 years experience. Residential and commercial wiring, outlet repair, panel upgrades.', 90.00, True, 4.80),
        (3, 4, 'Skilled carpenter and handyman. Specializing in custom woodwork, furniture repair, and home improvement.', 65.00, True, 4.70),
        (4, 5, 'Plumbing and fixtures specialist. Under-sink repairs, fixture replacement, kitchen and bath renovations.', 68.00, True, 4.80),
        (5, 6, 'Full-service plumbing contractor with 20+ years. Leak detection, water damage prevention, pipe replacement.', 90.00, True, 4.70),
        (6, 7, 'Multi-trade specialist handling plumbing, HVAC, and moisture control. Ideal for complex home issues.', 85.00, True, 4.90),
        (7, 11, 'HVAC technician specializing in AC repair, furnace maintenance, and ventilation systems. EPA certified.', 80.00, True, 4.60),
        (8, 12, 'Professional painter with 8 years experience. Interior, exterior, residential and commercial painting.', 55.00, True, 4.50),
        (9, 14, 'Pest control expert. Licensed for residential and commercial pest management. Eco-friendly options.', 70.00, True, 4.70),
        (10, 15, 'Roofing contractor with 15 years experience. Shingle repair, leak repair, gutter installation.', 95.00, True, 4.80),
    ]
    cur.executemany(
        """INSERT INTO provider_profiles
           (provider_id, user_id, bio, rate, verified_status, average_rating)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        providers
    )
    print(f"  Inserted {len(providers)} provider profiles")

    # ── SERVICE LISTINGS ──
    listings = [
        (1, 1, 1, 'Emergency Leak Repair', 'Fast response leak detection and repair for pipes, faucets, and drains.', 75.00, 'active'),
        (2, 1, 1, 'Drain Cleaning Service', 'Professional drain clearing and maintenance for kitchens and bathrooms.', 60.00, 'active'),
        (3, 2, 2, 'Electrical Outlet Repair', 'Fix broken outlets, install new ones, and upgrade old wiring.', 90.00, 'active'),
        (4, 2, 2, 'Panel and Breaker Service', 'Breaker replacement, panel upgrades, and electrical inspections.', 120.00, 'active'),
        (5, 3, 9, 'Custom Woodwork', 'Shelving, cabinets, trim work, and custom furniture repairs.', 65.00, 'active'),
        (6, 3, 4, 'General Handyman Services', 'Door repair, mounting, installations, and minor home repairs.', 55.00, 'active'),
        (7, 4, 1, 'Kitchen and Bath Plumbing', 'Fixture installation, faucet repair, and under-sink plumbing.', 68.00, 'active'),
        (8, 5, 1, 'Pipe Replacement', 'Full pipe replacement, leak detection, and water damage prevention.', 90.00, 'active'),
        (9, 6, 1, 'Plumbing and HVAC Combo', 'Combined plumbing and ventilation for complex moisture issues.', 85.00, 'active'),
        (10, 6, 3, 'HVAC Maintenance', 'AC tune-up, furnace check, and air quality assessment.', 85.00, 'active'),
        (11, 7, 3, 'AC Repair and Install', 'Air conditioning repair, installation, and seasonal maintenance.', 80.00, 'active'),
        (12, 7, 3, 'Furnace Service', 'Furnace repair, maintenance, and replacement. Gas and electric.', 80.00, 'active'),
        (13, 8, 10, 'Interior Painting', 'Professional interior painting for rooms, walls, and trim.', 55.00, 'active'),
        (14, 8, 10, 'Exterior Painting', 'House exterior painting, siding, trim, and fence staining.', 65.00, 'active'),
        (15, 9, 7, 'Residential Pest Control', 'Ant, roach, termite, and rodent control. Monthly plans available.', 70.00, 'active'),
        (16, 10, 6, 'Roof Leak Repair', 'Emergency and scheduled roof leak repair. Shingle replacement.', 95.00, 'active'),
        (17, 10, 6, 'Gutter Installation', 'New gutter installation, cleaning, and repair.', 85.00, 'active'),
    ]
    cur.executemany(
        """INSERT INTO service_listings
           (listing_id, provider_id, category_id, title, description, price, status)
           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        listings
    )
    print(f"  Inserted {len(listings)} listings")

    # ── LISTING IMAGES ──
    images = [
        (1, 1, 'https://picsum.photos/seed/plumb1/400/300'),
        (2, 3, 'https://picsum.photos/seed/elect1/400/300'),
        (3, 5, 'https://picsum.photos/seed/wood1/400/300'),
    ]
    cur.executemany(
        "INSERT INTO listing_images (image_id, listing_id, image_url) VALUES (%s,%s,%s)",
        images
    )
    print(f"  Inserted {len(images)} listing images")

    # ── JOB REQUESTS ──
    job_requests = [
        (1, 1, 'Water dripping under my kitchen sink and the cabinet floor is damp', 1, 'booked', '2026-04-08 09:00:00'),
        (2, 1, 'Outlet not working in the living room', 2, 'matched', '2026-04-09 14:00:00'),
        (3, 1, 'Window frame needs new weatherstripping', 4, 'closed', '2026-03-28 10:00:00'),
        (4, 8, 'AC unit blowing warm air even on max cool', 3, 'matched', '2026-04-05 11:00:00'),
        (5, 9, 'Ants everywhere in the kitchen need pest control', 7, 'booked', '2026-04-07 16:00:00'),
        (6, 13, 'Need to repaint my living room walls', 10, 'matched', '2026-04-10 09:00:00'),
    ]
    cur.executemany(
        """INSERT INTO job_requests
           (request_id, user_id, description, matched_category_id, status, created_at)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        job_requests
    )
    print(f"  Inserted {len(job_requests)} job requests")

    # ── BOOKINGS ──
    bookings = [
        (1, 1, 1, 'confirmed', '2026-04-12 10:00:00', 150.00),
        (2, 3, 3, 'completed', '2026-04-03 09:00:00', 130.00),
        (3, 5, 9, 'pending', '2026-04-14 13:00:00', 140.00),
        (4, 4, 7, 'pending', '2026-04-15 10:00:00', 160.00),
    ]
    cur.executemany(
        """INSERT INTO bookings
           (booking_id, request_id, provider_id, status, scheduled_date, total_price)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        bookings
    )
    print(f"  Inserted {len(bookings)} bookings")

    # ── REVIEWS ──
    reviews = [
        (1, 2, 5, 'James did amazing work on the weatherstripping. Arrived on time and cleaned up after. Highly recommend.', '2026-04-04 15:00:00'),
    ]
    cur.executemany(
        "INSERT INTO reviews (review_id, booking_id, rating, comment, created_at) VALUES (%s,%s,%s,%s,%s)",
        reviews
    )
    print(f"  Inserted {len(reviews)} reviews")

    # ── MESSAGES ──
    messages = [
        (1, 2, 1, 'Hi Jordan! I saw your request about the kitchen sink leak. Happy to come take a look.', '2026-04-08 10:14:00'),
        (2, 1, 2, 'Thanks Marcus! Yes it started 2 days ago. Water pooling under the cabinet.', '2026-04-08 10:18:00'),
        (3, 2, 1, 'Sounds like the P-trap or a compression fitting. Very common and usually a quick fix.', '2026-04-08 10:21:00'),
        (4, 1, 2, 'Great, when can you come out?', '2026-04-08 10:23:00'),
        (5, 2, 1, "I can come by Saturday at 10am. I'll bring parts for both common scenarios.", '2026-04-08 10:26:00'),
        (6, 3, 1, 'Hi! I can check your outlet issue. Does Thursday afternoon work?', '2026-04-09 15:00:00'),
        (7, 1, 3, 'Thursday afternoon works perfectly. See you then!', '2026-04-09 15:30:00'),
    ]
    cur.executemany(
        "INSERT INTO messages (message_id, sender_id, receiver_id, content, created_at) VALUES (%s,%s,%s,%s,%s)",
        messages
    )
    print(f"  Inserted {len(messages)} messages")

    conn.commit()
    cur.close()
    conn.close()
    print("\nDatabase seeded successfully!")


if __name__ == '__main__':
    print("Seeding taskmatch database...")
    try:
        seed()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
