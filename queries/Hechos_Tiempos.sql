SELECT T.pgsBuzID, T.pgsID, T.pgsDateWork 'Fecha',
U.id 'idAbogado', U.username 'Email',
U.fname 'Abogado', -- C.cmrName 'Cliente', AA.pcsDsc 'Asunto', 
-- APA.name 'AreaPracticaAsunto', 
AP.name 'AreaPractica',
T.pgsHourRate 'TarifaHora',
CASE WHEN T.pgsInvoiceble = 1 THEN 'Facturable'
WHEN T.pgsInvoiceble = 2 THEN 'No Facturable'
ELSE NULL END 'TipoTiempo',
IF(T.pgsInvoiceble = 1, T.pgsMinuts/60, 0) 'TiempoFacturable',
IF(T.pgsInvoiceble = 1, T.pgsTotal, 0) 'ValorTiempoFacturable',
IF(T.pgsInvoiceble = 2, T.pgsMinuts/60, 0) 'TiempoNoFacturable',
IF(T.pgsInvoiceble = 2, T.pgsTotal, 0) 'ValorTiempoNoFacturable'
-- T.pgsDetails 'Descripcion'
-- T.*
FROM tmc_progress_tbl_pgs T
INNER JOIN users U ON T.pgsProID = U.id
-- INNER JOIN tmc_business_rel_buz A ON T.pgsBuzID = A.buzID
-- INNER JOIN tmc_process_tbl_pcs AA ON A.buzPcsID = AA.pcsID
-- INNER JOIN tmc_customers_tbl_cmr C ON A.buzCmrID = C.cmrID
-- INNER JOIN practice_areas APA ON A.practice_area_id = APA.id_practice_area
INNER JOIN practice_areas AP ON T.practice_area_id = AP.id_practice_area
-- WHERE T.pgsStatus IN (1,3,4) -- No incluir: inactivo, compartido, cancelado, merma, liquidado, evento rechazado
WHERE T.pgsStatus NOT IN (2,5,7) AND U.user_type NOT IN (0,2,4)

-- AND A.deleted = 0
-- and T.pgsDateWork = '2024-05-20'
-- and T.pgsProID = 88