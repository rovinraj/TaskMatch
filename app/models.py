"""
models.py — Data-access functions for every TaskMatch table.
All functions use app.db.query / app.db.execute.
"""

from app.db import query, execute


# ──────────────────────────────────────────────
#  USERS
# ──────────────────────────────────────────────

def get_user_by_id(user_id):
    return query("SELECT * FROM users WHERE user_id = %s", (user_id,), one=True)


def get_user_by_email(email):
    return query("SELECT * FROM users WHERE email = %s", (email,), one=True)


def create_user(name, email, phone, role, password_hash):
    return execute(
        """INSERT INTO users (name, email, phone, role, password_hash)
           VALUES (%s, %s, %s, %s, %s)""",
        (name, email, phone, role, password_hash),
    )


def update_user(user_id, name, email, phone):
    return execute(
        """UPDATE users SET name=%s, email=%s, phone=%s WHERE user_id=%s""",
        (name, email, phone, user_id),
    )


def update_user_password(user_id, password_hash):
    return execute(
        "UPDATE users SET password_hash=%s WHERE user_id=%s",
        (password_hash, user_id),
    )


def delete_user(user_id):
    return execute("DELETE FROM users WHERE user_id=%s", (user_id,))


# ──────────────────────────────────────────────
#  LOCATIONS
# ──────────────────────────────────────────────

def get_location_by_user(user_id):
    return query("SELECT * FROM locations WHERE user_id = %s", (user_id,), one=True)


def upsert_location(user_id, city, state, zip_code):
    existing = get_location_by_user(user_id)
    if existing:
        return execute(
            "UPDATE locations SET city=%s, state=%s, zip_code=%s WHERE user_id=%s",
            (city, state, zip_code, user_id),
        )
    return execute(
        "INSERT INTO locations (user_id, city, state, zip_code) VALUES (%s,%s,%s,%s)",
        (user_id, city, state, zip_code),
    )


# ──────────────────────────────────────────────
#  SERVICE CATEGORIES
# ──────────────────────────────────────────────

def get_all_categories():
    return query("SELECT * FROM service_categories ORDER BY category_name")


def get_category_by_id(category_id):
    return query("SELECT * FROM service_categories WHERE category_id=%s", (category_id,), one=True)


def get_category_by_name(name):
    return query("SELECT * FROM service_categories WHERE category_name=%s", (name,), one=True)


# ──────────────────────────────────────────────
#  PROVIDER PROFILES
# ──────────────────────────────────────────────

def get_provider_by_user(user_id):
    return query("SELECT * FROM provider_profiles WHERE user_id=%s", (user_id,), one=True)


def get_provider_by_id(provider_id):
    return query("SELECT * FROM provider_profiles WHERE provider_id=%s", (provider_id,), one=True)


def create_provider_profile(user_id, bio, rate):
    return execute(
        """INSERT INTO provider_profiles (user_id, bio, rate, verified_status, average_rating)
           VALUES (%s, %s, %s, FALSE, NULL)""",
        (user_id, bio, rate),
    )


def update_provider_profile(provider_id, bio, rate):
    return execute(
        "UPDATE provider_profiles SET bio=%s, rate=%s WHERE provider_id=%s",
        (bio, rate, provider_id),
    )


def get_provider_full(provider_id):
    """Provider joined with user + location info."""
    return query(
        """SELECT pp.*, u.name, u.email, u.phone,
                  l.city, l.state, l.zip_code
           FROM provider_profiles pp
           JOIN users u ON pp.user_id = u.user_id
           LEFT JOIN locations l ON u.user_id = l.user_id
           WHERE pp.provider_id = %s""",
        (provider_id,),
        one=True,
    )


def search_providers_by_category(category_id, zip_code=None, max_rate=None, min_rating=None):
    """Find providers who have active listings in a category."""
    sql = """
        SELECT DISTINCT pp.provider_id, pp.bio, pp.rate, pp.verified_status,
               pp.average_rating, u.name, u.email, u.phone,
               l.city, l.state, l.zip_code
        FROM provider_profiles pp
        JOIN users u ON pp.user_id = u.user_id
        LEFT JOIN locations l ON u.user_id = l.user_id
        JOIN service_listings sl ON pp.provider_id = sl.provider_id
        WHERE sl.category_id = %s AND sl.status = 'active'
    """
    params = [category_id]

    if zip_code:
        sql += " AND l.zip_code = %s"
        params.append(zip_code)
    if max_rate:
        sql += " AND pp.rate <= %s"
        params.append(max_rate)
    if min_rating:
        sql += " AND pp.average_rating >= %s"
        params.append(min_rating)

    sql += " ORDER BY pp.average_rating DESC, pp.rate ASC"
    return query(sql, tuple(params))


