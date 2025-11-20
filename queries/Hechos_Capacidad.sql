WITH RECURSIVE meses AS (
    SELECT A.id, A.upsDay, 
        A.upsInitDay 'fecha_inicial',  -- Reemplaza con tu fecha inicial
        DATE_FORMAT(A.upsInitDay, '%Y-%m-01') 'mes_inicio',
        LAST_DAY(CURDATE()) 'mes_fin_actual'
    FROM (  SELECT DISTINCT U.id, P.upsDay, P.upsInitDay 
			FROM tm_emba.tmc_usrproductivity_tbl_usp P
			INNER JOIN tm_emba.users U ON P.uspProID = U.id
			WHERE P.uspStatus = 1
			AND P.upsInitDay IS NOT NULL
			AND U.user_type = 1 -- Tipo: Usuario o Abogado?
			AND U.enabled = 1  ) A    
    UNION ALL
    SELECT id, upsDay, fecha_inicial, DATE_ADD(mes_inicio, INTERVAL 1 MONTH), mes_fin_actual
    FROM meses
    WHERE DATE_ADD(mes_inicio, INTERVAL 1 MONTH) <= mes_fin_actual
),

dias_calendario AS (
    SELECT a.Date 'fecha'
    FROM (
        SELECT DATE_ADD('2020-01-01', INTERVAL n DAY) 'Date'
        FROM (
            SELECT a.N + b.N*10 + c.N*100 + d.N*1000 'n'
            FROM (SELECT 0 'N' UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) a
            CROSS JOIN (SELECT 0 'N' UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) b
            CROSS JOIN (SELECT 0 'N' UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) c
            CROSS JOIN (SELECT 0 'N' UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) d
        ) numeros
        WHERE DATE_ADD('2020-01-01', INTERVAL n DAY) BETWEEN '2020-01-01' AND DATE_ADD(CURDATE(), INTERVAL 1 YEAR)
    ) a
    WHERE DAYOFWEEK(a.Date) BETWEEN 2 AND 6  -- Lunes(2) a Viernes(6)
)

