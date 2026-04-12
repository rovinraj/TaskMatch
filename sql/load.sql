USE taskmatch;

SET FOREIGN_KEY_CHECKS = 0;

LOAD DATA LOCAL INFILE 'data/users.csv'
INTO TABLE users
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(user_id, name, email, phone, role, created_at);

LOAD DATA LOCAL INFILE 'data/locations.csv'
INTO TABLE locations
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(location_id, user_id, city, state, zip_code);

LOAD DATA LOCAL INFILE 'data/service_categories.csv'
INTO TABLE service_categories
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(category_id, category_name);

LOAD DATA LOCAL INFILE 'data/provider_profiles.csv'
INTO TABLE provider_profiles
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(provider_id, user_id, bio, rate, verified_status, average_rating);

LOAD DATA LOCAL INFILE 'data/service_listings.csv'
INTO TABLE service_listings
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(listing_id, provider_id, category_id, title, description, price, status);

LOAD DATA LOCAL INFILE 'data/listing_images.csv'
INTO TABLE listing_images
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(image_id, listing_id, image_url);

LOAD DATA LOCAL INFILE 'data/job_requests.csv'
INTO TABLE job_requests
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(request_id, user_id, description, @matched_category_id, status, created_at)
SET matched_category_id = NULLIF(@matched_category_id, '');

LOAD DATA LOCAL INFILE 'data/bookings.csv'
INTO TABLE bookings
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(booking_id, request_id, provider_id, status, @scheduled_date, @total_price)
SET scheduled_date = NULLIF(@scheduled_date, ''),
    total_price = NULLIF(@total_price, '');

LOAD DATA LOCAL INFILE 'data/reviews.csv'
INTO TABLE reviews
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(review_id, booking_id, rating, comment, created_at);

LOAD DATA LOCAL INFILE 'data/messages.csv'
INTO TABLE messages
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(message_id, sender_id, receiver_id, content, created_at);

SET FOREIGN_KEY_CHECKS = 1;