def recalc_provider_rating(provider_id):
    """Recalculate average_rating from reviews table."""
    row = query(
        """SELECT AVG(r.rating) AS avg_r
           FROM reviews r
           JOIN bookings b ON r.booking_id = b.booking_id
           WHERE b.provider_id = %s""",
        (provider_id,),
        one=True,
    )
    avg = row["avg_r"] if row and row["avg_r"] else None
    execute(
        "UPDATE provider_profiles SET average_rating=%s WHERE provider_id=%s",
        (avg, provider_id),
    )
    return avg


# ──────────────────────────────────────────────
#  SERVICE LISTINGS
# ──────────────────────────────────────────────

def get_listings_by_provider(provider_id):
    return query(
        """SELECT sl.*, sc.category_name
           FROM service_listings sl
           JOIN service_categories sc ON sl.category_id = sc.category_id
           WHERE sl.provider_id = %s
           ORDER BY sl.listing_id DESC""",
        (provider_id,),
    )


def get_listing_by_id(listing_id):
    return query(
        """SELECT sl.*, sc.category_name
           FROM service_listings sl
           JOIN service_categories sc ON sl.category_id = sc.category_id
           WHERE sl.listing_id = %s""",
        (listing_id,),
        one=True,
    )


def create_listing(provider_id, category_id, title, description, price):
    return execute(
        """INSERT INTO service_listings (provider_id, category_id, title, description, price, status)
           VALUES (%s,%s,%s,%s,%s,'active')""",
        (provider_id, category_id, title, description, price),
    )


def update_listing(listing_id, title, description, price, status):
    return execute(
        """UPDATE service_listings SET title=%s, description=%s, price=%s, status=%s
           WHERE listing_id=%s""",
        (title, description, price, status, listing_id),
    )


def delete_listing(listing_id):
    return execute("DELETE FROM service_listings WHERE listing_id=%s", (listing_id,))


# ──────────────────────────────────────────────
#  LISTING IMAGES
# ──────────────────────────────────────────────

def get_images_for_listing(listing_id):
    return query("SELECT * FROM listing_images WHERE listing_id=%s", (listing_id,))


def add_listing_image(listing_id, image_url):
    return execute(
        "INSERT INTO listing_images (listing_id, image_url) VALUES (%s,%s)",
        (listing_id, image_url),
    )


# ──────────────────────────────────────────────
#  JOB REQUESTS
# ──────────────────────────────────────────────

def create_job_request(user_id, description, matched_category_id=None):
    return execute(
        """INSERT INTO job_requests (user_id, description, matched_category_id, status)
           VALUES (%s, %s, %s, 'open')""",
        (user_id, description, matched_category_id),
    )


def get_job_requests_by_user(user_id):
    return query(
        """SELECT jr.*, sc.category_name
           FROM job_requests jr
           LEFT JOIN service_categories sc ON jr.matched_category_id = sc.category_id
           WHERE jr.user_id = %s
           ORDER BY jr.created_at DESC""",
        (user_id,),
    )


def get_job_request_by_id(request_id):
    return query(
        """SELECT jr.*, sc.category_name
           FROM job_requests jr
           LEFT JOIN service_categories sc ON jr.matched_category_id = sc.category_id
           WHERE jr.request_id = %s""",
        (request_id,),
        one=True,
    )


def update_job_request_status(request_id, status):
    return execute(
        "UPDATE job_requests SET status=%s WHERE request_id=%s",
        (status, request_id),
    )


def update_job_request_category(request_id, category_id):
    return execute(
        "UPDATE job_requests SET matched_category_id=%s, status='matched' WHERE request_id=%s",
        (category_id, request_id),
    )


# ──────────────────────────────────────────────
#  BOOKINGS
# ──────────────────────────────────────────────

def create_booking(request_id, provider_id, scheduled_date, total_price):
    return execute(
        """INSERT INTO bookings (request_id, provider_id, status, scheduled_date, total_price)
           VALUES (%s, %s, 'pending', %s, %s)""",
        (request_id, provider_id, scheduled_date, total_price),
    )


