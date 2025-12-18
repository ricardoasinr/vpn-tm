-- Consulta para DWH - Hechos Estado de Resultados
SELECT 'BKP' AS 'Sociedad', F.invDate AS 'Fecha', 0 AS 'Asiento', '' AS 'DocOrigen', invOficialNum AS 'NroFactura', U.fname AS 'Usuario',
0 AS 'DebitoBOB', SUM(FD.indSubTotal)/6.86 AS 'CreditoBOB', 0 AS 'DebitoUSD', SUM(FD.indSubTotal) AS 'CreditoUSD',
F.invConcept AS 'Glosa', AP.area_codigo_externo_primario AS 'AreaCC', 'BKP' AS 'RegionCC',
'411100001' AS 'CodigoCuenta', 'Honorarios por Servicios Fijos' AS 'Cuenta', '411100000' AS 'CodigoCuentaPadre', 'Ingresos Fijos' AS 'CuentaUnificador', '4.1.1.1' AS 'CodigoCuentaUnificador',
A.expediente AS 'CodigoProyecto', AD.pcsDsc AS 'Proyecto', 'BKP' AS 'Regional', UR.fname AS 'Abogado', AP.name AS 'Area',
C.cmrID AS 'CodigoCliente', C.cmrName AS 'Cliente', '' AS 'Industria'
FROM tm_emba.tmi_invoice_tbl_inv F
INNER JOIN tm_emba.series FS ON F.serie_id = FS.id
INNER JOIN tm_emba.users U ON F.created_by = U.id
INNER JOIN tm_emba.tmi_invoicedetail_tbl_ind FD ON FD.indInvID = F.invID
INNER JOIN tm_emba.tmc_business_rel_buz A ON FD.indBuzID = A.buzID
LEFT JOIN practice_areas AP ON A.practice_area_id = AP.id_practice_area
LEFT JOIN tm_emba.users UR ON A.buzResponsable = UR.id
INNER JOIN tm_emba.tmc_process_tbl_pcs AD on A.buzPcsID = AD.pcsID
INNER JOIN tm_emba.tmc_customers_tbl_cmr C on A.buzCmrID = C.cmrID
WHERE FS.id IN (5,6,22) -- PREBKP, BPK, ND25
AND F.invStatus != 4 -- Anulado
GROUP BY F.invDate, invOficialNum, U.fname, F.invConcept, AP.area_codigo_externo_primario,
A.expediente, AD.pcsDsc, UR.fname, AP.name, C.cmrID, C.cmrName

