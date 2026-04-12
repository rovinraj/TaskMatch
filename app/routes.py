"""
routes.py — Every route for the TaskMatch / Fixr application.
"""

import os
from datetime import datetime
from functools import wraps

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    session, flash, jsonify, current_app,
)
from werkzeug.security import generate_password_hash, check_password_hash

from app import models
from app.db import query

bp = Blueprint("main", __name__)


# ──────────────────────────────────────────────
#  AUTH HELPERS
# ──────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    return decorated


def current_user():
    """Return the logged-in user dict or None."""
    uid = session.get("user_id")
    if uid:
        return models.get_user_by_id(uid)
    return None


# ──────────────────────────────────────────────
#  CONTEXT PROCESSOR — inject user into all templates
# ──────────────────────────────────────────────

@bp.app_context_processor
def inject_user():
    user = current_user()
    unread = 0
    if user:
        # count conversations with unread (simplified: count convos)
        convos = models.get_conversations(user["user_id"])
        unread = len(convos)
    return dict(current_user=user, unread_count=unread)


# ──────────────────────────────────────────────
#  HOME
# ──────────────────────────────────────────────

@bp.route("/")
def home():
    categories = models.get_all_categories()
    return render_template("home.html", categories=categories)


# ──────────────────────────────────────────────
#  AUTH — LOGIN
# ──────────────────────────────────────────────

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = models.get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid email or password.", "error")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("main.home"))


# ──────────────────────────────────────────────
#  AUTH — SIGN UP
# ──────────────────────────────────────────────

