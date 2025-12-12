-- удалил каскад материал_инфо

INSERT INTO auth_info (login, first_name, last_name, phone_number, birthday)
VALUES  ('director', 'John', 'Frog', '0987654321', '01.01.1980'),
        ('admin', 'Michael', 'Squaer', '0934654321', '04.02.1995'),
        ('admin_2', 'Jacob', 'Johnson', '0934643141', '12.11.1994'),
        ('editor', 'Chistopher', 'Baum', '0954351221', '06.01.2000'),
        ('user999', 'Friedrich', 'Wabetailung', '0998543321', '08.09.1997'),
        ('acdc02', 'Claus', 'Landzung', '0933622111', '06.04.1994'),
        ('03doe80', 'Leonardo', 'Dolchdose', '0967754988', '01.11.2001');

-- INSERT INTO position (position_id, position_name)
-- VALUES  (1, 'director'),
        -- (2, 'administrator'),
        -- (3, 'editor');
-- 01.06 changed to
-- publishing_house=# CREATE TYPE worker_position AS ENUM ('director', 'administrator', 'editor');

-- INSERT INTO worker_status (worker_status_id, worker_status_name)
-- VALUES  (1, 'works'),
        -- (2, 'on_leave'),
        -- (3, 'fired');
-- 01.06 changed to
-- publishing_house=# CREATE TYPE worker_status AS ENUM ('works', 'on_leave', 'fired');


-- TODO edit next worker_id
INSERT INTO worker (login, position, status)
VALUES  ('director', 'director', 'works'),
        ('admin', 'administrator', 'works'),
        ('admin_2', 'administrator', 'on_leave'),
        ('editor', 'editor', 'works');

-- INSERT INTO client_status (client_status_id, client_status_name)
-- VALUES  (1, 'new'),
        -- (2, 'regular'),
        -- (3, 'vip');

INSERT INTO client (client_id, login, purchases, status)
VALUES  (543, 'user999', 7, 'regular'),
        (654, 'acdc02', 2, 'new'),
        (841, '03doe80', 20, 'vip');

-- INSERT INTO material_genre (genre_id, genre)
-- VALUES  (1, 'fiction'),
        -- (2, 'romance'),
        -- (3, 'scifiction'),
        -- (4, 'detective'),
        -- (5, 'adventure'),
        -- (6, 'for children'),
        -- (7, 'history'),
        -- (8, 'educational'),
        -- (9, 'news'),
        -- (10, 'magazine');

-- INSERT INTO material_form (form_id, form)
-- VALUES  (1, 'paper book'),
        -- (2, 'electronic book'),
        -- (3, 'audio book'),
        -- (4, 'news'),
        -- (5, 'magazine');

INSERT INTO material_info (title, author, genre, form, age_restriction)
VALUES  ('The Lord of the rings', 'Tolkien J.R.R', 'adventure', 'paper book', 12),
        ('Scaramouche', 'Sabatini R.', 'romance', 'electronic book', 16),
        ('Alica adventures in the Wonderland', 'Carroll L.', 'for children', 'audio book', 10),
        ('Ulysses', 'Joyce J.', 'romance', 'paper book', 16),
        ('Just for fun', 'Torvalds L.', 'history', 'electronic book', 12),
        ('News magazine for 2022', 'Hersh S.', 'magazine', 'magazine', 12),
        ('Database lection course', 'Malahov E.V.', 'educational', 'electronic book', 16);

-- INSERT INTO request_status (request_status_id, request_status_name) -- VALUES  (1, 'processing'),
        -- (2, 'accepted'),
        -- (3, 'canceled');

INSERT INTO request (request_id, client_id, material_id, status, comment)
VALUES  (37, 654, 821, 'processing', NULL),
        (739, 654, 821, 'annuled', 'now publishing house can not accept this reques'),
        (740, 841, 821, 'processing', NULL),
        (738, 654, 832, 'accepted', NULL),
        (741, 654, 832, 'processing', NULL),
        (742, 841, 832, 'processing', NULL),
        (743, 654, 56, 'processing', 'very useful book'),
        (423, 654, 056, 'annuled', 'the material does not suit the organisation thematic');

INSERT INTO request (client_id, title, author, status, request_date, comment)
VALUES  (654, 'Три мушкетери', 'Олександр Дюма', 'processing', 06.03.2023, NULL),

-- INSERT INTO contract_status (contract_status_id, contract_status_name)
-- VALUES  (1, 'processing'),
        -- (2, 'to print'),
        -- (3, 'annuled');
        -- (4, 'printed'),

INSERT INTO contract (contract_id, worker_id, material_id, planed_circulation, status, last_changed_date, previous_status)
VALUES  (305, 277, 821, 10000, 'to print', '11.10.2021', 'processing'),
        (23, 464, 196, 9000, 'to print', '08.20.2023', 'processing');

INSERT INTO published_material (material_id, circulation, publishing_date, responsible_worker)
VALUES  (821, 5000, '01.11.2022', 464),
        (196, 9000, '09.01.2023', 277);

