--
-- 4 Лабораторна (підзапити, представлення, аналітичні функції)
--

-- 1. Отримати (в одному запиті) список матеріалу зі вказанням рейтингу по:
--      тиражу за весь час
--      тиражу за останній місяць
--      кількості замовлень від клієнтів
SELECT M.title, M.author, P.circulation AS full_ciculation, circulation AS year_circulation, COUNT(R.material_id) req_count, P.publishing_date
FROM material_info M
INNER JOIN published_material P ON M.material_id=P.material_id
INNER JOIN request R ON M.material_id=R.material_id
WHERE circulation = (
        SELECT circulation FROM published_material P
        WHERE P.material_id=M.material_id AND
                publishing_date > '2023-01-01'::date
)
GROUP BY M.title, M.author, P.circulation, P.publishing_date;
-- вивід підзапиту
               title                |    author     | full_ciculation | year_circulation | req_count | publishing_date
------------------------------------+---------------+-----------------+------------------+-----------+-----------------
 Alica adventures in the Wonderland | Carroll L.    |            1300 |             1300 |         3 | 2023-03-01
 Database lection course            | Malahov E.V.  |             400 |              400 |         1 | 2023-07-01
 The Lord of the rings              | Tolkien J.R.R |             800 |              800 |         3 | 2023-05-01
(3 rows)



-- 2. Зробити представлення про співробітників.
--      Додати інформацію матеріал, публікацію якого він виконував з найменшим тиражем.
WITH last_publication AS
        (SELECT material_id, circulation, responsible_worker FROM published_material)
SELECT W.login, worker_id, material_id, circulation FROM worker W
INNER JOIN last_publication P ON W.worker_id=P.responsible_worker
WHERE login='admin'
ORDER BY worker_id, circulation
LIMIT 1;
-- вивід
 login | worker_id | material_id | circulation
-------+-----------+-------------+-------------
 Admin |       464 |          56 |         400
(1 row)

--      Додати інформацію про клієнтів, які робити запити на останній в його роботі матеріал, публікацію якого він вже виконав.
WITH last_publication AS
        (SELECT client_id, R.material_id, publishing_date, responsible_worker FROM request R
        INNER JOIN published_material P ON P.material_id=R.material_id
        WHERE request_status = 1)
SELECT W.login, W.worker_id, L.client_id, L.material_id, L.publishing_date FROM last_publication L
INNER JOIN worker W ON W.worker_id=L.responsible_worker
WHERE login = 'admin_2'
ORDER BY publishing_date DESC;
-- вивід
  login  | worker_id | client_id | material_id | publishing_date
---------+-----------+-----------+-------------+-----------------
 Admin_2 |       277 |       841 |         832 | 2023-03-01
 Admin_2 |       277 |       654 |         832 | 2023-03-01
(2 rows)

-- 3. Отримати типи матеріалу, в яких ще немає матеріалу.
WITH loc_mat_form AS
        (SELECT form_id FROM material_form
        EXCEPT
        SELECT form FROM material_info)
SELECT F.form_id, form AS form_name FROM loc_mat_form F
INNER JOIN material_form M ON F.form_id=M.form_id
ORDER BY form_id;
-- вивід підзапиту
 form_id | form_name
---------+-----------
       4 | news
       6 | comics
(2 rows)







SELECT M.title, M.author, COUNT(R.title) AS req_count
FROM material_info M
INNER JOIN request R ON M.title = R.title
GROUP BY M.title, M.author
ORDER BY req_count DESC
LIMIT 10;


SELECT W.login, COUNT(P.material_id) AS pub_count
FROM worker W
INNER JOIN published_material P ON W.worker_id = P.responsible_worker
GROUP BY W.login
ORDER BY pub_count DESC
LIMIT 10;

SELECT M.title, M.author, P.circulation
FROM material_info M
INNER JOIN published_material P ON M.material_id = P.material_id
WHERE P.publishing_date BETWEEN '2023-01-01' AND '2023-12-31'
ORDER BY P.circulation DESC
LIMIT 10;
