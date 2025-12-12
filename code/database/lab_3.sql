--
-- 3 Лабораторна (запити)
--

-- 1.Показати 3 найпопулярніші матеріали за кількістю запитів.
SELECT R.material_id, title, COUNT(R.material_id) reqest_count
FROM request R INNER JOIN material_info M ON R.material_id=M.material_id
GROUP BY R.material_id, title
ORDER BY R.material_id DESC
LIMIT 3;
-- Вивід
 material_id |               title                | reqest_count
-------------+------------------------------------+--------------
         832 | Alica adventures in the Wonderland |            3
         821 | The Lord of the rings              |            3
          56 | Database lection course            |            1
(3 rows)

------------
SELECT
        M.material_id, R.title, COUNT(R.title) request_count
FROM
        request R JOIN material_info M ON M.title=R.title
GROUP BY M.material_id, R.title
ORDER BY M.material_id DESC
LIMIT 10;

------------

-- 2.Показати всіх працівників, згрупувавши їх по позиції, яким від 18 до 21
-- років.  (З вашого дозволу, збільшу діапазон до 25 років)
SELECT P.position_name, A.last_name, A.first_name, AGE(A.birthday) age
FROM worker W
INNER JOIN auth_info A
ON W.login=A.login
INNER JOIN position P
ON W.position=P.position_id
WHERE birthday>'1998-01-01'
GROUP BY P.position_name, last_name, first_name, age;
-- Вивід
 position_name | last_name | first_name |           age
---------------+-----------+------------+-------------------------
 Editor        | Baum      | Chistopher | 23 years 7 mons 29 days
 Editor        | Dubov     | Viktor     | 22 years 28 days
(2 rows)

-- Покати 3 жанри, кількість матеріалів якого найбільша.
SELECT M.genre, COUNT(M.genre) genre_count
FROM material_info M
INNER JOIN material_genre G
ON M.genre=G.genre_id
GROUP BY M.genre
ORDER BY genre_count DESC
LIMIT 3;
-- Вивід
 genre | genre_count
-------+-------------
     6 |           2
     2 |           2
     5 |           1
(3 rows)

-- 4.Показати працівників які на поточний момент займаються публікацією якогось
-- матеріалу.
SELECT responsible_worker, published_material_id, publishing_date
FROM published_material INNER JOIN worker W ON responsible_worker=worker_id;
-- Вивід
 responsible_worker | published_material_id | publishing_date
--------------------+-----------------------+-----------------
                464 |                   537 | 2022-01-11
                277 |                   641 | 2023-09-01
(2 rows)


-- 5.Показати контракти, які були створені більше ніж 1 день назад і в яких
-- запланований тираж перевищує на 15% фактичний тираж на поточний момент.
SELECT C.material_id, AGE(last_changed_date) contract_age, planed_circulation,
circulation, (planed_circulation-circulation)*100/planed_circulation circ_percent
FROM contract C
INNER JOIN published_material P ON C.material_id=P.material_id
WHERE last_changed_date<CURRENT_DATE AND (planed_circulation-circulation)*100/planed_circulation >=15;
-- Вивід
 material_id |      contract_age      | planed_circulation | circulation | circ_percent
-------------+------------------------+--------------------+-------------+--------------
         821 | 2 years 2 mons 21 days |              10000 |        5000 |           50
(1 row)

-- 6.Показати клієнтів, які ще нічого не купили.
SELECT * FROM client
WHERE purchases = 0;
-- Вивід
 client_id |  login   | purchases | client_status
-----------+----------+-----------+---------------
       322 | new_user |         0 |             1
(1 row)

-- 7. Показати співвідношення між всім тиражем матеріалів з віковим рейтингом до
-- 18 і більше 18 років. Формат: "<тираж до 18> / <тираж більше 18>".
--
-- На жаль, я не придумав як вивести дані у заданому форматі, але мені вдалося
-- вивести дані у вигляді окремого стовпця SUM_CIRC
SELECT title, age_restriction, circulation, SUM(circulation)
OVER (PARTITION BY age_restriction < 12) sum_circ
FROM material_info M
INNER JOIN published_material P ON M.material_id=P.material_id
ORDER BY age_restriction < 16
-- Вивід
               title                | age_restriction | circulation | sum_circ
