--
-- 5 Лабораторна (збережені процедури, тригери)
--

-- 1. Створити збережену процедуру, яка покаже співробітників, в яких є активні контракти, але ще немає проведення публікації.
CREATE OR REPLACE FUNCTION unpub_info()
        RETURNS
        TABLE ("material_id" INT, "worker_id" INT, "last_changed_date" DATE)
        AS $$
        BEGIN
                RETURN QUERY
                        SELECT C.material_id, C.worker_id, C.last_changed_date FROM contract C
                        WHERE C.material_id NOT IN
                                (SELECT P.material_id FROM published_material P);
        END;
        $$ LANGUAGE plpgsql;
-- вивід
      unpub_info
----------------------
 (897,464,2024-02-01)
(1 row)

-- 2. Створити тригер, який буде змінювати previous_status на відповідний після зміни contract.
CREATE FUNCTION contract_data_change()
        RETURNS TRIGGER
        LANGUAGE PLPGSQL
        AS $$ BEGIN
                IF OLD.last_changed_date <> CURRENT_DATE THEN
                        UPDATE contract SET contract_status=3, previous_status=OLD.contract_status, last_changed_date = CURRENT_DATE WHERE contract_id=OLD.contract_id;
                END IF;
                RETURN NEW;
        END; $$;

CREATE TRIGGER contract_data_change_tg
        AFTER UPDATE ON contract
        FOR EACH ROW
        EXECUTE PROCEDURE contract_data_change()
        ;

-- результат роботи тригеру
publishing_house=# UPDATE contract SET planed_circulation=9011 WHERE material_id=196;
UPDATE 1
publishing_house=# SELECT * FROM contract;
 contract_id | worker_id | material_id | planed_circulation | contract_status | last_changed_date | previous_status
-------------+-----------+-------------+--------------------+-----------------+-------------------+-----------------
         305 |       277 |         821 |              10000 |               2 | 2021-11-10        | 1
         370 |       277 |         870 |               2000 |               2 | 2023-01-01        | 1
         332 |       277 |         832 |               1500 |               2 | 2023-02-01        | 1
         369 |       464 |         869 |                550 |               2 | 2023-03-01        | 1
         397 |       464 |         897 |               2000 |               2 | 2024-02-01        | 1
          23 |       464 |         196 |               9011 |               3 | 2024-02-13        | 2
(6 rows)

-- 3. Створити тригер, який буде змінювати contract_status на "завершено", коли після останньої зміни тиража він став >= запланованому.
CREATE FUNCTION contract_circ_update()
        RETURNS TRIGGER
        LANGUAGE PLPGSQL
        AS $$ BEGIN
                IF NEW.planed_circulation >= OLD.planed_circulation THEN
                        DELETE FROM contract WHERE contract_id=OLD.contract_id;
                        INSERT INTO contract
                                VALUES(OLD.contract_id, OLD.worker_id, OLD.material_id,
                                        NEW.planed_circulation, 3, CURRENT_DATE, OLD.contract_status);
                END IF;
                RETURN NEW;
        END; $$;

CREATE TRIGGER contract_circ_update_tg
        AFTER UPDATE ON contract
        FOR EACH ROW
        EXECUTE PROCEDURE contract_circ_update()
        ;
-- результат роботи
publishing_house=# UPDATE contract SET planed_circulation=551 WHERE contract_id=369;
UPDATE 1
publishing_house=# SELECT * FROM contract;

 contract_id | worker_id | material_id | planed_circulation | contract_status | last_changed_date | previous_status
-------------+-----------+-------------+--------------------+-----------------+-------------------+-----------------
          23 |       464 |         196 |               9102 |               1 | 2024-02-13        | 3
         370 |       277 |         870 |               2000 |               2 | 2023-01-01        | 1
         332 |       277 |         832 |               1500 |               2 | 2023-02-01        | 1
         305 |       277 |         821 |              10001 |               2 | 2021-11-10        | 1
         397 |       464 |         897 |               2000 |               2 | 2024-02-01        | 1
         369 |       464 |         869 |                551 |               3 | 2024-02-14        | 2
(6 rows)


-------------------------------------
--Тригер для автоматичного оновлення статусу клієнтів
CREATE OR REPLACE FUNCTION update_client_status() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.purchases >= 100 THEN
        NEW.status := 'vip';
    ELSIF NEW.purchases >= 10 THEN
        NEW.status := 'regular';
    ELSE
        NEW.status := 'new';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_client_status_trigger
BEFORE INSERT OR UPDATE ON client
FOR EACH ROW
EXECUTE FUNCTION update_client_status();

-- Тригер для запису логів при зміні статусу контракту

CREATE TABLE contract_status_log (
    log_id SERIAL PRIMARY KEY,
    contract_id INT NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION log_contract_status_change() RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO contract_status_log (contract_id, old_status, new_status)
        VALUES (OLD.contract_id, OLD.status, NEW.status);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER contract_status_log_trigger
AFTER UPDATE ON contract
FOR EACH ROW
EXECUTE FUNCTION log_contract_status_change();

--Процедура для отримання щомісячного звіту про публікації
CREATE OR REPLACE FUNCTION monthly_publication_report() RETURNS TABLE (
    title VARCHAR,
    author VARCHAR,
    circulation INT,
    publishing_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT M.title, M.author, P.circulation, P.publishing_date
    FROM material_info M
    INNER JOIN published_material P ON M.material_id = P.material_id
    WHERE P.publishing_date BETWEEN date_trunc('month', CURRENT_DATE) AND CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- Виклик процедури
SELECT * FROM monthly_publication_report();

-- Процедура для підрахунку загальної кількості замовлень на матеріали
CREATE OR REPLACE FUNCTION total_material_requests(material_id INT) RETURNS INT AS $$
DECLARE
    request_count INT;
BEGIN
    SELECT COUNT(*) INTO request_count
    FROM request
    WHERE request.material_id = material_id;
    RETURN request_count;
END;
$$ LANGUAGE plpgsql;

-- Виклик процедури
SELECT total_material_requests(821);

--Тригер для автоматичного встановлення дати публікації
CREATE OR REPLACE FUNCTION set_publishing_date() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.publishing_date IS NULL THEN
        NEW.publishing_date := CURRENT_DATE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_publishing_date_trigger
BEFORE INSERT ON published_material
FOR EACH ROW
EXECUTE FUNCTION set_publishing_date();




CREATE OR REPLACE FUNCTION get_active_users(period TEXT)
RETURNS TABLE (
    client_id INT,
    login VARCHAR,
    request_count INT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.client_id,
        c.login,
        COUNT(r.request_id) AS request_count
    FROM
        client c
        JOIN request r ON c.client_id = r.client_id
    -- WHERE
        -- (period = 'week' AND r.request_date >= CURRENT_DATE - INTERVAL '1 week')
        -- OR (period = 'month' AND r.request_date >= CURRENT_DATE - INTERVAL '1 month')
        -- OR (period = 'all' AND r.request_date >= '1970-01-01')
    GROUP BY c.client_id, c.login
    ORDER BY request_count DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;