SELECT C.id, C.Fecha, C.Gestion, C.Mes, 
-- C.DiasLaborales - COALESCE(F.DiasFestivos,0) 'DiasLaborares',
C.DiasLaborales - COALESCE(F.DiasFestivos,0) - COALESCE(A.total_dias,0) 'DiasLaborares',
-- (C.DiasLaborales - COALESCE(F.DiasFestivos,0)) * C.HorasDiarias 'HorasMes',
(C.DiasLaborales - COALESCE(F.DiasFestivos,0) - COALESCE(A.total_dias,0)) * C.HorasDiarias 'HorasMes'
FROM (
  SELECT 
    M.id,
    -- DATE_FORMAT(m.mes_inicio, '%Y-%m') AS mes_año,
    M.mes_inicio 'Fecha', YEAR(M.mes_inicio) 'Gestion', MONTH(M.mes_inicio) 'Mes',
    M.upsDay 'HorasDiarias',
    COUNT(D.fecha) 'DiasLaborales'
  FROM meses M 
  JOIN dias_calendario D ON D.fecha BETWEEN CASE WHEN M.mes_inicio = DATE_FORMAT(M.fecha_inicial, '%Y-%m-01') THEN M.fecha_inicial ELSE M.mes_inicio END AND LAST_DAY(M.mes_inicio)
  GROUP BY M.id, M.mes_inicio, M.fecha_inicial
  -- ORDER BY M.id, M.mes_inicio
) C 
LEFT JOIN (
  SELECT YEAR(fecha) 'Gestion', MONTH(fecha) 'Mes', COUNT(*) 'DiasFestivos'
  FROM festivos
  WHERE estado = 1
  GROUP BY CONCAT(YEAR(fecha), MONTH(fecha))
) F ON C.Gestion = F.Gestion AND C.Mes = F.Mes
LEFT JOIN (

SELECT id_usuario_ausencia, year_number, month_number, 
SUM(minutos)/60 AS horas, SUM(dias_ausencia_neto) AS dias,
COALESCE(SUM(minutos)/60/8,0) + COALESCE(SUM(dias_ausencia_neto),0) AS total_dias
FROM (
	SELECT u.id AS id_usuario_ausencia,	ta.descripcion as descripcion,
	@minutes := IF(	DATE_FORMAT(a.fecha_inicio, "%Y-%m-%d")=DATE_FORMAT(a.fecha_final, "%Y-%m-%d"),
				ABS(TIMESTAMPDIFF(MINUTE, a.fecha_final, a.fecha_inicio)),
				NULL ) AS minutos,
	@yearnum := CASE
	    WHEN sq.month_number IS NULL OR DATE_FORMAT(a.fecha_final, "%Y")=DATE_FORMAT(a.fecha_inicio, "%Y") THEN DATE_FORMAT(a.fecha_inicio, "%Y")
	    WHEN DATE_FORMAT(a.fecha_final, "%Y")>DATE_FORMAT(a.fecha_inicio, "%Y") AND sq.month_number BETWEEN DATE_FORMAT(a.fecha_inicio, "%m") AND 12 THEN DATE_FORMAT(a.fecha_inicio, "%Y")
	    ELSE DATE_FORMAT(a.fecha_final, "%Y") END AS year_number,
	sq.month_number,
	@startDate := CASE
		WHEN @minutes IS NOT NULL THEN DATE_FORMAT(a.fecha_inicio, "%Y-%m-%d")
		WHEN (DATE_FORMAT(a.fecha_inicio, "%Y%m")=CONCAT(@yearnum,lpad(sq.month_number,2,0))) THEN DATE_FORMAT(a.fecha_inicio, "%Y-%m-%d")
	  	ELSE  DATE_FORMAT(CONCAT(@yearnum,"-",sq.month_number,"-01"), "%Y-%m-%d") END AS start_date_eval,
	@endDate := CASE
		WHEN @minutes IS NOT NULL THEN DATE_FORMAT(a.fecha_final, "%Y-%m-%d")
		WHEN (DATE_FORMAT(a.fecha_final, "%Y%m")=CONCAT(@yearnum,lpad(sq.month_number,2,0))) THEN DATE_FORMAT(a.fecha_final, "%Y-%m-%d")
	  	ELSE LAST_DAY(DATE_FORMAT(CONCAT(@yearnum,"-",sq.month_number,"-01"), "%Y-%m-%d")) END AS end_date_eval,
	@absentDays := IF(@minutes IS NULL, CALC_BUSINESS_DAYS (@startDate, @endDate), NULL) AS absent_business_days,
	@holidays := (SELECT COUNT(1) FROM festivos WHERE fecha BETWEEN @startDate AND @endDate) as holidays,
	@absentDays - @holidays AS dias_ausencia_neto
FROM ausencias a 
INNER JOIN users u ON (a.user_id=u.id)
INNER JOIN tipo_ausencia ta ON (a.tipo=ta.id_tipo_ausencia)
LEFT JOIN ( SELECT 1 AS month_number UNION ALL SELECT 2 AS month_number UNION ALL
		SELECT 3 AS month_number UNION ALL SELECT 4 AS month_number UNION ALL
		SELECT 5 AS month_number UNION ALL SELECT 6 AS month_number UNION ALL
		SELECT 7 AS month_number UNION ALL SELECT 8 AS month_number UNION ALL
		SELECT 9 AS month_number UNION ALL SELECT 10 AS month_number UNION ALL
		SELECT 11 AS month_number UNION ALL SELECT 12 AS month_number 
	) AS sq ON (
		(DATE_FORMAT(a.fecha_inicio, "%Y")=DATE_FORMAT(a.fecha_final, "%Y") AND sq.month_number BETWEEN DATE_FORMAT(a.fecha_inicio, "%m") AND DATE_FORMAT(a.fecha_final, "%m")) 
        OR (DATE_FORMAT(a.fecha_final, "%Y")>DATE_FORMAT(a.fecha_inicio, "%Y")
			AND (sq.month_number BETWEEN DATE_FORMAT(a.fecha_inicio, "%m") AND 12 OR sq.month_number BETWEEN 1 AND DATE_FORMAT(a.fecha_final, "%m"))))
	WHERE TIMESTAMPDIFF(YEAR, a.fecha_final, a.fecha_inicio) < 1 AND NOT (_delete = 1 OR deleted_at IS NOT NULL)
) AS P
GROUP BY id_usuario_ausencia, year_number, month_number


) A ON C.Gestion = A.year_number AND C.Mes = A.month_number AND C.id = A.id_usuario_ausencia


 order by C.id, C.Fecha