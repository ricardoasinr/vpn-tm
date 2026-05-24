# Modelo de Datos — Datawarehouse Moreno Baldivieso

## Esquema Estrella

El datawarehouse sigue un **esquema estrella** con dos dimensiones principales y cuatro tablas de hechos.

```
                    ┌─────────────────┐
                    │  dim_usuarios   │
                    │─────────────────│
                    │ id              │
                    │ Nombre          │
                    │ Estado          │
                    │ Categoria       │
                    │ Email           │
                    │ CI              │
                    └────────┬────────┘
                             │
                             │ id ◄─── idAbogado / user.id
                             │
┌──────────────┐    ┌────────┴────────────────────────┐
│ dim_asuntos  │    │        hechos_tiempos            │
│──────────────│    │─────────────────────────────────│
│ buzID        ├────► pgsBuzID / business.id           │
│ Fecha        │    │ pgsID / id                      │
│ CodigoAsunto │    │ Fecha / date                    │
│ Cliente      │    │ idAbogado                       │
│ TipoCliente  │    │ Email                           │
│ OrigenCliente│    │ Abogado / user.fullName         │
│ Regional     │    │ AreaPractica / practice_area.name│
│ AreaPractica │    │ TarifaHora / pgsHourRate        │
│ Responsable  │    │ TipoTiempo (Facturable/No Fact.)│
│ ...          │    │ TiempoFacturable (horas)        │
└──────────────┘    │ TiempoNoFacturable (horas)      │
                    │ ValorTiempoFacturable           │
                    │ ValorTiempoNoFacturable         │
                    └─────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              hechos_capacidad                       │
│─────────────────────────────────────────────────────│
│ id (usuario)                                        │
│ Fecha (mes)                                         │
│ Gestion (año)                                       │
│ Mes (número)                                        │
│ DiasLaborares (días hábiles - festivos - ausencias) │
│ HorasMes (días hábiles × horas diarias)             │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│          hechos_estado_resultados                   │
│─────────────────────────────────────────────────────│
│ Sociedad                                            │
│ Fecha                                               │
│ NroFactura                                          │
│ Usuario (facturador)                                │
│ CreditoBOB / CreditoUSD                             │
│ Glosa                                               │
│ AreaCC / RegionCC                                   │
│ CodigoCuenta / Cuenta                               │
│ CodigoProyecto / Proyecto                           │
│ Abogado responsable                                 │
│ CodigoCliente / Cliente                             │
└─────────────────────────────────────────────────────┘
```

---

## Dimensiones

### `dim_asuntos` — Dimensión de Asuntos/Expedientes

Representa los asuntos jurídicos activos del estudio.

**Fuente SQL** (`queries/sql/dimensions/dim_asuntos.sql`):

| Columna | Tabla Origen | Descripción |
|---------|-------------|-------------|
| `buzID` | `tmc_business_rel_buz.buzID` | ID del asunto (clave primaria) |
| `Fecha` | `tmc_business_rel_buz.created` | Fecha de creación del asunto |
| `CodigoAsunto` | `tmc_business_rel_buz.expediente` | Código expediente |
| `Cliente` | `tmc_customers_tbl_cmr.cmrName` | Nombre del cliente |
| `TipoCliente` | Calculado | `Nuevo` si mismo mes/año que creación del cliente, `Existente` si no |
| `OrigenCliente` | `taxonomy_terms` (OriginClienteSAP) | Origen SAP del cliente |
| `Regional` | `taxonomy_terms` (RegionalEMBA) | Regional asignada al asunto |
| `AreaPractica` | `practice_areas.name` | Área de práctica jurídica |
| `ResponsableFacturacion` | `users.nickname` | Usuario responsable de facturación |

**Filtro:** Solo asuntos no eliminados (`deleted = 0`).

**Fuente API** (`queries/graphql/dim_asuntos.graphql`):  
Query `BusinessMeta` — retorna datos enriquecidos del asunto incluyendo modo de facturación, moneda, estado BPM, hitos, fecha de vencimiento estimada, etc.

Variables de paginación por defecto:
```json
{ "enabled": [1, 0], "page": 1, "limit": 1000, "orderDesc": false }
```

---

### `dim_usuarios` — Dimensión de Usuarios

Representa los abogados y profesionales del estudio (excluye administradores, auxiliares y usuarios TM).

**Fuente SQL** (`queries/sql/dimensions/dim_usuarios.sql`):

| Columna | Tabla Origen | Descripción |
|---------|-------------|-------------|
| `id` | `users.id` | ID del usuario |
| `Nombre` | `users.fname` | Nombre completo |
| `Estado` | `users.enabled` | `Activo` / `Inactivo` |
| `Categoria` | `user_roll.roll_description` | Categoría/rol del usuario |
| `Email` | `users.username` | Email (usado como identificador) |
| `CI` | `users.personal_identification_number` | Cédula de identidad |

**Filtro:** `user_type NOT IN (0, 2, 4)` — excluye Administrador (0), Auxiliar (2) y TM (4).

**Fuente API** (`queries/graphql/dim_usuarios.graphql`):  
Query `Users` — incluye nombre corto, categoría, días permitidos y estado de habilitación.

---

## Hechos

### `hechos_tiempos` — Registros de Tiempo

Registros de tiempo trabajado por abogados en asuntos.

**Fuente SQL** (`queries/sql/facts/hechos_tiempos.sql`):

