DROP DATABASE IF EXISTS taskmatch;
CREATE DATABASE taskmatch CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE taskmatch;

CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) DEFAULT NULL,
    role ENUM('client','provider','admin') NOT NULL DEFAULT 'client',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
);

CREATE TABLE locations (
    location_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    city VARCHAR(100) DEFAULT NULL,
    state VARCHAR(50) DEFAULT NULL,
    zip_code VARCHAR(10) DEFAULT NULL,
    PRIMARY KEY (location_id),
    UNIQUE KEY uq_user_location (user_id),
    CONSTRAINT fk_loc_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE service_categories (
    category_id INT NOT NULL AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    PRIMARY KEY (category_id)
);

CREATE TABLE provider_profiles (
    provider_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    bio TEXT DEFAULT NULL,
    rate DECIMAL(8,2) DEFAULT NULL,
    verified_status BOOLEAN NOT NULL DEFAULT FALSE,
    average_rating DECIMAL(3,2) DEFAULT NULL,
    PRIMARY KEY (provider_id),
    UNIQUE KEY uq_provider_user (user_id),
    CONSTRAINT fk_pp_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE service_listings (
    listing_id INT NOT NULL AUTO_INCREMENT,
    provider_id INT NOT NULL,
    category_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT DEFAULT NULL,
    price DECIMAL(8,2) DEFAULT NULL,
    status ENUM('active','inactive','pending') NOT NULL DEFAULT 'active',
    PRIMARY KEY (listing_id),
    CONSTRAINT fk_sl_provider
        FOREIGN KEY (provider_id) REFERENCES provider_profiles(provider_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_sl_category
        FOREIGN KEY (category_id) REFERENCES service_categories(category_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE listing_images (
    image_id INT NOT NULL AUTO_INCREMENT,
    listing_id INT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    PRIMARY KEY (image_id),
    CONSTRAINT fk_li_listing
        FOREIGN KEY (listing_id) REFERENCES service_listings(listing_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE job_requests (
    request_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    description TEXT NOT NULL,
    matched_category_id INT DEFAULT NULL,
    status ENUM('open','matched','booked','closed','cancelled') NOT NULL DEFAULT 'open',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (request_id),
    CONSTRAINT fk_jr_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_jr_category
        FOREIGN KEY (matched_category_id) REFERENCES service_categories(category_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE bookings (
    booking_id INT NOT NULL AUTO_INCREMENT,
    request_id INT NOT NULL,
    provider_id INT NOT NULL,
    status ENUM('pending','confirmed','in_progress','completed','cancelled') NOT NULL DEFAULT 'pending',
    scheduled_date TIMESTAMP NULL DEFAULT NULL,
    total_price DECIMAL(10,2) DEFAULT NULL,
    PRIMARY KEY (booking_id),
    CONSTRAINT fk_bk_request
        FOREIGN KEY (request_id) REFERENCES job_requests(request_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_bk_provider
        FOREIGN KEY (provider_id) REFERENCES provider_profiles(provider_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE reviews (
    review_id INT NOT NULL AUTO_INCREMENT,
    booking_id INT NOT NULL,
    rating TINYINT NOT NULL,
    comment TEXT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (review_id),
    UNIQUE KEY uq_review_booking (booking_id),
    CONSTRAINT fk_rv_booking
        FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT chk_review_rating CHECK (rating BETWEEN 1 AND 5)
);

CREATE TABLE messages (
    message_id INT NOT NULL AUTO_INCREMENT,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (message_id),
    CONSTRAINT fk_msg_sender
        FOREIGN KEY (sender_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_msg_receiver
        FOREIGN KEY (receiver_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);