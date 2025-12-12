CREATE TABLE auth_info (
  login VARCHAR(16) PRIMARY KEY,
  first_name VARCHAR(16) NOT NULL,
  last_name VARCHAR(16),
  phone_number VARCHAR(15) UNIQUE CHECK(phone_number ~ '^\d{3}\s?\d{3}\s?\d{4}$'),
  birthday DATE NOT NULL CHECK( birthday <= CURRENT_DATE - INTERVAL '16 years')
);

CREATE OR REPLACE FUNCTION is_valid_phone_number(phone TEXT) RETURNS BOOLEAN AS $
BEGIN
    RETURN (phone ~ '^(\[0-9]{3,14}))

CREATE TABLE worker (
  worker_id SERIAL PRIMARY KEY,
  login VARCHAR UNIQUE,
  position worker_position NOT NULL,
  status worker_status NOT NULL
);

CREATE TABLE client (
  client_id SERIAL PRIMARY KEY,
  login VARCHAR(16) UNIQUE,
  purchases INT,
  status client_status NOT NULL
);

CREATE TABLE material_info (
  material_id SERIAL PRIMARY KEY,
  title VARCHAR(60) NOT NULL,
  author VARCHAR(30) NOT NULL,
  genre material_genre NOT NULL,
  form  material_form NOT NULL,
  age_restriction INT NOT NULL
);

CREATE TABLE request (
  request_id SERIAL PRIMARY KEY,
  client_id INT NOT NULL,
  title VARCHAR(60) NOT NULL,
  author VARCHAR(60) NOT NULL,
  status request_status NOT NULL,
  request_date DATE NOT NULL,
  comment VARCHAR(300)
);

CREATE TABLE contract (
  contract_id SERIAL PRIMARY KEY,
  worker_id INT NOT NULL,
  material_id INT NOT NULL,
  planed_circulation INT NOT NULL,
  status contract_status NOT NULL,
  last_changed_date DATE NOT NULL,
  previous_status contract_status
);

CREATE TABLE published_material (
  published_material_id SERIAL PRIMARY KEY,
  material_id INT NOT NULL,
  circulation INT NOT NULL,
  publishing_date DATE NOT NULL CHECK(publishing_date <= CURRENT_DATE),
  responsible_worker INT NOT NULL
);


ALTER TABLE worker
-- ADD FOREIGN KEY (position) REFERENCES position (position_id) ON DELETE CASCADE ON UPDATE CASCADE,
ADD FOREIGN KEY (login) REFERENCES auth_info (login) ON DELETE CASCADE ON UPDATE CASCADE;
-- ADD FOREIGN KEY (worker_status) REFERENCES worker_status (worker_status_id) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE request
-- ADD FOREIGN KEY (request_status) REFERENCES request_status (request_status_id) ON DELETE CASCADE ON UPDATE CASCADE,
-- ADD FOREIGN KEY (material_id) REFERENCES material_info (material_id) ON DELETE CASCADE ON UPDATE CASCADE,
ADD FOREIGN KEY (client_id) REFERENCES client (client_id) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE contract
ADD FOREIGN KEY (material_id) REFERENCES material_info (material_id) ON DELETE CASCADE ON UPDATE CASCADE,
ADD FOREIGN KEY (worker_id) REFERENCES worker (worker_id) ON DELETE CASCADE ON UPDATE CASCADE;
-- ADD FOREIGN KEY (contract_status) REFERENCES contract_status (contract_status_id) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE client
ADD FOREIGN KEY (login) REFERENCES auth_info (login) ON DELETE CASCADE ON UPDATE CASCADE;
-- ADD FOREIGN KEY (client_status) REFERENCES client_status (client_status_id) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE published_material
ADD FOREIGN KEY (responsible_worker) REFERENCES worker (worker_id) ON DELETE CASCADE ON UPDATE CASCADE,
ADD FOREIGN KEY (material_id) REFERENCES material_info (material_id) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE material_info
-- ADD FOREIGN KEY (form) REFERENCES material_form (form_id) ON DELETE CASCADE ON UPDATE CASCADE,
-- ADD FOREIGN KEY (genre) REFERENCES material_genre (genre_id) ON DELETE CASCADE ON UPDATE CASCADE;