| Columna | Descripción |
|---------|-------------|
| `pgsBuzID` | FK → `dim_asuntos.buzID` |
| `pgsID` | ID del registro de tiempo |
| `Fecha` | Fecha del trabajo (`pgsDateWork`) |
| `idAbogado` | FK → `dim_usuarios.id` |
| `Email` | Email del abogado |
| `Abogado` | Nombre del abogado |
| `AreaPractica` | Área de práctica del tiempo registrado |
| `TarifaHora` | Tarifa por hora aplicada |
| `TipoTiempo` | `Facturable` (pgsInvoiceble=1) o `No Facturable` (=2) |
| `TiempoFacturable` | Minutos facturables / 60 |
| `ValorTiempoFacturable` | Valor monetario del tiempo facturable |
| `TiempoNoFacturable` | Minutos no facturables / 60 |
| `ValorTiempoNoFacturable` | Valor monetario del tiempo no facturable |

**Filtros:**
- `pgsStatus NOT IN (2, 5, 7)` — excluye: compartido (2), cancelado (5), liquidado (7)
- `user_type NOT IN (0, 2, 4)` — solo abogados activos

**Fuente API** (`queries/graphql/hechos_tiempos.graphql`):  
Query `TimesByFiltersPaged` — incluye datos enriquecidos: moneda, clasificación de cliente, actividad, tarea, estado de workflow, tiempo de inicio/fin, etc.

Variables por defecto:
```json
{
  "access": "ALL", "max_per_page": 1000, "page": 1,
  "order_by": "date", "order_dir": true
}
```

---

### `hechos_capacidad` — Capacidad por Abogado/Mes

Calcula la capacidad disponible de cada abogado por mes, descontando festivos y ausencias.

**Fuente SQL** (`queries/sql/facts/hechos_capacidad.sql`):  
Consulta compleja con CTEs recursivas.

| Columna | Descripción |
|---------|-------------|
| `id` | FK → `dim_usuarios.id` |
| `Fecha` | Primer día del mes |
| `Gestion` | Año |
| `Mes` | Número de mes |
| `DiasLaborares` | Días hábiles − festivos − días de ausencia |
| `HorasMes` | `DiasLaborares × HorasDiarias` (según productividad configurada) |

**Lógica:**
1. CTE `meses`: genera una fila por cada mes desde la fecha de inicio de productividad de cada usuario hasta el mes actual.
2. CTE `dias_calendario`: genera todos los días hábiles (lunes a viernes) desde 2020.
3. Cruza usuarios × meses × días, resta festivos (tabla `festivos`) y ausencias (tabla `ausencias`).

**Solo disponible desde BD** (no tiene equivalente en la API).

---

### `hechos_estado_resultados` — Estado de Resultados

Registros de facturación para análisis contable y de ingresos.

**Fuente SQL** (`queries/sql/facts/hechos_estado_resultados.sql`):

| Columna | Descripción |
|---------|-------------|
| `Sociedad` | Fijo: `BKP` |
| `Fecha` | Fecha de la factura |
| `NroFactura` | Número oficial de factura |
| `Usuario` | Usuario que creó la factura |
| `CreditoBOB` | Subtotal en bolivianos (USD / 6.86) |
| `CreditoUSD` | Subtotal en USD |
| `Glosa` | Concepto de la factura |
| `AreaCC` | Código de área (para centro de costos) |
| `CodigoCuenta` | `411100001` (Honorarios por Servicios Fijos) |
| `CuentaUnificador` | `Ingresos Fijos` |
| `CodigoProyecto` | Expediente del asunto |
| `Proyecto` | Descripción del proceso |
| `Abogado` | Responsable del asunto |
| `CodigoCliente` | ID del cliente |
| `Cliente` | Nombre del cliente |

**Filtros:**
- Series `IN (5, 6, 22)`: PREBKP, BKP, ND25
- `invStatus != 4`: excluye facturas anuladas

**Solo disponible desde BD** (no tiene equivalente en la API).

---

## Tablas Fuente en la Base de Datos

| Tabla | Descripción |
|-------|-------------|
| `tmc_business_rel_buz` | Asuntos/expedientes jurídicos |
| `tmc_process_tbl_pcs` | Procesos asociados a asuntos |
| `tmc_customers_tbl_cmr` | Clientes |
| `tmc_progress_tbl_pgs` | Registros de tiempo (progreso) |
| `tmc_usrproductivity_tbl_usp` | Productividad configurada por usuario |
| `tmi_invoice_tbl_inv` | Facturas |
| `tmi_invoicedetail_tbl_ind` | Detalle de líneas de factura |
| `users` | Usuarios del sistema |
| `user_roll` | Roles/categorías de usuarios |
| `practice_areas` | Áreas de práctica jurídica |
| `taxonomies` / `taxonomy_terms` / `object_terms` | Sistema de etiquetas |
| `festivos` | Días festivos/feriados |
| `ausencias` | Ausencias de usuarios |
| `tipo_ausencia` | Tipos de ausencia |
| `series` | Series de facturación |

---

## Matrices de Cobertura por Fuente

| Dataset | BD (SQL) | API (GraphQL) |
|---------|----------|---------------|
| `dim_asuntos` | ✓ Versión básica | ✓ Versión enriquecida |
| `dim_usuarios` | ✓ Con CI y categoría | ✓ Con daysAllow |
| `hechos_tiempos` | ✓ Versión básica | ✓ Versión enriquecida |
| `hechos_capacidad` | ✓ (cálculo CTE) | ✗ No disponible |
| `hechos_estado_resultados` | ✓ | ✗ No disponible |
