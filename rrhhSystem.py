from conexions import systemRRHH, systemArchivoApp
from decimal import Decimal
from datetime import datetime

# Obtener la fecha actual
fecha_actual = datetime.now()
# Formatear la fecha como YYYY-MM-DD
fecha_formateada = fecha_actual.strftime("%Y-%m-%d")

# Crear una instancia de la clase
db = systemRRHH()
dbAr = systemArchivoApp()
success_employee_codes = ""

# Funcion para obtener y grabar los documentos
def docs_employee(id_employee):
    global success_employee_codes 
    id_employee = str(id_employee)
    success_employee_codes = success_employee_codes + id_employee + ","
    # creación de todos los registros de documentos
    # obtencion de ids activos de documentos
    dbAr.connect()
    query_docs = """SELECT id_document FROM expediente.document WHERE show_ = 1 ORDER BY id_document ASC"""
    dbAr.execute_query(query_docs)
    docs_ids = dbAr.cursor.fetchall()
    dbAr.disconnect()
    # insert de registros de docs
    for doc in docs_ids:
        dbAr.connect()
        id_doc = str(doc[0])
        query_docs = """INSERT INTO expediente.employee_document (
                          employee_id,
                          document_id,
                          document_status_id,
                          data_status_id,
                          last_update
                          ) 
                          VALUES (
                          '"""+id_employee+"""',
                          '"""+id_doc+"""',
                          '5',
                          '1',
                          '"""+fecha_formateada+"""'
                          )"""
        dbAr.execute_query(query_docs)
        dbAr.disconnect()

# Ejecutar una consulta
db.connect()
db.execute_query('''SELECT 
                      emp.id_employee, 
                      emp.name, 
                      emp.id_account, 
                      emp.generation, 
                      emp.site, 
                      emp.id_status, 
                      emp.work_start_date
                  FROM OPENQUERY(RH_ACC,'SELECT 
                    emp.id_empleado AS id_employee, 
                    TRIM(TRIM(TRIM(TRIM(TRIM(c.NOMBRE1) || '' '' || TRIM(c.NOMBRE2)) || '' '' || TRIM(c.APELLIDO1)) || '' '' || TRIM(c.APELLIDO2)) || '' '' || TRIM(c.APELLIDO_CASADA)) AS name,
                    gn.GRUPO_NOMINA as id_account,
                    emp.NUM_GENERACION AS generation, 
                    s.NOMBRE_SITE AS site, 
                    ee.ID_ESTATUS_EMPLEADO AS id_status, 
                    TO_CHAR(emp.FECHA_INGRESO,''yyyy-mm-dd'') AS work_start_date,
                    pais.NACIONALIDAD as nationality
                    FROM MAIN_RRHH.RHC_EMPLEADOS emp
                    INNER JOIN MAIN_FUSA.MG_CONTACTOS c ON c.COD_CONTACTO = emp.COD_CONTACTO
                    INNER JOIN MAIN_RRHH.RHC_GRUPO_NOMINA gn ON gn.ID_GRUPO_NOMINA = emp.GRUPO_NOMINA
                    INNER JOIN MAIN_RRHH.RHC_SITE s ON s.ID_SITE = emp.ID_SITE
                    INNER JOIN MAIN_RRHH.RHC_ESTATUS_EMPLEADO ee ON ee.ID_ESTATUS_EMPLEADO = emp.ID_ESTATUS_EMPLEADO
                    INNER JOIN MAIN_FUSA.MG_PAISES pais ON pais.COD_PAIS = c.COD_PAIS
                  ') emp
                  WHERE emp.nationality = 'GUATEMALTECO'
                  AND emp.work_start_date >= CAST(GETDATE()-150 AS DATE)
                  ORDER BY emp.id_employee''')

codigos = ""
resultados = db.cursor.fetchall()

for index, row in enumerate(resultados):
    if index == len(resultados) - 1:
        codigos = codigos + str(row[0])
    else:
        codigos = codigos + str(row[0]) + ","

# Conexion y validacion de codigos en sistema de Archivo
dbAr.connect()

