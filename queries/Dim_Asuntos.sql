SELECT A.buzID, A.created 'Fecha', A.expediente 'CodigoAsunto',
C.cmrName 'Cliente', 
IF(YEAR(C.created)=YEAR(A.created) AND MONTH(C.created)=MONTH(A.created),'Nuevo','Existente') 'TipoCliente',  
( SELECT TT.name FROM object_terms OT
  INNER JOIN taxonomy_terms TT ON OT.term_id = TT.id 
  INNER JOIN taxonomies T ON TT.tax_id = T.id 
  WHERE T.name = 'OriginClienteSAP' 
  AND OT.object_id = C.cmrID  
  LIMIT 1 ) 'OrigenCliente',
( SELECT TT.name FROM tm_emba.object_terms OT
  INNER JOIN tm_emba.taxonomy_terms TT ON OT.term_id = TT.id
  INNER JOIN tm_emba.taxonomies T ON TT.tax_id = T.id
  AND T.name = 'RegionalEMBA' 
  AND OT.object_id = A.buzID
  LIMIT 1 ) 'Regional',
AP.name 'AreaPractica',
U.nickname 'ResponsableFacturacion'-- ,
-- CASE WHEN A.buzImoID = 2 THEN 
-- ( SELECT G.grpMonthlyFixRate  
--   FROM tmc_group_tbl_grp G
--   WHERE G.grpID = A.buzOnly )
-- WHEN A.buzImoID = 3 OR A.buzImoID = 6  THEN A.buzMonthlyFixRate
-- WHEN A.buzImoID = 4 THEN H.monthlyFixRate
-- ELSE 0 END AS 'Honorarios'

FROM tmc_business_rel_buz A 
-- INNER JOIN tmc_process_tbl_pcs AA ON A.buzPcsID = AA.pcsID
INNER JOIN tmc_customers_tbl_cmr C ON A.buzCmrID = C.cmrID
LEFT JOIN practice_areas AP ON A.practice_area_id = AP.id_practice_area
LEFT JOIN users U ON A.buzResponsable = U.id
-- LEFT JOIN hitos H ON (A.buzID = H.id_business AND A.buzImoID = 4)
WHERE A.deleted = 0
-- and A.buzID IN (1360,1364,2966)