------------------------------------+-----------------+-------------+----------
 Winnie the pooh                    |               6 |        2000 |    18650
 Alica adventures in the Wonderland |              10 |        1300 |    18650
 News magazine for 2022             |              12 |        9000 |    18650
 The Lord of the rings              |              12 |         800 |    18650
 Just for fun                       |              12 |         550 |    18650
 The Lord of the rings              |              12 |        5000 |    18650
 Database lection course            |              16 |         400 |     1400
 Ulysses                            |              16 |        1000 |     1400
(8 rows)



-- 8. Показати по одному найпопулярнішому матеріалу (за кількістю замовлень від
-- клієнтів) в трьох категоріях. Із вказанням виданому тиражу за весь час.

--      100 < тираж < 700
SELECT M.material_id, M.title, P.circulation, COUNT(R.material_id) request_count
FROM material_info M
INNER JOIN published_material P ON M.material_id=P.material_id
INNER JOIN request R ON M.material_id=R.material_id
WHERE circulation > 100 AND circulation < 700
GROUP BY M.material_id, M.title, P.circulation
ORDER BY M.material_id DESC
LIMIT 1;
-- Вивід
 material_id |          title          | circulation | request_count
-------------+-------------------------+-------------+---------------
          56 | Database lection course |         400 |             1
(1 row)

--      700 <= тираж < 5000
-- ...
WHERE circulation >= 700 AND circulation <= 5000
-- ...
-- Вивід
 material_id |               title                | circulation | request_count
-------------+------------------------------------+-------------+---------------
         832 | Alica adventures in the Wonderland |        1300 |             3
(1 row)

--      5000 <= тираж < 100000
-- ...
WHERE circulation >= 5000 AND circulation <= 100000
-- ...
-- Вивід
 material_id |         title         | circulation | request_count
-------------+-----------------------+-------------+---------------
         821 | The Lord of the rings |        5000 |             3
(1 row)

-- 9. Показати контракти, які є завершеними і в яких фактичний тираж >= запланованому.
SELECT C.material_id, M.title, planed_circulation, circulation
FROM contract C
INNER JOIN published_material P ON C.material_id=P.material_id
INNER JOIN material_info M ON C.material_id=M.material_id
WHERE circulation>=planed_circulation;
-- Вивід
 material_id |         title          | planed_circulation | circulation
-------------+------------------------+--------------------+-------------
         196 | News magazine for 2022 |               9000 |        9000
         869 | Just for fun           |                550 |         550
         870 | Winnie the pooh        |               2000 |        2000
(3 rows)

-- 10. Показати всіх співробітників Олегів і Віталіїв, які ніколи не проводили публікації. 
WITH workers_without_pub AS
        (SELECT worker_id FROM worker
        EXCEPT
        SELECT responsible_worker FROM published_material)
SELECT wp.worker_id, a.login, first_name || ' ' || last_name worker_name
FROM
workers_without_pub wp
INNER JOIN worker w ON wp.worker_id=w.worker_id
INNER JOIN auth_info a ON w.login=a.login;
-- Вивід
 worker_id |  login   |   worker_name
-----------+----------+-----------------
       255 | Editor_2 | Viktor Dubov
       243 | Director | John Frog
       805 | Editor   | Chistopher Baum
(3 rows)



----------------------------------------------------
CREATE OR REPLACE FUNCTION get_top_request_users() RETURNS TABLE (
    client_id INT,
    request_count INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        R.client_id,
        COUNT(R.request_id) AS request_count
    FROM
        request R
    GROUP BY
        R.client_id
    ORDER BY
        R.request_count DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;

        SELECT M.title, M.author, COUNT(R.title) AS req_count
        FROM material_info M
        INNER JOIN request R ON M.title = R.title
        GROUP BY M.title, M.author
        ORDER BY req_count DESC
        LIMIT 10;


ERROR:  permission denied to grant role "pg_read_all_data"
DETAIL:  Only roles with the ADMIN option on role "pg_read_all_data" may grant this role.


