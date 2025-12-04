-- Active users query
SELECT 
  user_id,
  username,
  email,
  created_at,
  last_login
FROM users
WHERE status = 'active'
  AND deleted_at IS NULL
ORDER BY last_login DESC;