@bp.route("/signup", methods=["GET", "POST"])
def signup():
    categories = models.get_all_categories()

    if request.method == "POST":
        role = request.form.get("role", "client")
        first = request.form.get("first_name", "").strip()
        last = request.form.get("last_name", "").strip()
        name = f"{first} {last}"
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        city = request.form.get("city", "").strip()
        zip_code = request.form.get("zip_code", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        # Validation
        if not all([first, last, email, password]):
            flash("Please fill in all required fields.", "error")
            return render_template("signup.html", categories=categories)

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("signup.html", categories=categories)

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("signup.html", categories=categories)

        if models.get_user_by_email(email):
            flash("An account with that email already exists.", "error")
            return render_template("signup.html", categories=categories)

        pw_hash = generate_password_hash(password)
        user_id = models.create_user(name, email, phone, role, pw_hash)

        # Save location
        if city or zip_code:
            models.upsert_location(user_id, city, "", zip_code)

        # If provider, create profile
        if role == "provider":
            bio = request.form.get("bio", "")
            rate = request.form.get("rate", 0)
            try:
                rate = float(rate)
            except ValueError:
                rate = 0
            provider_id = models.create_provider_profile(user_id, bio, rate)

            # Create a default listing if category selected
            cat_name = request.form.get("primary_trade", "")
            if cat_name:
                cat = models.get_category_by_name(cat_name)
                if cat:
                    models.create_listing(
                        provider_id, cat["category_id"],
                        f"{cat_name} Services by {name}",
                        bio, rate,
                    )

        session["user_id"] = user_id
        session["user_name"] = name
        session["user_role"] = role
        flash("Account created! Welcome to Fixr.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("signup.html", categories=categories)


# ──────────────────────────────────────────────
#  DASHBOARD
# ──────────────────────────────────────────────

@bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    role = user["role"]

    if role == "provider":
        provider = models.get_provider_by_user(user["user_id"])
        bookings = models.get_bookings_by_provider(provider["provider_id"]) if provider else []
        listings = models.get_listings_by_provider(provider["provider_id"]) if provider else []
        return render_template("dashboard.html", user=user, bookings=bookings,
                               listings=listings, provider=provider)
    else:
        bookings = models.get_bookings_by_user(user["user_id"])
        job_requests = models.get_job_requests_by_user(user["user_id"])
        return render_template("dashboard.html", user=user, bookings=bookings,
                               job_requests=job_requests)


# ──────────────────────────────────────────────
#  SEARCH / CLASSIFY / RESULTS
# ──────────────────────────────────────────────

def classify_problem(description):
    """Use LLM to classify or fall back to keyword matching."""
    categories = models.get_all_categories()
    cat_names = [c["category_name"] for c in categories]

    # Try Gemini
    api_key = current_app.config.get("GEMINI_API_KEY", "")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""You are a classification engine for a home services marketplace.
Choose exactly one service category from SERVICE_CATEGORIES that best resolves the user's problem.
Output exactly one category name and nothing else.

SERVICE_CATEGORIES:
{', '.join(cat_names)}

USER_PROBLEM:
{description}

Return exactly one category from SERVICE_CATEGORIES and nothing else."""

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={"temperature": 0},
            )
            result = response.text.strip()
            if result in cat_names:
                return result
        except Exception as e:
            print(f"[LLM] Classification error: {e}")

    # Fallback: keyword matching
    desc_lower = description.lower()
    keyword_map = {
        "Plumbing": ["leak", "pipe", "drain", "faucet", "toilet", "sink", "water", "shower", "plumb"],
        "Electrical": ["outlet", "wire", "breaker", "switch", "light", "electric", "spark", "power"],
        "HVAC": ["ac", "air condition", "heat", "furnace", "thermostat", "hvac", "cool", "ventilat"],
        "Appliance Repair": ["washer", "dryer", "fridge", "refrigerator", "oven", "dishwasher", "appliance"],
        "Roofing": ["roof", "shingle", "gutter", "attic"],
        "Pest Control": ["ant", "roach", "termite", "pest", "mouse", "rat", "bug", "insect", "rodent"],
        "Handyman": ["shelf", "door", "mount", "install", "fix", "repair", "paint", "drywall"],
        "Landscaping": ["lawn", "garden", "tree", "yard", "landscap", "mow"],
        "Carpentry": ["wood", "cabinet", "carpent", "deck", "fence"],
        "Painting": ["paint", "stain", "primer", "wall color"],
    }
    for cat_name, keywords in keyword_map.items():
        for kw in keywords:
            if kw in desc_lower and cat_name in cat_names:
                return cat_name

    return cat_names[0] if cat_names else None


@bp.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        description = request.form.get("description", "").strip()
        zip_code = request.form.get("zip_code", "").strip()
        budget = request.form.get("budget", "").strip()

        if not description:
            flash("Please describe your problem.", "warning")
            return redirect(url_for("main.home"))

        # Classify
        matched_category_name = classify_problem(description)
        matched_cat = models.get_category_by_name(matched_category_name) if matched_category_name else None

        # Create job request if logged in
        job_request_id = None
        if "user_id" in session and matched_cat:
            job_request_id = models.create_job_request(
                session["user_id"], description, matched_cat["category_id"]
            )

        # Find providers
        providers = []
        if matched_cat:
            max_rate = None
            if budget:
                try:
                    max_rate = float(budget.replace("$", "").replace(",", "").strip())
                except ValueError:
                    pass
            providers = models.search_providers_by_category(
                matched_cat["category_id"],
                zip_code=zip_code or None,
                max_rate=max_rate,
            )
            # If no providers in exact zip, try without zip filter
            if not providers and zip_code:
                providers = models.search_providers_by_category(
                    matched_cat["category_id"], max_rate=max_rate,
                )

        # Get listings for each provider in this category
        for p in providers:
            p["listings"] = models.get_listings_by_provider(p["provider_id"])
            p["review_count"] = models.get_review_count_for_provider(p["provider_id"])
            p["initials"] = "".join([w[0].upper() for w in p["name"].split()[:2]])

        return render_template(
            "results.html",
            description=description,
            matched_category=matched_cat,
            providers=providers,
            zip_code=zip_code,
            budget=budget,
            job_request_id=job_request_id,
        )

    # GET — redirect to home
    return redirect(url_for("main.home"))


# ──────────────────────────────────────────────
#  PROVIDER PROFILE (public)
# ──────────────────────────────────────────────

@bp.route("/provider/<int:provider_id>")
def provider_profile(provider_id):
    provider = models.get_provider_full(provider_id)
    if not provider:
        flash("Provider not found.", "error")
        return redirect(url_for("main.home"))

    listings = models.get_listings_by_provider(provider_id)
    reviews = models.get_reviews_for_provider(provider_id)
    review_count = len(reviews)
    initials = "".join([w[0].upper() for w in provider["name"].split()[:2]])

    # get images for all listings
    for lst in listings:
        lst["images"] = models.get_images_for_listing(lst["listing_id"])

    return render_template(
        "provider_profile.html",
        provider=provider,
        listings=listings,
        reviews=reviews,
        review_count=review_count,
        initials=initials,
    )


# ──────────────────────────────────────────────
#  BOOKING
# ──────────────────────────────────────────────

@bp.route("/book/<int:provider_id>", methods=["GET", "POST"])
@login_required
def book(provider_id):
    provider = models.get_provider_full(provider_id)
    if not provider:
        flash("Provider not found.", "error")
        return redirect(url_for("main.home"))

    initials = "".join([w[0].upper() for w in provider["name"].split()[:2]])

    if request.method == "POST":
        scheduled_date = request.form.get("scheduled_date", "")
        scheduled_time = request.form.get("scheduled_time", "")
        description = request.form.get("description", "")
        total_price = request.form.get("total_price", "0")

        try:
            total_price = float(total_price.replace("$", "").replace(",", ""))
        except ValueError:
            total_price = 0

        # Parse date+time
        dt_str = f"{scheduled_date} {scheduled_time}"
        try:
            scheduled_dt = datetime.strptime(dt_str, "%Y-%m-%d %I:%M %p")
        except ValueError:
            try:
                scheduled_dt = datetime.strptime(scheduled_date, "%Y-%m-%d")
            except ValueError:
                scheduled_dt = datetime.now()

        # Find or create a job request
        request_id = request.form.get("request_id")
        if not request_id:
            # Classify and create
            cat_name = classify_problem(description) if description else None
            cat = models.get_category_by_name(cat_name) if cat_name else None
            cat_id = cat["category_id"] if cat else None
            request_id = models.create_job_request(
                session["user_id"], description or "Booking request", cat_id
            )

        booking_id = models.create_booking(
            int(request_id), provider_id, scheduled_dt, total_price
        )
        models.update_job_request_status(int(request_id), "booked")

        flash("Booking confirmed!", "success")
        return render_template(
            "booking.html",
            provider=provider,
            initials=initials,
            confirmed=True,
            booking_id=booking_id,
            scheduled_date=scheduled_dt.strftime("%a %b %d, %Y"),
            scheduled_time=scheduled_dt.strftime("%I:%M %p"),
        )

    # GET — show booking form
    request_id = request.args.get("request_id", "")
    return render_template(
        "booking.html",
        provider=provider,
        initials=initials,
        confirmed=False,
        request_id=request_id,
    )


# ──────────────────────────────────────────────
#  MESSAGES
# ──────────────────────────────────────────────

@bp.route("/messages")
@login_required
def messages():
    user = current_user()
    conversations = models.get_conversations(user["user_id"])
    return render_template("messages.html", conversations=conversations)


@bp.route("/messages/<int:partner_id>")
@login_required
def message_thread(partner_id):
    user = current_user()
    conversations = models.get_conversations(user["user_id"])
    thread = models.get_thread(user["user_id"], partner_id)
    partner = models.get_user_by_id(partner_id)
    return render_template(
        "messages.html",
        conversations=conversations,
        thread=thread,
        partner=partner,
    )


@bp.route("/api/messages/send", methods=["POST"])
@login_required
def api_send_message():
    data = request.get_json() or request.form
    receiver_id = data.get("receiver_id")
    content = data.get("content", "").strip()

    if not receiver_id or not content:
        return jsonify({"error": "Missing receiver or content"}), 400

    msg_id = models.send_message(session["user_id"], int(receiver_id), content)
    return jsonify({"message_id": msg_id, "status": "sent"})


# ──────────────────────────────────────────────
#  ACCOUNT
# ──────────────────────────────────────────────

@bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    user = current_user()
    location = models.get_location_by_user(user["user_id"])

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "update_profile":
            first = request.form.get("first_name", "").strip()
            last = request.form.get("last_name", "").strip()
            name = f"{first} {last}"
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            city = request.form.get("city", "").strip()
            zip_code = request.form.get("zip_code", "").strip()

            models.update_user(user["user_id"], name, email, phone)
            models.upsert_location(user["user_id"], city, "", zip_code)
            session["user_name"] = name
            flash("Profile updated.", "success")

        elif action == "update_password":
            current_pw = request.form.get("current_password", "")
            new_pw = request.form.get("new_password", "")
            confirm_pw = request.form.get("confirm_password", "")

            if not check_password_hash(user["password_hash"], current_pw):
                flash("Current password is incorrect.", "error")
            elif new_pw != confirm_pw:
                flash("New passwords do not match.", "error")
            elif len(new_pw) < 8:
                flash("Password must be at least 8 characters.", "error")
            else:
                models.update_user_password(user["user_id"], generate_password_hash(new_pw))
                flash("Password updated.", "success")

        return redirect(url_for("main.account"))

    return render_template("account.html", user=user, location=location)


# ──────────────────────────────────────────────
#  REVIEWS
# ──────────────────────────────────────────────

@bp.route("/review/<int:booking_id>", methods=["POST"])
@login_required
def submit_review(booking_id):
    booking = models.get_booking_by_id(booking_id)
    if not booking:
        flash("Booking not found.", "error")
        return redirect(url_for("main.dashboard"))

    rating = request.form.get("rating", 5)
    comment = request.form.get("comment", "").strip()

    try:
        rating = int(rating)
        rating = max(1, min(5, rating))
    except ValueError:
        rating = 5

    existing = models.get_review_by_booking(booking_id)
    if existing:
        flash("You already reviewed this booking.", "warning")
        return redirect(url_for("main.dashboard"))

    models.create_review(booking_id, rating, comment)
    models.recalc_provider_rating(booking["provider_id"])
    models.update_booking_status(booking_id, "completed")
    flash("Review submitted. Thank you!", "success")
    return redirect(url_for("main.provider_profile", provider_id=booking["provider_id"]))


@bp.route("/review/provider/<int:provider_id>", methods=["POST"])
@login_required
def submit_provider_review(provider_id):
    """Review from the provider profile page — finds the relevant booking."""
    rating = request.form.get("rating", 5)
    comment = request.form.get("comment", "").strip()

    try:
        rating = int(rating)
        rating = max(1, min(5, rating))
    except ValueError:
        rating = 5

    # Find a completed booking between this user and provider
    user_bookings = models.get_bookings_by_user(session["user_id"])
    target_booking = None
    for b in user_bookings:
        if b["provider_id"] == provider_id and not models.get_review_by_booking(b["booking_id"]):
            target_booking = b
            break

    if not target_booking:
        flash("No eligible booking found to review.", "warning")
        return redirect(url_for("main.provider_profile", provider_id=provider_id))

    models.create_review(target_booking["booking_id"], rating, comment)
    models.recalc_provider_rating(provider_id)
    flash("Review submitted. Thank you!", "success")
    return redirect(url_for("main.provider_profile", provider_id=provider_id))


# ──────────────────────────────────────────────
#  PROVIDER LISTINGS MANAGEMENT
# ──────────────────────────────────────────────

@bp.route("/listings/new", methods=["GET", "POST"])
@login_required
def new_listing():
    user = current_user()
    if user["role"] != "provider":
        flash("Only providers can create listings.", "warning")
        return redirect(url_for("main.dashboard"))

    provider = models.get_provider_by_user(user["user_id"])
    categories = models.get_all_categories()

    if request.method == "POST":
        category_id = request.form.get("category_id")
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", "0")
        try:
            price = float(price)
        except ValueError:
            price = 0

        models.create_listing(provider["provider_id"], int(category_id), title, description, price)
        flash("Listing created!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("new_listing.html", categories=categories)


@bp.route("/listings/<int:listing_id>/edit", methods=["POST"])
@login_required
def edit_listing(listing_id):
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    price = request.form.get("price", "0")
    status = request.form.get("status", "active")
    try:
        price = float(price)
    except ValueError:
        price = 0
    models.update_listing(listing_id, title, description, price, status)
    flash("Listing updated.", "success")
    return redirect(url_for("main.dashboard"))


@bp.route("/listings/<int:listing_id>/delete", methods=["POST"])
@login_required
def delete_listing_route(listing_id):
    models.delete_listing(listing_id)
    flash("Listing deleted.", "success")
    return redirect(url_for("main.dashboard"))


# ──────────────────────────────────────────────
#  BOOKING STATUS (for providers)
# ──────────────────────────────────────────────

@bp.route("/booking/<int:booking_id>/status", methods=["POST"])
@login_required
def update_booking(booking_id):
    status = request.form.get("status", "")
    if status in ("confirmed", "in_progress", "completed", "cancelled"):
        models.update_booking_status(booking_id, status)
        flash(f"Booking status updated to {status}.", "success")
    return redirect(url_for("main.dashboard"))


# ──────────────────────────────────────────────
#  DELETE ACCOUNT
# ──────────────────────────────────────────────

@bp.route("/account/delete", methods=["POST"])
@login_required
def delete_account():
    models.delete_user(session["user_id"])
    session.clear()
    flash("Account deleted.", "info")
    return redirect(url_for("main.home"))