def get_bookings_by_user(user_id):
    """Bookings for a client (via their job requests)."""
    return query(
        """SELECT b.*, jr.description AS job_desc, jr.user_id,
                  u.name AS provider_name, sc.category_name
           FROM bookings b
           JOIN job_requests jr ON b.request_id = jr.request_id
           JOIN provider_profiles pp ON b.provider_id = pp.provider_id
           JOIN users u ON pp.user_id = u.user_id
           LEFT JOIN service_categories sc ON jr.matched_category_id = sc.category_id
           WHERE jr.user_id = %s
           ORDER BY b.scheduled_date DESC""",
        (user_id,),
    )


def get_bookings_by_provider(provider_id):
    """Bookings assigned to a provider."""
    return query(
        """SELECT b.*, jr.description AS job_desc,
                  u.name AS client_name, sc.category_name
           FROM bookings b
           JOIN job_requests jr ON b.request_id = jr.request_id
           JOIN users u ON jr.user_id = u.user_id
           LEFT JOIN service_categories sc ON jr.matched_category_id = sc.category_id
           WHERE b.provider_id = %s
           ORDER BY b.scheduled_date DESC""",
        (provider_id,),
    )


def get_booking_by_id(booking_id):
    return query(
        """SELECT b.*, jr.description AS job_desc, jr.user_id AS client_user_id,
                  pp.user_id AS provider_user_id,
                  cu.name AS client_name, pu.name AS provider_name,
                  sc.category_name
           FROM bookings b
           JOIN job_requests jr ON b.request_id = jr.request_id
           JOIN provider_profiles pp ON b.provider_id = pp.provider_id
           JOIN users cu ON jr.user_id = cu.user_id
           JOIN users pu ON pp.user_id = pu.user_id
           LEFT JOIN service_categories sc ON jr.matched_category_id = sc.category_id
           WHERE b.booking_id = %s""",
        (booking_id,),
        one=True,
    )


def update_booking_status(booking_id, status):
    return execute(
        "UPDATE bookings SET status=%s WHERE booking_id=%s",
        (status, booking_id),
    )


# ──────────────────────────────────────────────
#  REVIEWS
# ──────────────────────────────────────────────

def create_review(booking_id, rating, comment):
    return execute(
        "INSERT INTO reviews (booking_id, rating, comment) VALUES (%s,%s,%s)",
        (booking_id, rating, comment),
    )


def get_review_by_booking(booking_id):
    return query("SELECT * FROM reviews WHERE booking_id=%s", (booking_id,), one=True)


def get_reviews_for_provider(provider_id):
    return query(
        """SELECT r.*, b.booking_id, u.name AS reviewer_name
           FROM reviews r
           JOIN bookings b ON r.booking_id = b.booking_id
           JOIN job_requests jr ON b.request_id = jr.request_id
           JOIN users u ON jr.user_id = u.user_id
           WHERE b.provider_id = %s
           ORDER BY r.created_at DESC""",
        (provider_id,),
    )


def get_review_count_for_provider(provider_id):
    row = query(
        """SELECT COUNT(*) AS cnt
           FROM reviews r JOIN bookings b ON r.booking_id = b.booking_id
           WHERE b.provider_id = %s""",
        (provider_id,),
        one=True,
    )
    return row["cnt"] if row else 0


# ──────────────────────────────────────────────
#  MESSAGES
# ──────────────────────────────────────────────

def send_message(sender_id, receiver_id, content):
    return execute(
        "INSERT INTO messages (sender_id, receiver_id, content) VALUES (%s,%s,%s)",
        (sender_id, receiver_id, content),
    )


def get_conversations(user_id):
    """Get the latest message per conversation partner."""
    return query(
        """SELECT m.*, u.name AS partner_name,
                  SUBSTRING(u.name, 1, 1) AS initial1,
                  SUBSTRING(SUBSTRING_INDEX(u.name, ' ', -1), 1, 1) AS initial2
           FROM messages m
           JOIN users u ON u.user_id = IF(m.sender_id = %s, m.receiver_id, m.sender_id)
           WHERE m.message_id IN (
               SELECT MAX(message_id)
               FROM messages
               WHERE sender_id = %s OR receiver_id = %s
               GROUP BY LEAST(sender_id, receiver_id), GREATEST(sender_id, receiver_id)
           )
           ORDER BY m.created_at DESC""",
        (user_id, user_id, user_id),
    )


def get_thread(user_id, partner_id):
    """All messages between two users, oldest first."""
    return query(
        """SELECT m.*, u.name AS sender_name
           FROM messages m
           JOIN users u ON m.sender_id = u.user_id
           WHERE (m.sender_id = %s AND m.receiver_id = %s)
              OR (m.sender_id = %s AND m.receiver_id = %s)
           ORDER BY m.created_at ASC""",
        (user_id, partner_id, partner_id, user_id),
    )
