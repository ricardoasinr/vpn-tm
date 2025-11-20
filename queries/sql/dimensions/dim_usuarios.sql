SELECT U.id, U.fname 'Nombre', IF(U.enabled = 1, 'Activo', 'Inactivo') 'Estado', 
R.roll_description 'Categoria', U.username 'Email', U.personal_identification_number 'CI'
FROM tm_emba.users U
LEFT JOIN tm_emba.user_roll R ON U.id_user_roll = R.user_roll_id
WHERE U.user_type NOT IN (0,2,4) -- Administrador, Auxiliar, TM
order by 1