query = """SELECT 
              id_employee, 
              name, 
              account_id, 
              site_id, 
              emp_status_id, 
              generation, 
              fecha_ingreso
            FROM expediente.employee WHERE id_employee IN (""" + codigos + """)"""

dbAr.execute_query(query)
Encontrados = dbAr.cursor.fetchall()
dbAr.disconnect()
codesArch = ""

for index, row in enumerate(Encontrados):
    if index == len(Encontrados) - 1:
        codesArch = codesArch + str(row[0])
    else:
        codesArch = codesArch + str(row[0]) + ","

# Manipulacion de resultados
codes_list = set(codigos.split(","))
codesarch_list = set(codesArch.split(","))

codigos_faltantes = codes_list.difference(codesarch_list)

if len(codigos_faltantes) > 0:
    codigos_faltantes_parameter = ",".join(codigos_faltantes)
    conjunto_decimal = {Decimal(valor) for valor in codigos_faltantes}

    for_insert_query = [
        tupla for tupla in resultados if tupla[0] in conjunto_decimal]

# validacion y proceso para actualizacion de archivo app
for tupla in for_insert_query:
    dbAr.connect()
    query_account_site = """select a.id_account, s.id_site
                      from expediente.account a 
                      cross join expediente.site s 
                      where a.account = '"""+tupla[2]+"""' and s.site = '"""+str(tupla[4])+"""';"""
    dbAr.execute_query(query_account_site)
    account_site = dbAr.cursor.fetchall()
    dbAr.disconnect()
    code = str(tupla[0])
    status_id = str(tupla[5])
    account_id = str(account_site[0][0]) if len(account_site) > 0 else "115"
    site_id = str(account_site[0][1]) if len(account_site) > 0 else "565"
    generation = str(tupla[3])
    name = tupla[1]
    last_update = tupla[6]
    if len(account_site) > 0:  # 115 Sin Cuenta 565 sin site
        dbAr.connect()
        query_Insert = """INSERT INTO expediente.employee 
                          (
                            id_employee,
                            account_id,
                            site_id,
                            emp_status_id,
                            data_status_id,
                            name,
                            generation,
                            fecha_ingreso,
                            fecha_recepcion,
                            fecha_auditoria,
                            fecha_recep_contratos,
                            exp_comp,
                            fecha_formalizacion,
                            observations,
                            complete_incomplete,
                            last_update
                          ) 
                          VALUES 
                          (
                            '"""+code+"""',
                            '"""+account_id+"""',
                            '"""+site_id+"""',
                            '"""+status_id+"""',
                            '1',
                            '"""+name+"""',
                            '"""+generation+"""',
                            '"""+last_update+"""',
                            NULL,
                            NULL,
                            NULL,
                            0,
                            NULL,
                            NULL,
                            0,
                            '"""+fecha_formateada+"""'
                          )"""
        dbAr.execute_query(query_Insert)
        dbAr.disconnect()
        docs_employee(tupla[0])
    else:
        dbAr.connect()
        query_Insert = """INSERT INTO expediente.employee 
                            (
                              id_employee,
                              account_id,
                              site_id,
                              emp_status_id,
                              data_status_id,
                              name,
                              generation,
                              fecha_ingreso,
                              fecha_recepcion,
                              fecha_auditoria,
                              fecha_recep_contratos,
                              exp_comp,
                              fecha_formalizacion,
                              observations,
                              complete_incomplete,
                              last_update
                            ) 
                          VALUES 
                          (
                            '"""+code+"""',
                            '"""+account_id+"""',
                            '"""+site_id+"""',
                            '"""+status_id+"""',
                            '1',
                            '"""+name+"""',
                            '"""+generation+"""',
                            '"""+last_update+"""',
                            NULL,
                            NULL,
                            NULL,
                            0,
                            NULL,
                            NULL,
                            0,
                            '"""+fecha_formateada+"""'
                          )"""
        dbAr.execute_query(query_Insert)
        dbAr.disconnect()
        docs_employee(tupla[0])

print("Finalizo la actualización de empleados")
print(success_employee_codes)