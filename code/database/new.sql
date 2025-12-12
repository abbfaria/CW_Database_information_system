---------------------- Adding domains --------------------------------
CREATE DOMAIN phone_number AS VARCHAR(15)
CHECK(VALUE ~ '^\d{3}\s?\d{3}\s?\d{4}$');

CREATE DOMAIN email_address AS VARCHAR(255)
CHECK(VALUE ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$');

CREATE DOMAIN contract_status AS VARCHAR(50)
CHECK(VALUE IN ('processing', 'to print', 'printed', 'canceled'));

CREATE DOMAIN worker_status AS VARCHAR(50)
CHECK(VALUE IN ('working', 'on_leave', 'terminated'));

CREATE DOMAIN request_status AS VARCHAR(50)
CHECK(VALUE IN ('new', 'processing', 'completed', 'canceled'));

---------------------- Adding views --------------------------------
CREATE VIEW active_contracts AS
SELECT
    c.contract_id,
    c.worker_id,
    w.login AS worker_login,
    c.material_id,
    m.title AS material_title,
    c.planed_circulation,
    c.status,
    c.last_changed_date
FROM
    contract c
JOIN
    worker w ON c.worker_id = w.worker_id
JOIN
    material_info m ON c.material_id = m.material_id
WHERE
    c.status = 'processing';


CREATE VIEW popular_materials AS
SELECT 
    m.material_id, 
    m.title, 
    m.author, 
    COUNT(r.request_id) AS request_count
FROM 
    material_info m
JOIN 
    request r ON m.material_id = r.material_id
GROUP BY 
    m.material_id, m.title, m.author
ORDER BY 
    request_count DESC;


CREATE VIEW recent_requests AS
SELECT 
    r.request_id, 
    r.client_id, 
    c.login AS client_login, 
    r.title, 
    r.author, 
    r.status, 
    r.request_date, 
    r.comment
FROM 
    request r
JOIN 
    client c ON r.client_id = c.client_id
WHERE 
    r.request_date >= CURRENT_DATE - INTERVAL '1 month';


CREATE VIEW worker_statistics AS
SELECT 
    w.worker_id, 
    w.login, 
    w.position, 
    w.status, 
    COUNT(p.published_material_id) AS published_count
FROM 
    worker w
LEFT JOIN 
    published_material p ON w.worker_id = p.responsible_worker
GROUP BY 
    w.worker_id, w.login, w.position, w.status;


CREATE VIEW requests_with_comments AS
SELECT 
    r.request_id, 
    r.client_id, 
    c.login AS client_login, 
    r.title, 
    r.author, 
    r.status, 
    r.request_date, 
    r.comment
FROM 
    request r
JOIN 
    client c ON r.client_id = c.client_id
WHERE 
    r.comment IS NOT NULL;



Для получения ролей пользователя
        SELECT r.rolname AS role_name
        FROM pg_roles r
        JOIN pg_auth_members m ON r.oid = m.roleid
        JOIN pg_roles u ON m.member = u.oid
        WHERE u.rolname = 'username';
