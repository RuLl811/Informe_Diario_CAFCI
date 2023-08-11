# Importación de librerias
import datetime as dt
import math,time, shutil, sys
from datetime import timedelta
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', None)
print('\n')
print(f"{'*' * 20}\n  {'Informe Diario'}\n{'*' * 20}")
print('\n')
########################################################################################################################
#############################                        INPUTS                  ##############################################
########################################################################################################################

print(f"{'*' * 120}")
while True:
    fecha_principal = input(" Ingresa la fecha del día habil anterior al Informe (d/m/yyyy): ")
    try:
        fecha_principal = dt.datetime.strptime(fecha_principal, "%d/%m/%Y")
        break
    except ValueError:
        print(f"Error: Fecha del día habil anterior al Informe incorrecta. Por favor, ingresa la fecha en el formato d/m/yyyy.")
        print(f"{'*' * 120}")
        print('\n')
while True:
    fecha_informe = input(' Ingresa la fecha del Informe (d/m/yyyy): ')
    try:
        fecha_informe = dt.datetime.strptime(fecha_informe, "%d/%m/%Y")
        break
    except ValueError:
        print(f"{'*' * 120}")
        print("Error: Fecha del Informe incorrecta. Por favor, ingresa la fecha en el formato d/m/yyyy.")
        print(f"{'*' * 120}")
        print('\n')
if fecha_principal > fecha_informe:
    print("Error: La fecha principal es mayor que la fecha del informe.")
    print(f"{'*' * 120}")
    print('\n')
    sys.exit()

print(f"{'*' * 120}\n")

# Formato de fechas para las exportaciones e importaciones
fecha_principal = fecha_principal.strftime("%d%m%Y")
fecha_planilla = fecha_informe.strftime("%Y%m%d")
fecha_concat = fecha_informe.strftime("%d%m%Y")
########################################################################################################################
#############################                  LECTURA DE BASES           ##############################################
########################################################################################################################
start_time = time.time()
########################## Lectura de Equivalencias ################################
equivalencias = pd.read_excel(r"C:\Users\lr110574\PycharmProjects\Informe_Diario\Equivalencias.xlsx", sheet_name='Sheet1')

########################## Lectura del Principal ###################################
#principal = pd.read_csv(r"C:\Users\lr110574\PycharmProjects\Informe_Diario\principal_12072023.csv", sep=';')
principal = pd.read_csv(fr"C:\Users\lr110574\PycharmProjects\Informe_Diario\Salidas\principal_{fecha_principal}.csv", sep=';')
principal['fecha_carga'] = pd.to_datetime(principal['fecha_carga'], format='%Y-%m-%d')
principal['fecha'] = pd.to_datetime(principal['fecha'], format='%Y-%m-%d')
principal = principal.loc[principal['fecha'] >= pd.to_datetime(fecha_informe - timedelta(days=370), format='%Y/%m/%d')]
principal.sort_values(by='fecha', inplace=True)
principal.reset_index(drop=True, inplace=True)

########################## Lectura de la "Planilla Diaria" ##########################
basedia = pd.read_excel(fr"C:\Rubén\Fondos\Informe\Boston\{fecha_planilla}_Planilla_Diaria_F1.xlsx")  # Hacerlo dinamico

end_time = time.time()
total_time0 = end_time - start_time
print("Tiempo total de procesamiento lectura: ", round(total_time0, 4), "segundos")
########################################################################################################################
#############################                  MATRIZ DE FECHAS           ##############################################
########################################################################################################################
start_time = time.time()
dias_habiles = principal['fecha']
dias_habiles = dias_habiles.drop_duplicates()
#dias_habiles.reset_index(drop=True, inplace=True)
dias_habiles = pd.DataFrame(dias_habiles)

dias_habiles = dias_habiles.sort_values('fecha')
dias_habiles.reset_index(drop=True, inplace=True)

calculo_fechas = pd.DataFrame()

calculo_fechas["Referencia"] = ['fechahoy', 'undia', 'fechamtd', 'treintadias', 'noventadias', 'cientoochentadias',
                                'fechaytd', 'tressesentadias']

calculo_fechas["fecha"] = 1
calculo_fechas.iloc[0, 1] = fecha_informe.strftime('%Y-%m-%d')
calculo_fechas.iloc[1, 1] = fecha_informe - timedelta(days=1)
primer_dia_del_mes = dt.datetime(day=1, month=fecha_informe.month, year=fecha_informe.year)
Month_to_date = primer_dia_del_mes - timedelta(days=1)
calculo_fechas.iloc[2, 1] = Month_to_date
#Month_to_date = pd.to_datetime(Month_to_date, format='%Y/%m/%d')
calculo_fechas.iloc[3, 1] = fecha_informe - timedelta(days=30)
calculo_fechas.iloc[4, 1] = fecha_informe - timedelta(days=90)
calculo_fechas.iloc[5, 1] = fecha_informe - timedelta(days=180)
primer_dia_del_año = dt.datetime(day=1, month=1, year=fecha_informe.year)
Year_to_date = primer_dia_del_año - timedelta(days=1)
calculo_fechas.iloc[6, 1] = Year_to_date
calculo_fechas.iloc[7, 1] = fecha_informe - timedelta(days=365)
calculo_fechas["fecha"] = pd.to_datetime(calculo_fechas["fecha"])

def encontrar_fecha_anterior_o_igual(fecha, df):

    if not df.empty:
        if fecha in df['fecha'].values:
            fecha_anterior_o_igual = fecha
        else:
            fecha_anterior_o_igual = df.loc[df['fecha'] < fecha].sort_values('fecha', ascending=False).iloc[0]['fecha']
    else:
        fecha_anterior_o_igual = pd.NaT
    return fecha_anterior_o_igual

# agregar columna con la fecha más cercana a cada fecha en el dataframe nuevas_fechas
calculo_fechas["Fecha a considerar"] = calculo_fechas["fecha"].apply(encontrar_fecha_anterior_o_igual, args=(dias_habiles,))
calculo_fechas = calculo_fechas.drop('fecha', axis=1)
calculo_fechas.iloc[0, 1] = fecha_informe.strftime('%Y-%m-%d')

calculo_fechas['Diferencia de fechas'] = fecha_informe - pd.to_datetime(calculo_fechas['Fecha a considerar'])

new_cols = ['BNA', 'Var_BNA', 'Var_Anualizada_BNA', 'DTI', 'Var_DTI', 'Var_Anualizada_DTI', 'Delta_DTI/BNA']
for col in new_cols:
    calculo_fechas[col] = 0

undia = calculo_fechas.iloc[1, 1].date()
Month_to_date = calculo_fechas.iloc[2, 1].date()
treintadias = calculo_fechas.iloc[3, 1].date()
noventadias = calculo_fechas.iloc[4, 1].date()
cientoochentadias = calculo_fechas.iloc[5, 1].date()
Year_to_date = calculo_fechas.iloc[6, 1].date()
tressesentadias = calculo_fechas.iloc[7, 1].date()

dif_1 = int(calculo_fechas.iloc[1, 2].days)
dif_mtd = int(calculo_fechas.iloc[2, 2].days)
dif_30 = int(calculo_fechas.iloc[3, 2].days)
dif_90 = int(calculo_fechas.iloc[4, 2].days)
dif_180 = int(calculo_fechas.iloc[5, 2].days)
dif_ytd = int(calculo_fechas.iloc[6, 2].days)
dif_360 = int(calculo_fechas.iloc[7, 2].days)

end_time = time.time()
total_time1 = end_time - start_time
print("Tiempo total de procesamiento fechas: ", round(total_time1, 4), "segundos")

########################################################################################################################
#############################                  PLANILLA DIARIA            ##############################################
########################################################################################################################
# Filtro de Fondos Cerrados
start_time = time.time()
basedia.drop(basedia[(basedia.clasi_nombre == "Fondos Cerrados")].index, inplace=True)
basedia["fecha"] = pd.to_datetime(basedia['fecha'], format='%d/%m/%y')  # Formato a fecha de la planilla diaria
basedia = basedia.rename(columns={'fecha': 'fecha_carga'})
basedia["fecha"] = fecha_informe
basedia["fecha"] = pd.to_datetime(basedia['fecha'], format='%Y/%m/%d')
basedia['moneda_cod'] = basedia['moneda_cod'].replace({1: 'ARS', 2: 'USD', 180: 'USD'})
basedia['honorarios_de_exito'] = basedia['honorarios_de_exito'].replace({'N': 0})

basedia = pd.concat([basedia.loc[(basedia['fecha_carga'] == pd.to_datetime(fecha_informe, format='%Y/%m/%d'))],
                     basedia.loc[(basedia['fecha_carga'] == pd.to_datetime(undia, format='%Y/%m/%d'))]], axis=0)
basedia_hoy = basedia.loc[basedia['fecha_carga'] == pd.to_datetime(fecha_informe, format='%Y/%m/%d')]
end_time = time.time()
total_time2 = end_time - start_time
print("Tiempo total de procesamiento lectura de CAFCI: ", round(total_time2, 4), "segundos")
########################################################################################################################
#############################                   CONTROLES                 ##############################################
########################################################################################################################
start_time = time.time()
##################### INCORPORACION DE CLASES NUEVAS AL PRINCIPAL   #####################
clases_dia = list(basedia_hoy["clase_id"])
clases_equi = list(equivalencias["clase_id"])
clases_nuevas = list(filter(lambda x: True if x not in clases_equi else False, clases_dia))

df_clases_nuevas = pd.DataFrame()
df_clases_nuevas['clase_id'] = clases_nuevas
df_clases_nuevas = pd.merge(df_clases_nuevas, basedia_hoy,  on='clase_id', how='left')
df_clases_nuevas = df_clases_nuevas.drop(['rg384', 'liquida', 'suscribe', 'subyacente', 'region_cod', 'horiz_cod',
                                         'compute_0013', 'cuotapartes', 'patrimonio', 'minimo_de_inversion',
                                          'honorarios_de_ingreso', 'honorarios_de_rescate', 'honorarios_de_transferencia',
                                          'honorarios_de_exito', 'fecha', 'fecha_carga'], axis=1)
df_clases_nuevas = df_clases_nuevas.rename(columns={'moneda_cod': 'moneda'})

equivalencias = pd.concat([equivalencias, df_clases_nuevas], ignore_index=True)  # Incorporo las nuevas clases en equivalencias

s_clases_nuevas = df_clases_nuevas['clase_id']
s_clases_nuevas = s_clases_nuevas.rename('Clases_nuevas')

# Listar las clases del archivo Equivalencias que NO estan en Base día
clases_noinformaron = list(filter(lambda x: True if x not in clases_dia else False, clases_equi))
clases_noinformaron = pd.DataFrame(clases_noinformaron)
clases_noinformaron.columns = ['Clases que no informaron']
# AGREGAR CONTROL DE TIPO DE RENTA Y MONEDA DE BASE DIARIA CONTRA EQUIVALENCIAS.

##################### Clases que informaron patrimonio = 0 en la base de CAFCI  ########################
clases_con_0 = basedia_hoy[basedia_hoy.patrimonio == 0]
clases_con_0 = clases_con_0.rename(columns={'clase_id': 'Clases con patrimonio 0'})
clases_con_0 = clases_con_0['Clases con patrimonio 0']

##################### Clases que informaron patrimonion = "Vacio" en la base de CAFCI  ########################
clases_sin_patrimonio = basedia_hoy[basedia_hoy['patrimonio'].isna()]['clase_id'].unique()
clases_sin_patrimonio = pd.DataFrame(clases_sin_patrimonio)
clases_sin_patrimonio.columns = ['Clases sin Patrimonio (Vacio)']

##################### Clases cambio de tipo de renta  ########################
basedia_hoy.loc[basedia_hoy['clasi_nombre'] == 'Retorno Total', 'clasi_nombre'] = 'Renta Mixta'  # Reemplazo Retorno Total por Renta Mixta
df1 = pd.merge(basedia_hoy[['clasi_nombre', 'clase_id']], equivalencias[['clasi_nombre', 'clase_id']],
               on='clase_id', suffixes=('_df1', '_df2'))

# Filtrar las filas donde las clases sean diferentes
df2 = df1.loc[df1['clasi_nombre_df1'] != df1['clasi_nombre_df2'], 'clase_id']
df2 = pd.DataFrame(df2)
df2.columns = ['clase_id']
df1 = pd.merge(basedia_hoy[['clasi_nombre', 'clase_id']], df2[['clase_id']], on='clase_id')
df1 = df1.drop(df1[(df1['clasi_nombre'] == 'RG900')].index)  # Eliminar las filas donde los valores de las columnas sean "R9600"
clases_renta_diferente = df1.rename(columns={'clase_id': 'Clases con renta diferente', 'clasi_nombre': 'Renta Base Cafci'})

##################### Clases cambio de moneda  ################################
df1 = pd.merge(basedia_hoy[['moneda_cod', 'clase_id']], equivalencias[['moneda', 'clase_id']], on='clase_id')

# Filtrar las filas donde las monedas sean diferentes
df2 = df1.loc[df1['moneda_cod'] != df1['moneda'], 'clase_id']

df2 = pd.DataFrame(df2)
df2.columns = ['clase_id']
df1 = pd.merge(basedia_hoy[['moneda_cod', 'clase_id']], df2[['clase_id']], on='clase_id')
clases_moneda_diferente = df1.rename(columns={'clase_id': 'Clases con moneda diferente', 'moneda_cod': 'Moneda Base Cafci'})

end_time = time.time()
total_time3 = end_time - start_time
print("Tiempo total de procesamiento controles: ", round(total_time3, 4), "segundos")

########################################################################################################################
#############################               CONCATENADO                   ##############################################
########################################################################################################################
start_time = time.time()
concat_princip_basedia = pd.concat([principal, basedia], axis=0)
concat_princip_basedia.sort_values(by='fecha', ascending=True, inplace=True)
concat_princip_basedia = concat_princip_basedia.reset_index()

concat_princip_basedia.drop(['index'], axis=1, inplace=True)  # Eliminar la columna index

# Repetir la informacion de t-1 en t para las clases que no informaron
concat_princip_basedia_undia = concat_princip_basedia[concat_princip_basedia.fecha.dt.date == undia].copy()  # Creo una copia del concat de t-1
concat_princip_basedia_undia.fecha = fecha_informe
concat_princip_basedia_undia.fecha_carga = calculo_fechas.iloc[1, 1].date()  # Pongo la fecha de t-1 en fecha carga
# filtro las CLASES QUE NO INFORMARON en CAFCI en la el principal de t-1
concat_princip_basedia_undia = concat_princip_basedia_undia[concat_princip_basedia_undia['clase_id'].isin(clases_noinformaron['Clases que no informaron'])]
concat_princip_basedia_undia = concat_princip_basedia_undia.reset_index(drop=True)
# Concateno la infomracion en la base día
concat_princip_basedia = pd.concat([concat_princip_basedia, concat_princip_basedia_undia]).fillna(0)  # concateno los df
concat_princip_basedia["fecha"] = pd.to_datetime(concat_princip_basedia["fecha"])   # Le quito la hora a la fecha
concat_princip_basedia["fecha_carga"] = pd.to_datetime(concat_princip_basedia["fecha_carga"])  # Le quito la hora a la fecha
concat_princip_basedia.drop_duplicates(subset=['clase_id', 'fecha', 'fecha_carga'], keep='last', inplace=True)

'''
# Repetir la informacion de t-1 en t para las clases que no tiene patrimonio 0
concat_princip_basedia_undia_2 = concat_princip_basedia[concat_princip_basedia.fecha.dt.date == undia].copy()  # Creo una copia del concat de t-1
concat_princip_basedia_undia_2.fecha = fecha_informe
concat_princip_basedia_undia_2.fecha_carga = calculo_fechas.iloc[1, 1].date()
# filtro las CLASES QUE NO INFORMARON PATRIMONIO (PATRIMONIO == 0) en CAFCI en la el principal de t-1
concat_princip_basedia_undia_2 = concat_princip_basedia_undia_2[concat_princip_basedia_undia_2['clase_id'].isin(clases_sin_patrimonio['Clases sin Patrimonio (Vacio)'])]
concat_princip_basedia_undia_2 = concat_princip_basedia_undia_2.reset_index(drop=True)
concat_princip_basedia = pd.concat([concat_princip_basedia, concat_princip_basedia_undia_2]).fillna(0)  # concateno los df
concat_princip_basedia["fecha_carga"] = pd.to_datetime(concat_princip_basedia["fecha_carga"])   # Le quito la hora a la fecha
'''
end_time = time.time()
total_time4 = end_time - start_time
print("Tiempo total de procesamiento concatenado: ", round(total_time4, 4), "segundos")

########################################################################################################################
#############################           PARTICIONES DEL PRINCIPAL         ##############################################
########################################################################################################################
start_time = time.time()
def get_data_for_date(date_string):
  date = pd.to_datetime(date_string).date()
  filtered_data = concat_princip_basedia[(pd.to_datetime(concat_princip_basedia["fecha"]).dt.date == date)]
  filtered_data.reset_index(drop=True, inplace=True)
  return filtered_data

fecha_informe = pd.to_datetime(fecha_informe, format='%Y-%m-%d')
principal_daily = get_data_for_date(fecha_informe)
principal_undia = get_data_for_date(undia)
principal_mtd = get_data_for_date(Month_to_date)
principal_30_DAYS = get_data_for_date(treintadias)
principal_3Month = get_data_for_date(noventadias)
principal_6Month = get_data_for_date(cientoochentadias)
principal_YTD = get_data_for_date(Year_to_date)
principal_12Month = get_data_for_date(tressesentadias)

end_time = time.time()
total_time5 = end_time - start_time
print("Tiempo total de procesamiento particiones principal: ", round(total_time5, 4), "segundos")

########################################################################################################################
#############################                BENCHMARK              ####################################################
########################################################################################################################
########################## Lectura de Benchmark ################################
start_time = time.time()
benchmark = pd.read_excel(r"C:\Rubén\Fondos\Informe\Benchmark informe.xls",
                          skiprows=5, header=None)
#Filtro las ultimas 370 filas
benchmark = benchmark.tail(370)
# Elimina las columnas con fecha menos la primera que uso de indice y las columnas que tienen en TODAS las columnas NaN
# Agrego la columna 0 porque la omiti en [:1]
columnas_a_omitir = (
    benchmark.select_dtypes(include='datetime64').columns.tolist()[1:] +
    benchmark.columns[benchmark.isna().all()].tolist() +
    [benchmark.columns[0]]
)

# Obtiene las columnas a mantener
columnas_a_mantener = [columna for columna in benchmark.columns if columna not in columnas_a_omitir]

# Crea un nuevo DataFrame sin las columnas vacías
benchmark = benchmark[columnas_a_mantener]

nombres_columnas = [
    'fecha', 'MERVAL Index', 'bna', 'dti', 'ccl', 'IBOV $', 'INDU Index', 'SX5P Index', 'BADLARPP Index',
    'ARDRT30P Index', 'EUR Curncy', 'BRL Curncy', 'GT2 Govt', 'ACERCER Index', 'GOLDS Comdty', 'IBOV Index',
    'IBOV USD', 'USIBOV Equity', 'IAMCCOPP Index', 'IAMCCODD Index', 'ALRECNC AR Equity', 'BWMING Index', 'BWAGRI Index',
    'BWOILP Index', 'Benchmark RRNN', 'Benchmark RRNN ARS', 'IAMCGRAD Index', 'Benchmark MIX',
    'MAR Index', 'MAR Index USD', 'IAMCLAPP Index', 'IAMCCOPP Index', 'IAMCLADD Index', 'IAMCCODD Index',
    'IAMCCODD Index ARS', 'IGSB US Equity', 'ARS BNAG Curncy', '.FXIMPL Index', 'EURUSD Curncy', 'IAMCCODP Index',
    'IAMCLADP Index', 'IAMCCOPD Index', 'IAMCLAPD Index', 'LQD US Equity', 'IEF US Equity', 'PFF US Equity',
    '.BWOILP en AR$', 'Benchmark RRNN NEW', 'Benchmark Mercosur NEW', '1784AHP Equity', 'ARDRARPP Index',
    'IAMCGRAP Index', 'ILF Equity', 'ILF Equity ARS']

# Renombrar las columnas del DataFrame
benchmark.columns = nombres_columnas


end_time = time.time()
total_time6 = end_time - start_time
print("Tiempo total de procesamiento Benchmark: ", round(total_time6, 4), "segundos")
########################################################################################################################
#############################                BNA Y DTI              ####################################################
########################################################################################################################
start_time = time.time()
fecha_informe = fecha_informe.date()
fecha_informe_bna, fecha_undia_bna, fecha_mtd_bna, fecha_treinta_bna, fecha_noventa_bna, fecha_cientoochenta_bna, fecha_ytd_bna, fecha_tressesenta_bna = [0] * 8
fecha_informe_dti, fecha_undia_dti, fecha_mtd_dti, fecha_treinta_dti, fecha_noventa_dti, fecha_cientoochenta_dti, fecha_ytd_dti, fecha_tressesenta_dti = [0] * 8

fechas_tc = [
    (fecha_informe, 'fecha_informe'),
    (undia, 'fecha_undia'),
    (Month_to_date, 'fecha_mtd'),
    (treintadias, 'fecha_treinta'),
    (noventadias, 'fecha_noventa'),
    (cientoochentadias, 'fecha_cientoochenta'),
    (Year_to_date, 'fecha_ytd'),
    (tressesentadias, 'fecha_tressesenta')
]

tc_fechas = benchmark.loc[benchmark['fecha'].isin([pd.Timestamp(fecha[0]).date() for fecha in fechas_tc]), ['fecha', 'bna', 'dti']]

valores = []
for fecha, variable in fechas_tc:
    valor, dti = tc_fechas.loc[tc_fechas['fecha'].dt.date == pd.Timestamp(fecha).date(), ['bna', 'dti']].values[0]
    exec(f"{variable}_bna= {valor}")
    exec(f"{variable}_dti = {dti}")

# Crear una lista con las variables
variables_bna = [fecha_informe_bna, fecha_undia_bna, fecha_mtd_bna, fecha_treinta_bna, fecha_noventa_bna,
                 fecha_cientoochenta_bna, fecha_ytd_bna, fecha_tressesenta_bna]

# Desempaquetar los valores de la lista en variables separadas
(fecha_informe_bna, fecha_undia_bna, fecha_mtd_bna, fecha_treinta_bna, fecha_noventa_bna,
 fecha_cientoochenta_bna, fecha_ytd_bna, fecha_tressesenta_bna) = variables_bna

calculo_fechas["BNA"] = variables_bna

# DTI
# Crear una lista con las variables de interés
variables_dti = [fecha_informe_dti, fecha_undia_dti, fecha_mtd_dti, fecha_treinta_dti, fecha_noventa_dti,
                 fecha_cientoochenta_dti, fecha_ytd_dti, fecha_tressesenta_dti]

# Desempaquetar los valores de la lista en variables separadas
(fecha_informe_dti, fecha_undia_dti, fecha_mtd_dti, fecha_treinta_dti, fecha_noventa_dti,
 fecha_cientoochenta_dti, fecha_ytd_dti, fecha_tressesenta_dti) = variables_dti

calculo_fechas["DTI"] = variables_dti

############## Calculo de variciones BNA y DTI  ##############

# Variaciones Relativas BNA
def var_rel(valor1, valor2):
    return (valor1 / valor2) - 1

# Calculo las var rel BNA en base al fecha informe
var_bna_fechainforme = var_rel(fecha_informe_bna, fecha_informe_bna)
var_bna_undia = var_rel(fecha_informe_bna, fecha_undia_bna)
var_bna_mtd = var_rel(fecha_informe_bna, fecha_mtd_bna)
var_bna_treinta = var_rel(fecha_informe_bna, fecha_treinta_bna)
var_bna_noventa = var_rel(fecha_informe_bna, fecha_noventa_bna)
var_bna_cientoochenta = var_rel(fecha_informe_bna, fecha_cientoochenta_bna)
var_bna_ytd = var_rel(fecha_informe_bna, fecha_ytd_bna)

var_bna_tressesenta = var_rel(fecha_informe_bna, fecha_tressesenta_bna)

var_dti_fechainforme = var_rel(fecha_informe_dti, fecha_informe_dti)
var_dti_undia = var_rel(fecha_informe_dti, fecha_undia_dti)
var_dti_mtd = var_rel(fecha_informe_dti, fecha_mtd_dti)
var_dti_treinta = var_rel(fecha_informe_dti, fecha_treinta_dti)
var_dti_noventa = var_rel(fecha_informe_dti, fecha_noventa_dti)
var_dti_cientoochenta = var_rel(fecha_informe_dti, fecha_cientoochenta_dti)
var_dti_ytd = var_rel(fecha_informe_dti, fecha_ytd_dti)
var_dti_tressesenta = var_rel(fecha_informe_dti, fecha_tressesenta_dti)

#Exporto las variaciones a una lista
var_bna = [var_bna_fechainforme, var_bna_undia, var_bna_mtd, var_bna_treinta, var_bna_noventa,
           var_bna_cientoochenta, var_bna_ytd, var_bna_tressesenta]
calculo_fechas["Var_BNA"] = var_bna

var_dti = [var_dti_fechainforme, var_dti_undia, var_dti_mtd, var_dti_treinta, var_dti_noventa,
           var_dti_cientoochenta, var_dti_ytd, var_dti_tressesenta]
calculo_fechas["Var_DTI"] = var_dti

#Variaciones relativas Anualizadas BNA
def var_rel_anualizado(valor1):
    return ((1+valor1)**365) - 1
# Calculo las var rel anulizada
var_anualizada_bna_fechainforme = var_rel_anualizado(var_bna_fechainforme)
var_anualizada_bna_undia = var_rel_anualizado(var_bna_undia/dif_1)
var_anualizada_bna_mtd = var_rel_anualizado(var_bna_mtd/dif_mtd)
var_anualizada_bna_treinta = var_rel_anualizado(var_bna_treinta/dif_30)
var_anualizada_bna_noventa = var_rel_anualizado(var_bna_noventa/dif_90)
var_anualizada_bna_cientoochenta = var_rel_anualizado(var_bna_cientoochenta/dif_180)
var_anualizada_bna_ytd = var_rel_anualizado(var_bna_ytd/dif_ytd)
var_anualizada_bna_tressesenta = var_rel_anualizado(var_bna_tressesenta/dif_360)
var_anualizada_dti_fechainforme = var_rel_anualizado(var_dti_fechainforme)
var_anualizada_dti_undia = var_rel_anualizado(var_dti_undia/dif_1)
var_anualizada_dti_mtd = var_rel_anualizado(var_dti_mtd/dif_mtd)
var_anualizada_dti_treinta = var_rel_anualizado(var_dti_treinta/dif_30)
var_anualizada_dti_noventa = var_rel_anualizado(var_dti_noventa/dif_90)
var_anualizada_dti_cientoochenta = var_rel_anualizado(var_dti_cientoochenta/dif_180)
var_anualizada_dti_ytd = var_rel_anualizado(var_dti_ytd/dif_ytd)
var_anualizada_dti_tressesenta = var_rel_anualizado(var_dti_tressesenta/dif_360)

#Exporto las variaciones a una lista
var_anualizada_bna = [var_anualizada_bna_fechainforme, var_anualizada_bna_undia, var_anualizada_bna_mtd,
                      var_anualizada_bna_treinta, var_anualizada_bna_noventa, var_anualizada_bna_cientoochenta,
                      var_anualizada_bna_ytd, var_anualizada_bna_tressesenta]
calculo_fechas["Var_Anualizada_BNA"] = var_anualizada_bna

var_anualizada_dti = [var_anualizada_dti_fechainforme, var_anualizada_dti_undia, var_anualizada_dti_mtd,
                      var_anualizada_dti_treinta, var_anualizada_dti_noventa, var_anualizada_dti_cientoochenta,
                      var_anualizada_dti_ytd, var_anualizada_dti_tressesenta]
calculo_fechas["Var_Anualizada_DTI"] = var_anualizada_dti

# Delta DTI-BNA
dti_bna_fechainforme = fecha_informe_dti/fecha_informe_bna - 1
dti_bna_undia = fecha_undia_dti/fecha_undia_bna - 1
dti_bna_mtd = fecha_mtd_dti/fecha_mtd_bna - 1
dti_bna_treinta = fecha_treinta_dti/fecha_treinta_bna - 1
dti_bna_noventa = fecha_noventa_dti/fecha_noventa_bna - 1
dti_bna_cientoochenta = fecha_cientoochenta_dti/fecha_cientoochenta_bna - 1
dti_bna_ytd = fecha_ytd_dti/fecha_ytd_bna - 1
dti_bna_tressesenta = fecha_tressesenta_dti/fecha_tressesenta_bna - 1

delta_dti_bna = [dti_bna_fechainforme, dti_bna_undia, dti_bna_mtd, dti_bna_treinta, dti_bna_noventa,
                 dti_bna_cientoochenta, dti_bna_ytd, dti_bna_tressesenta]

(dti_bna_fechainforme, dti_bna_undia, dti_bna_mtd, dti_bna_treinta, dti_bna_noventa,
 dti_bna_cientoochenta, dti_bna_ytd, dti_bna_tressesenta) = delta_dti_bna
calculo_fechas["Delta_DTI/BNA"] = delta_dti_bna

end_time = time.time()
total_time7 = end_time - start_time
print("Tiempo total de procesamiento BNA/DTI: ", round(total_time7, 4), "segundos")

########################################################################################################################
#############################           MATRICES AUM Y RENDIMIENTOS         ############################################
########################################################################################################################
start_time = time.time()
clases = pd.DataFrame(equivalencias[["clase_id", "clase_nombre", "sg_id", "sociedad_gerente",
                                     "segmento_cajon", "clasi_nombre", "moneda"]])

# Creo Dataframe de los clases y patrimonios
principal_aum_daily = pd.DataFrame(principal_daily[['clase_id', 'patrimonio']])
principal_aum_undia = pd.DataFrame(principal_undia[['clase_id', 'patrimonio']])
principal_aum_mtd = pd.DataFrame(principal_mtd[['clase_id', 'patrimonio']])
principal_aum_30_DAYS = pd.DataFrame(principal_30_DAYS[['clase_id', 'patrimonio']])
principal_aum_3Month = pd.DataFrame(principal_3Month[['clase_id', 'patrimonio']])
principal_aum_6Month = pd.DataFrame(principal_6Month[['clase_id', 'patrimonio']])
principal_aum_YTD = pd.DataFrame(principal_YTD[['clase_id', 'patrimonio']])
principal_aum_12Month = pd.DataFrame(principal_12Month[['clase_id', 'patrimonio']])

#Merge de AUM en base a las clases de equivalencias

matriz = pd.merge(clases, principal_aum_daily, on='clase_id', how='left')
matriz = matriz.merge(principal_aum_undia, on='clase_id', how='left')
matriz = matriz.rename(columns={'patrimonio_x': 'AUM_daily', 'patrimonio_y': 'AUM_un_dia'})
matriz = matriz.merge(principal_aum_mtd, on='clase_id', how='left').rename(columns={'patrimonio': 'AUM_mtd'})
matriz = matriz.merge(principal_aum_30_DAYS, on='clase_id', how='left').rename(columns={'patrimonio': 'AUM_30_dias'})
matriz = matriz.merge(principal_aum_3Month, on='clase_id', how='left').rename(columns={'patrimonio': 'AUM_3_meses'})
matriz = matriz.merge(principal_aum_6Month, on='clase_id', how='left').rename(columns={'patrimonio': 'AUM_6_meses'})
matriz = matriz.merge(principal_aum_YTD, on='clase_id', how='left').rename(columns={'patrimonio': 'AUM_ytd'})
matriz = matriz.merge(principal_aum_12Month, on='clase_id', how='left').rename(columns={'patrimonio': 'AUM_12_meses'})
matriz = matriz.fillna(0)

# Cálculo de Variaciones AUM
matriz['var_aum_1_dia'] = (matriz['AUM_daily'] - matriz['AUM_un_dia'])
matriz['var_aum_mtd'] = (matriz['AUM_daily'] - matriz['AUM_mtd'])
matriz['var_aum_30_dias'] = (matriz['AUM_daily'] - matriz['AUM_30_dias'])
matriz['var_aum_3_meses'] = (matriz['AUM_daily'] - matriz['AUM_3_meses'])
matriz['var_aum_6_meses'] = (matriz['AUM_daily'] - matriz['AUM_6_meses'])
matriz['var_aum_ytd'] = (matriz['AUM_daily'] - matriz['AUM_ytd'])
matriz['var_aum_12_meses'] = (matriz['AUM_daily'] - matriz['AUM_12_meses'])

# Creo Dataframe de los clases y VCP
basedia_vcp_fechainforme = pd.DataFrame(basedia[['clase_id', 'compute_0013']])
principal_vcp_undia = pd.DataFrame(principal_undia[['clase_id', 'compute_0013']])
principal_vcp_mtd = pd.DataFrame(principal_mtd[['clase_id', 'compute_0013']])
principal_vcp_30_DAYS = pd.DataFrame(principal_30_DAYS[['clase_id', 'compute_0013']])
principal_vcp_3Month = pd.DataFrame(principal_3Month[['clase_id', 'compute_0013']])
principal_vcp_6Month = pd.DataFrame(principal_6Month[['clase_id', 'compute_0013']])
principal_vcp_YTD = pd.DataFrame(principal_YTD[['clase_id', 'compute_0013']])
principal_vcp_12Month = pd.DataFrame(principal_12Month[['clase_id', 'compute_0013']])

matriz = pd.merge(matriz, basedia_vcp_fechainforme, on='clase_id', how='left').rename(columns={'compute_0013': 'VCP_daily'})
matriz = matriz.merge(principal_vcp_undia, on='clase_id', how='left').rename(columns={'compute_0013': 'VCP_undia'})
matriz = matriz.merge(principal_vcp_mtd, on='clase_id', how='left').rename(columns={'compute_0013': 'VCP_mtd'})
matriz = matriz.merge(principal_vcp_30_DAYS, on='clase_id', how='left').rename(columns={'compute_0013': 'VCP_30dias'})
matriz = matriz.merge(principal_vcp_3Month, on='clase_id', how='left').rename(columns={'compute_0013': 'VCP_3meses'})
matriz = matriz.merge(principal_vcp_6Month, on='clase_id', how='left').rename(columns={'compute_0013': 'VCP_6meses'})
matriz = matriz.merge(principal_vcp_YTD, on='clase_id', how='left').rename(columns={'compute_0013': 'VCP_YTD'})
matriz = matriz.merge(principal_vcp_12Month, on='clase_id', how='left').rename(columns={'compute_0013': 'VCP_12meses'})

matriz["rend_1_dia"] = matriz.apply(lambda x: ((x['VCP_daily']/x['VCP_undia'])-1)*365/dif_1 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_undia'])-1), axis=1)
matriz["rend_vcp_mtd"] = matriz.apply(lambda x: ((x['VCP_daily']/x['VCP_mtd'])-1)*365/dif_mtd if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_mtd'])-1), axis=1)
matriz["rend_vcp_30_dias"] = matriz.apply(lambda x: ((x['VCP_daily']/x['VCP_30dias'])-1)*365/dif_30 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_30dias'])-1), axis=1)
matriz["rend_vcp_3_meses"] = matriz.apply(lambda x: ((x['VCP_daily']/x['VCP_3meses'])-1)*365/dif_90 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_3meses'])-1), axis=1)
matriz["rend_vcp_6_meses"] = matriz.apply(lambda x: ((x['VCP_daily']/x['VCP_6meses'])-1)*365/dif_180 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_6meses'])-1), axis=1)
matriz["rend_vcp_ytd"] = matriz.apply(lambda x: ((x['VCP_daily']/x['VCP_YTD'])-1)*365/dif_ytd if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_YTD'])-1), axis=1)
matriz["rend_vcp_12_meses"] = matriz.apply(lambda x: ((x['VCP_daily']/x['VCP_12meses'])-1)*365/dif_360 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_12meses'])-1), axis=1)

#Genero una matriz copia que contenga las clases que presentaron y luego calculo el rto ponderado del cajon
clases_noinformaron = clases_noinformaron.values.tolist()  # Conviertor el df en una lista
condiciones = [item for sublist in clases_noinformaron for item in sublist] # Convierte la lista de condiciones en una lista plana
clases_noinformaron = pd.DataFrame(clases_noinformaron, columns = ['Clases que no informaron'])

# Matriz SIN las clases que no presentaron. La uso para calcular el rto ponderado SIN las clases que no presentaron
matriz_copia = matriz.copy()
matriz_copia = matriz_copia[~matriz_copia['clase_id'].isin(condiciones)]
matriz_copia["rend_1_dia"] = matriz_copia.apply(lambda x: (x['VCP_daily'] / x['VCP_undia']) - 1, axis=1)
rendimiento_ponderado_cajon_daily = matriz_copia.groupby('segmento_cajon').apply(lambda x: ((x['rend_1_dia'] * x['AUM_daily']).sum() / x['AUM_daily'].sum()) if x['AUM_daily'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_daily.columns = ['segmento_cajon', 'Rto_ponderado_daily']

# Submatriz con las clases que no informaron. Calculo el VCP estimado en base a VCPt-2 * (1+rto ponderado)
matriz_copia_2 = matriz[['clase_id', 'segmento_cajon', 'VCP_undia']].loc[matriz['clase_id'].isin(condiciones)]
matriz_copia_2 = pd.merge(matriz_copia_2, rendimiento_ponderado_cajon_daily,  on='segmento_cajon', how='left')
matriz_copia_2['VCP_daily'] = matriz_copia_2['VCP_undia'] * (1 + matriz_copia_2['Rto_ponderado_daily'])
matriz_copia_2 = pd.DataFrame(matriz_copia_2[['clase_id', 'VCP_daily']])

df_merged = pd.merge(matriz, matriz_copia_2, on='clase_id', how='left')
# Actualizar los valores de 'AUM' en df_merged usando los valores de df1
df_merged['VCP_daily_x'].update(df_merged['VCP_daily_y'])
df_merged = df_merged.drop(columns=['VCP_daily_y']).rename(columns={'VCP_daily_x': 'VCP_daily'})  # Elimino la columna "VCP_daily_y" que esta desactualizada

# Ordenar las columnas para que coincidan con el orden de df2
df_merged = df_merged[matriz.columns]
matriz = df_merged

#Recalculo los rendimientos con los VCP estimados
matriz["rend_1_dia"] = matriz.apply(lambda x: ((x['VCP_daily']/x['VCP_undia'])-1)*365/dif_1 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_undia'])-1), axis=1)
matriz["rend_vcp_mtd"] = matriz.apply(lambda x: ((x['VCP_daily']/x['VCP_mtd'])-1)*365/dif_mtd if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_mtd'])-1), axis=1)
matriz["rend_vcp_30_dias"] = matriz.apply(lambda x: ((x['VCP_daily']/x['VCP_30dias'])-1)*365/dif_30 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_30dias'])-1), axis=1)
matriz["rend_vcp_3_meses"] = matriz.apply(lambda x: ((x['VCP_daily']/x['VCP_3meses'])-1)*365/dif_90 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_3meses'])-1), axis=1)
matriz["rend_vcp_6_meses"] = matriz.apply(lambda x: ((x['VCP_daily']/x['VCP_6meses'])-1)*365/dif_180 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_6meses'])-1), axis=1)
matriz["rend_vcp_ytd"] = matriz.apply(lambda x: ((x['VCP_daily']/x['VCP_YTD'])-1)*365/dif_ytd if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_YTD'])-1), axis=1)
matriz["rend_vcp_12_meses"] = matriz.apply(lambda x: ((x['VCP_daily']/x['VCP_12meses'])-1)*365/dif_360 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_12meses'])-1), axis=1)

end_time = time.time()
total_time8 = end_time - start_time
print("Tiempo total de procesamiento Matriz MO: ", round(total_time8, 4), "segundos")
#############################                   MATRIZ ARS                  ############################################
start_time = time.time()
#Obtengo el TC BNA de la fecha del informe:
tipo_de_cambio_bna = benchmark['bna'].iloc[-1]

# Arranco la matriz ARS
matriz_ars = pd.DataFrame()
matriz_ars = matriz.loc[:, ['clase_id', 'clase_nombre', 'sg_id', 'sociedad_gerente', 'segmento_cajon', 'clasi_nombre', 'moneda']]
matriz_ars = matriz_ars.fillna(0)

#Extraer el AUM de los fondos dolares y pesificarlos
matriz_ars['AUM_daily'] = matriz.apply(lambda x: x['AUM_daily'] * tipo_de_cambio_bna if x['moneda'] == 'USD' else x['AUM_daily'], axis=1)
matriz_ars['AUM_un_dia'] = matriz.apply(lambda x: x['AUM_un_dia'] * float(fecha_undia_bna) if x['moneda'] == 'USD' else x['AUM_un_dia'], axis=1)
matriz_ars['AUM_mtd'] = matriz.apply(lambda x: x['AUM_mtd'] * float(fecha_mtd_bna) if x['moneda'] == 'USD' else x['AUM_mtd'], axis=1)
matriz_ars['AUM_30_dias'] = matriz.apply(lambda x: x['AUM_30_dias'] * float(fecha_treinta_bna) if x['moneda'] == 'USD' else x['AUM_30_dias'], axis=1)
matriz_ars['AUM_3_meses'] = matriz.apply(lambda x: x['AUM_3_meses'] * float(fecha_noventa_bna) if x['moneda'] == 'USD' else x['AUM_3_meses'], axis=1)
matriz_ars['AUM_6_meses'] = matriz.apply(lambda x: x['AUM_6_meses'] * float(fecha_cientoochenta_bna) if x['moneda'] == 'USD' else x['AUM_6_meses'], axis=1)
matriz_ars['AUM_ytd'] = matriz.apply(lambda x: x['AUM_ytd'] * float(fecha_ytd_bna) if x['moneda'] == 'USD' else x['AUM_ytd'], axis=1)
matriz_ars['AUM_12_meses'] = matriz.apply(lambda x: x['AUM_12_meses'] * float(fecha_tressesenta_bna) if x['moneda'] == 'USD' else x['AUM_12_meses'], axis=1)

# Calculo de Var Abs de AUM
matriz_ars['var_aum_1_dia'] = (matriz_ars['AUM_daily'] - matriz_ars['AUM_un_dia'])
matriz_ars['var_aum_mtd'] = (matriz_ars['AUM_daily'] - matriz_ars['AUM_mtd'])
matriz_ars['var_aum_30_dias'] = (matriz_ars['AUM_daily'] - matriz_ars['AUM_30_dias'])
matriz_ars['var_aum_3_meses'] = (matriz_ars['AUM_daily'] - matriz_ars['AUM_3_meses'])
matriz_ars['var_aum_6_meses'] = (matriz_ars['AUM_daily'] - matriz_ars['AUM_6_meses'])
matriz_ars['var_aum_ytd'] = (matriz_ars['AUM_daily'] - matriz_ars['AUM_ytd'])
matriz_ars['var_aum_12_meses'] = (matriz_ars['AUM_daily'] - matriz_ars['AUM_12_meses'])

# Extraer el VCP de los fondos dolares y pesificarlos
matriz_ars['VCP_daily'] = matriz.apply(lambda x: x['VCP_daily'] * tipo_de_cambio_bna if x['moneda'] == 'USD' else x['VCP_daily'], axis=1)
matriz_ars['VCP_undia'] = matriz.apply(lambda x: x['VCP_undia'] * float(fecha_undia_bna) if x['moneda'] == 'USD' else x['VCP_undia'], axis=1)
matriz_ars['VCP_mtd'] = matriz.apply(lambda x: x['VCP_mtd'] * float(fecha_mtd_bna) if x['moneda'] == 'USD' else x['VCP_mtd'], axis=1)
matriz_ars['VCP_30dias'] = matriz.apply(lambda x: x['VCP_30dias'] * float(fecha_treinta_bna) if x['moneda'] == 'USD' else x['VCP_30dias'], axis=1)
matriz_ars['VCP_3meses'] = matriz.apply(lambda x: x['VCP_3meses'] * float(fecha_noventa_bna) if x['moneda'] == 'USD' else x['VCP_3meses'], axis=1)
matriz_ars['VCP_6meses'] = matriz.apply(lambda x: x['VCP_6meses'] * float(fecha_cientoochenta_bna) if x['moneda'] == 'USD' else x['VCP_6meses'], axis=1)
matriz_ars['VCP_YTD'] = matriz.apply(lambda x: x['VCP_YTD'] * float(fecha_ytd_bna) if x['moneda'] == 'USD' else x['VCP_YTD'], axis=1)
matriz_ars['VCP_12meses'] = matriz.apply(lambda x: x['VCP_12meses'] * float(fecha_tressesenta_bna) if x['moneda'] == 'USD' else x['VCP_12meses'], axis=1)

# Calculo de Rendimientos
matriz_ars["rend_1_dia"] = matriz_ars.apply(lambda x: ((x['VCP_daily']/x['VCP_undia'])-1)*365/dif_1 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_undia'])-1), axis=1)
matriz_ars["rend_vcp_mtd"] = matriz_ars.apply(lambda x: ((x['VCP_daily']/x['VCP_mtd'])-1)*365/dif_mtd if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_mtd'])-1), axis=1)
matriz_ars["rend_vcp_30_dias"] = matriz_ars.apply(lambda x: ((x['VCP_daily']/x['VCP_30dias'])-1)*365/dif_30 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_30dias'])-1), axis=1)
matriz_ars["rend_vcp_3_meses"] = matriz_ars.apply(lambda x: ((x['VCP_daily']/x['VCP_3meses'])-1)*365/dif_90 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_3meses'])-1), axis=1)
matriz_ars["rend_vcp_6_meses"] = matriz_ars.apply(lambda x: ((x['VCP_daily']/x['VCP_6meses'])-1)*365/dif_180 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_6meses'])-1), axis=1)
matriz_ars["rend_vcp_ytd"] = matriz_ars.apply(lambda x: ((x['VCP_daily']/x['VCP_YTD'])-1)*365/dif_ytd if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_YTD'])-1), axis=1)
matriz_ars["rend_vcp_12_meses"] = matriz_ars.apply(lambda x: ((x['VCP_daily']/x['VCP_12meses'])-1)*365/dif_360 if x["clasi_nombre"] == "Mercado de Dinero" else ((x['VCP_daily']/x['VCP_12meses'])-1), axis=1)

end_time = time.time()
total_time9 = end_time - start_time
print("Tiempo total de procesamiento Matriz ARS: ", round(total_time9, 4), "segundos")

########################################################################################################################
#############################              FEES & CALIFICACIONES            ############################################
########################################################################################################################
start_time = time.time()
fees_calificaciones = pd.read_excel(r"C:\Users\lr110574\PycharmProjects\Informe_Diario\Fee_calificaciones.xlsx", sheet_name='Base 2023')
fees_calificaciones['Calificacion'] = fees_calificaciones['Calificacion'].fillna('NA')

matriz = pd.merge(matriz, fees_calificaciones[['clase_id', 'Fee FY', 'Calificacion', 'Fee 3M']], on='clase_id', how='left')
matriz_ars = pd.merge(matriz_ars, fees_calificaciones[['clase_id', 'Fee FY', 'Calificacion', 'Fee 3M']], on='clase_id', how='left')

fee_3m_prop = matriz_ars.loc[matriz_ars["clasi_nombre"] != "Mercado de Dinero", "Fee 3M"].copy() / 4
fee_ytd_prop = matriz_ars.loc[matriz_ars["clasi_nombre"] != "Mercado de Dinero", "Fee FY"].copy() * (dif_ytd/365)

matriz['rend_vcp_3_meses_bruto'] = np.where(matriz["clasi_nombre"] != "Mercado de Dinero",
                                            matriz['rend_vcp_3_meses'] + fee_3m_prop,
                                            matriz['rend_vcp_3_meses'] + matriz["Fee 3M"])

matriz['rend_vcp_ytd_bruto'] = np.where(matriz["clasi_nombre"] != "Mercado de Dinero",
                                        matriz['rend_vcp_ytd'] + fee_ytd_prop,
                                        matriz['rend_vcp_ytd'] + matriz["Fee FY"])

matriz_ars['rend_vcp_3_meses_bruto'] = np.where(matriz_ars["clasi_nombre"] != "Mercado de Dinero",
                                                matriz_ars['rend_vcp_3_meses'] + fee_3m_prop,
                                                matriz_ars['rend_vcp_3_meses'] + matriz_ars["Fee 3M"])

matriz_ars['rend_vcp_ytd_bruto'] = np.where(matriz_ars["clasi_nombre"] != "Mercado de Dinero",
                                            matriz_ars['rend_vcp_ytd'] + fee_ytd_prop,
                                            matriz_ars['rend_vcp_ytd'] + matriz_ars["Fee FY"])

end_time = time.time()
total_time10 = end_time - start_time
print("Tiempo total de procesamiento Fee & Calificaciones: ", round(total_time10, 4), "segundos")

########################################################################################################################
#############################              EVOLUCIÓN PATRIMONIAL            ############################################
########################################################################################################################
start_time = time.time()
evolucion_patrimonial = matriz_ars.groupby(['sg_id'])[['AUM_daily', 'AUM_un_dia', 'AUM_mtd', 'AUM_30_dias',
                                                       'AUM_3_meses', 'AUM_6_meses', 'AUM_ytd', 'AUM_12_meses']].sum()
evolucion_patrimonial['Variacion_diaria'] = (evolucion_patrimonial['AUM_daily']-evolucion_patrimonial['AUM_un_dia'])
evolucion_patrimonial['Variacion_diaria_%'] = (evolucion_patrimonial['AUM_daily']/evolucion_patrimonial['AUM_un_dia']-1)
evolucion_patrimonial['Variacion_MTD'] = (evolucion_patrimonial['AUM_daily']-evolucion_patrimonial['AUM_mtd'])
evolucion_patrimonial['Variacion_MTD_%'] = (evolucion_patrimonial['AUM_daily']/evolucion_patrimonial['AUM_mtd']-1)
evolucion_patrimonial['Variacion_YTD'] = (evolucion_patrimonial['AUM_daily']-evolucion_patrimonial['AUM_ytd'])
evolucion_patrimonial['Variacion_YTD_%'] = (evolucion_patrimonial['AUM_daily']/evolucion_patrimonial['AUM_ytd']-1)
evolucion_patrimonial = evolucion_patrimonial.sort_values('AUM_daily', ascending=False)
evolucion_patrimonial.replace([np.inf, -np.inf], np.nan, inplace=True)

evolucion_patrimonial.loc['Total'] = evolucion_patrimonial[['AUM_daily', 'AUM_un_dia', 'AUM_mtd', 'AUM_30_dias',
                                                           'AUM_3_meses', 'AUM_6_meses', 'AUM_ytd', 'AUM_12_meses',
                                                            'Variacion_diaria', 'Variacion_MTD', 'Variacion_YTD']].sum()

evolucion_patrimonial.loc['Total', 'Variacion_diaria_%'] = (evolucion_patrimonial.loc['Total', 'AUM_daily']/evolucion_patrimonial.loc['Total', 'AUM_un_dia'])-1
evolucion_patrimonial.loc['Total', 'Variacion_MTD_%'] = (evolucion_patrimonial.loc['Total', 'AUM_daily']/evolucion_patrimonial.loc['Total', 'AUM_mtd'])-1
evolucion_patrimonial.loc['Total', 'Variacion_YTD_%'] = (evolucion_patrimonial.loc['Total', 'AUM_daily']/evolucion_patrimonial.loc['Total', 'AUM_ytd'])-1

# Itero para calcular los aum por S.G.
for i, row in evolucion_patrimonial.iterrows():
    evolucion_patrimonial.at[i, 'MS_daily'] = row['AUM_daily'] / evolucion_patrimonial.loc['Total', 'AUM_daily']

for i, row in evolucion_patrimonial.iterrows():
    evolucion_patrimonial.at[i, 'MS_MTD'] = row['AUM_mtd'] / evolucion_patrimonial.loc['Total', 'AUM_mtd']

for i, row in evolucion_patrimonial.iterrows():
    evolucion_patrimonial.at[i, 'MS_YTD'] = row['AUM_ytd'] / evolucion_patrimonial.loc['Total', 'AUM_ytd']

evolucion_patrimonial = pd.merge(evolucion_patrimonial, matriz.groupby('sg_id').agg({'sociedad_gerente': 'first'}),
                                 on='sg_id', how='left')

evolucion_patrimonial = evolucion_patrimonial.iloc[:, [-1] + list(range(len(evolucion_patrimonial.columns)-1))]
#########################################################################################################################
# Evolución patrimonial MM
evolucion_patrimonial_MM = matriz_ars[matriz_ars['clasi_nombre'] == 'Mercado de Dinero'].groupby('sg_id')[['AUM_daily', 'AUM_un_dia', 'AUM_mtd', 'AUM_ytd']].sum()
evolucion_patrimonial_MM['Variacion_diaria'] = (evolucion_patrimonial_MM['AUM_daily']-evolucion_patrimonial_MM['AUM_un_dia'])
evolucion_patrimonial_MM['Variacion_diaria_%'] = (evolucion_patrimonial_MM['AUM_daily']/evolucion_patrimonial_MM['AUM_un_dia']-1)
evolucion_patrimonial_MM['Variacion_MTD'] = (evolucion_patrimonial_MM['AUM_daily']-evolucion_patrimonial_MM['AUM_mtd'])
evolucion_patrimonial_MM['Variacion_MTD_%'] = (evolucion_patrimonial_MM['AUM_daily']/evolucion_patrimonial_MM['AUM_mtd']-1)
evolucion_patrimonial_MM['Variacion_YTD'] = (evolucion_patrimonial_MM['AUM_daily']-evolucion_patrimonial_MM['AUM_ytd'])
evolucion_patrimonial_MM['Variacion_YTD_%'] = (evolucion_patrimonial_MM['AUM_daily']/evolucion_patrimonial_MM['AUM_ytd']-1)
evolucion_patrimonial_MM = evolucion_patrimonial_MM.sort_values('AUM_daily', ascending=False)
top20_MM = evolucion_patrimonial_MM.nlargest(20, 'AUM_daily')

# Sumar los valores del resto de los bancos en columnas específicas
resto_MM = evolucion_patrimonial_MM[~evolucion_patrimonial_MM.index.isin(top20_MM.index)][['AUM_daily', 'AUM_un_dia', 'AUM_mtd',
                                                                                           'AUM_ytd', 'Variacion_diaria',
                                                                                           'Variacion_MTD', 'Variacion_YTD']].sum()
# Agregar una fila para el resto de los S.G.
resto_MM.name = 'Otras'
evolucion_patrimonial_MM = pd.concat([top20_MM, resto_MM.to_frame().T])
evolucion_patrimonial_MM.loc['Total'] = evolucion_patrimonial_MM[['AUM_daily', 'AUM_un_dia', 'AUM_mtd',
                                                                  'AUM_ytd', 'Variacion_diaria',
                                                                  'Variacion_MTD', 'Variacion_YTD']].sum()

evolucion_patrimonial_MM.loc['Otras', 'Variacion_diaria_%'] = (evolucion_patrimonial_MM.loc['Otras', 'AUM_daily']/evolucion_patrimonial_MM.loc['Otras', 'AUM_un_dia'])-1
evolucion_patrimonial_MM.loc['Otras', 'Variacion_MTD_%'] = (evolucion_patrimonial_MM.loc['Otras', 'AUM_daily']/evolucion_patrimonial_MM.loc['Otras', 'AUM_mtd'])-1
evolucion_patrimonial_MM.loc['Otras', 'Variacion_YTD_%'] = (evolucion_patrimonial_MM.loc['Otras', 'AUM_daily']/evolucion_patrimonial_MM.loc['Otras', 'AUM_ytd'])-1
evolucion_patrimonial_MM.loc['Total', 'Variacion_diaria_%'] = (evolucion_patrimonial_MM.loc['Total', 'AUM_daily']/evolucion_patrimonial_MM.loc['Total', 'AUM_un_dia'])-1
evolucion_patrimonial_MM.loc['Total', 'Variacion_MTD_%'] = (evolucion_patrimonial_MM.loc['Total', 'AUM_daily']/evolucion_patrimonial_MM.loc['Total', 'AUM_mtd'])-1
evolucion_patrimonial_MM.loc['Total', 'Variacion_YTD_%'] = (evolucion_patrimonial_MM.loc['Total', 'AUM_daily']/evolucion_patrimonial_MM.loc['Total', 'AUM_ytd'])-1

# Itero para calcular los aum por banco
for i, row in evolucion_patrimonial_MM.iterrows():
    evolucion_patrimonial_MM.at[i, 'MS_daily'] = row['AUM_daily'] / evolucion_patrimonial_MM.loc['Total', 'AUM_daily']

for i, row in evolucion_patrimonial_MM.iterrows():
    evolucion_patrimonial_MM.at[i, 'MS_MTD'] = row['AUM_mtd'] / evolucion_patrimonial_MM.loc['Total', 'AUM_mtd']

for i, row in evolucion_patrimonial_MM.iterrows():
    evolucion_patrimonial_MM.at[i, 'MS_YTD'] = row['AUM_ytd'] / evolucion_patrimonial_MM.loc['Total', 'AUM_ytd']

evolucion_patrimonial_MM.insert(0, 'Tipo de Renta', 'Money Market')
evolucion_patrimonial_MM = evolucion_patrimonial_MM.rename_axis('sg_id')
evolucion_patrimonial_MM = pd.merge(evolucion_patrimonial_MM, matriz.groupby('sg_id').agg({'sociedad_gerente': 'first'}), on='sg_id', how='left')

evolucion_patrimonial_MM = evolucion_patrimonial_MM.iloc[:, [-1] + list(range(len(evolucion_patrimonial_MM.columns)-1))]
################################################################################################################################
# Evolución Patrimonial RF

evolucion_patrimonial_RF = matriz_ars[matriz_ars['clasi_nombre'] == 'Renta Fija'].groupby('sg_id')[['AUM_daily', 'AUM_un_dia', 'AUM_mtd', 'AUM_ytd']].sum()
evolucion_patrimonial_RF['Variacion_diaria'] = (evolucion_patrimonial_RF['AUM_daily']-evolucion_patrimonial_RF['AUM_un_dia'])
evolucion_patrimonial_RF['Variacion_diaria_%'] = (evolucion_patrimonial_RF['AUM_daily']/evolucion_patrimonial_RF['AUM_un_dia']-1)
evolucion_patrimonial_RF['Variacion_MTD'] = (evolucion_patrimonial_RF['AUM_daily']-evolucion_patrimonial_RF['AUM_mtd'])
evolucion_patrimonial_RF['Variacion_MTD_%'] = (evolucion_patrimonial_RF['AUM_daily']/evolucion_patrimonial_RF['AUM_mtd']-1)
evolucion_patrimonial_RF['Variacion_YTD'] = (evolucion_patrimonial_RF['AUM_daily']-evolucion_patrimonial_RF['AUM_ytd'])
evolucion_patrimonial_RF['Variacion_YTD_%'] = (evolucion_patrimonial_RF['AUM_daily']/evolucion_patrimonial_RF['AUM_ytd']-1)
evolucion_patrimonial_RF = evolucion_patrimonial_RF.sort_values('AUM_daily', ascending=False)
top20_RF = evolucion_patrimonial_RF.nlargest(20, 'AUM_daily')

# Sumar los valores del resto de los bancos en columnas específicas
resto_RF = evolucion_patrimonial_RF[~evolucion_patrimonial_RF.index.isin(top20_RF.index)][['AUM_daily', 'AUM_un_dia', 'AUM_mtd',
                                                                                           'AUM_ytd', 'Variacion_diaria',
                                                                                           'Variacion_MTD', 'Variacion_YTD']].sum()
# Agregar una fila para el resto de los bancos
resto_RF.name = 'Otras'
evolucion_patrimonial_RF = pd.concat([top20_RF, resto_RF.to_frame().T])
evolucion_patrimonial_RF.loc['Total'] = evolucion_patrimonial_RF[['AUM_daily', 'AUM_un_dia', 'AUM_mtd',
                                                                  'AUM_ytd', 'Variacion_diaria',
                                                                  'Variacion_MTD', 'Variacion_YTD']].sum()

evolucion_patrimonial_RF.loc['Otras', 'Variacion_diaria_%'] = (evolucion_patrimonial_RF.loc['Otras', 'AUM_daily']/evolucion_patrimonial_RF.loc['Otras', 'AUM_un_dia'])-1
evolucion_patrimonial_RF.loc['Otras', 'Variacion_MTD_%'] = (evolucion_patrimonial_RF.loc['Otras', 'AUM_daily']/evolucion_patrimonial_RF.loc['Otras', 'AUM_mtd'])-1
evolucion_patrimonial_RF.loc['Otras', 'Variacion_YTD_%'] = (evolucion_patrimonial_RF.loc['Otras', 'AUM_daily']/evolucion_patrimonial_RF.loc['Otras', 'AUM_ytd'])-1
evolucion_patrimonial_RF.loc['Total', 'Variacion_diaria_%'] = (evolucion_patrimonial_RF.loc['Total', 'AUM_daily']/evolucion_patrimonial_RF.loc['Total', 'AUM_un_dia'])-1
evolucion_patrimonial_RF.loc['Total', 'Variacion_MTD_%'] = (evolucion_patrimonial_RF.loc['Total', 'AUM_daily']/evolucion_patrimonial_RF.loc['Total', 'AUM_mtd'])-1
evolucion_patrimonial_RF.loc['Total', 'Variacion_YTD_%'] = (evolucion_patrimonial_RF.loc['Total', 'AUM_daily']/evolucion_patrimonial_RF.loc['Total', 'AUM_ytd'])-1

# Itero para calcular los aum por banco
for i, row in evolucion_patrimonial_RF.iterrows():
    evolucion_patrimonial_RF.at[i, 'MS_daily'] = row['AUM_daily'] / evolucion_patrimonial_RF.loc['Total', 'AUM_daily']

for i, row in evolucion_patrimonial_RF.iterrows():
    evolucion_patrimonial_RF.at[i, 'MS_MTD'] = row['AUM_mtd'] / evolucion_patrimonial_RF.loc['Total', 'AUM_mtd']

for i, row in evolucion_patrimonial_RF.iterrows():
    evolucion_patrimonial_RF.at[i, 'MS_YTD'] = row['AUM_ytd'] / evolucion_patrimonial_RF.loc['Total', 'AUM_ytd']


evolucion_patrimonial_RF.insert(0, 'Tipo de Renta', 'Renta Fija')
evolucion_patrimonial_RF = evolucion_patrimonial_RF.rename_axis('sg_id')
evolucion_patrimonial_RF = pd.merge(evolucion_patrimonial_RF, matriz.groupby('sg_id').agg({'sociedad_gerente': 'first'}), on='sg_id', how='left')
evolucion_patrimonial_RF = evolucion_patrimonial_RF.iloc[:, [-1] + list(range(len(evolucion_patrimonial_RF.columns)-1))]
################################################################################################################################
# Evolución Patrimonial RV
evolucion_patrimonial_RV = matriz_ars[matriz_ars['clasi_nombre'] == 'Renta Variable'].groupby('sg_id')[['AUM_daily', 'AUM_un_dia', 'AUM_mtd', 'AUM_ytd']].sum()
evolucion_patrimonial_RV['Variacion_diaria'] = (evolucion_patrimonial_RV['AUM_daily']-evolucion_patrimonial_RV['AUM_un_dia'])
evolucion_patrimonial_RV['Variacion_diaria_%'] = (evolucion_patrimonial_RV['AUM_daily']/evolucion_patrimonial_RV['AUM_un_dia']-1)
evolucion_patrimonial_RV['Variacion_MTD'] = (evolucion_patrimonial_RV['AUM_daily']-evolucion_patrimonial_RV['AUM_mtd'])
evolucion_patrimonial_RV['Variacion_MTD_%'] = (evolucion_patrimonial_RV['AUM_daily']/evolucion_patrimonial_RV['AUM_mtd']-1)
evolucion_patrimonial_RV['Variacion_YTD'] = (evolucion_patrimonial_RV['AUM_daily']-evolucion_patrimonial_RV['AUM_ytd'])
evolucion_patrimonial_RV['Variacion_YTD_%'] = (evolucion_patrimonial_RV['AUM_daily']/evolucion_patrimonial_RV['AUM_ytd']-1)
evolucion_patrimonial_RV = evolucion_patrimonial_RV.sort_values('AUM_daily', ascending=False)
top20_RV = evolucion_patrimonial_RV.nlargest(20, 'AUM_daily')

# Sumar los valores del resto de los bancos en columnas específicas
resto_RV = evolucion_patrimonial_RV[~evolucion_patrimonial_RV.index.isin(top20_RV.index)][['AUM_daily', 'AUM_un_dia', 'AUM_mtd',
                                                                                           'AUM_ytd', 'Variacion_diaria',
                                                                                           'Variacion_MTD', 'Variacion_YTD']].sum()
# Agregar una fila para el resto de los bancos
resto_RV.name = 'Otras'
evolucion_patrimonial_RV = pd.concat([top20_RV, resto_RV.to_frame().T])
evolucion_patrimonial_RV.loc['Total'] = evolucion_patrimonial_RV[['AUM_daily', 'AUM_un_dia', 'AUM_mtd',
                                                                  'AUM_ytd', 'Variacion_diaria',
                                                                  'Variacion_MTD', 'Variacion_YTD']].sum()

evolucion_patrimonial_RV.loc['Otras', 'Variacion_diaria_%'] = (evolucion_patrimonial_RV.loc['Otras', 'AUM_daily']/evolucion_patrimonial_RV.loc['Otras', 'AUM_un_dia'])-1
evolucion_patrimonial_RV.loc['Otras', 'Variacion_MTD_%'] = (evolucion_patrimonial_RV.loc['Otras', 'AUM_daily']/evolucion_patrimonial_RV.loc['Otras', 'AUM_mtd'])-1
evolucion_patrimonial_RV.loc['Otras', 'Variacion_YTD_%'] = (evolucion_patrimonial_RV.loc['Otras', 'AUM_daily']/evolucion_patrimonial_RV.loc['Otras', 'AUM_ytd'])-1
evolucion_patrimonial_RV.loc['Total', 'Variacion_diaria_%'] = (evolucion_patrimonial_RV.loc['Total', 'AUM_daily']/evolucion_patrimonial_RV.loc['Total', 'AUM_un_dia'])-1
evolucion_patrimonial_RV.loc['Total', 'Variacion_MTD_%'] = (evolucion_patrimonial_RV.loc['Total', 'AUM_daily']/evolucion_patrimonial_RV.loc['Total', 'AUM_mtd'])-1
evolucion_patrimonial_RV.loc['Total', 'Variacion_YTD_%'] = (evolucion_patrimonial_RV.loc['Total', 'AUM_daily']/evolucion_patrimonial_RV.loc['Total', 'AUM_ytd'])-1

# Itero para calcular los aum por banco
for i, row in evolucion_patrimonial_RV.iterrows():
    evolucion_patrimonial_RV.at[i, 'MS_daily'] = row['AUM_daily'] / evolucion_patrimonial_RV.loc['Total', 'AUM_daily']

for i, row in evolucion_patrimonial_RV.iterrows():
    evolucion_patrimonial_RV.at[i, 'MS_MTD'] = row['AUM_mtd'] / evolucion_patrimonial_RV.loc['Total', 'AUM_mtd']

for i, row in evolucion_patrimonial_RV.iterrows():
    evolucion_patrimonial_RV.at[i, 'MS_YTD'] = row['AUM_ytd'] / evolucion_patrimonial_RV.loc['Total', 'AUM_ytd']

evolucion_patrimonial_RV.insert(0, 'Tipo de Renta', 'Renta Variable')
evolucion_patrimonial_RV = evolucion_patrimonial_RV.rename_axis('sg_id')
evolucion_patrimonial_RV = pd.merge(evolucion_patrimonial_RV, matriz.groupby('sg_id').agg({'sociedad_gerente': 'first'}), on='sg_id', how='left')
evolucion_patrimonial_RV = evolucion_patrimonial_RV.iloc[:, [-1] + list(range(len(evolucion_patrimonial_RV.columns)-1))]
################################################################################################################################
# Evolución Patrimonial RM
evolucion_patrimonial_RM = matriz_ars[matriz_ars['clasi_nombre'] == 'Renta Mixta'].groupby('sg_id')[['AUM_daily', 'AUM_un_dia', 'AUM_mtd', 'AUM_ytd']].sum()
evolucion_patrimonial_RM['Variacion_diaria'] = (evolucion_patrimonial_RM['AUM_daily']-evolucion_patrimonial_RM['AUM_un_dia'])
evolucion_patrimonial_RM['Variacion_diaria_%'] = (evolucion_patrimonial_RM['AUM_daily']/evolucion_patrimonial_RM['AUM_un_dia']-1)
evolucion_patrimonial_RM['Variacion_MTD'] = (evolucion_patrimonial_RM['AUM_daily']-evolucion_patrimonial_RM['AUM_mtd'])
evolucion_patrimonial_RM['Variacion_MTD_%'] = (evolucion_patrimonial_RM['AUM_daily']/evolucion_patrimonial_RM['AUM_mtd']-1)
evolucion_patrimonial_RM['Variacion_YTD'] = (evolucion_patrimonial_RM['AUM_daily']-evolucion_patrimonial_RM['AUM_ytd'])
evolucion_patrimonial_RM['Variacion_YTD_%'] = (evolucion_patrimonial_RM['AUM_daily']/evolucion_patrimonial_RM['AUM_ytd']-1)
evolucion_patrimonial_RM = evolucion_patrimonial_RM.sort_values('AUM_daily', ascending=False)
top20_RM = evolucion_patrimonial_RM.nlargest(20, 'AUM_daily')

# Sumar los valores del resto de los bancos en columnas específicas
resto_RM = evolucion_patrimonial_RM[~evolucion_patrimonial_RM.index.isin(top20_RM.index)][['AUM_daily', 'AUM_un_dia', 'AUM_mtd',
                                                                                           'AUM_ytd', 'Variacion_diaria',
                                                                                           'Variacion_MTD', 'Variacion_YTD']].sum()
# Agregar una fila para el resto de los bancos
resto_RM.name = 'Otras'
evolucion_patrimonial_RM = pd.concat([top20_RM, resto_RM.to_frame().T])
evolucion_patrimonial_RM.loc['Total'] = evolucion_patrimonial_RM[['AUM_daily', 'AUM_un_dia', 'AUM_mtd',
                                                                  'AUM_ytd', 'Variacion_diaria',
                                                                  'Variacion_MTD', 'Variacion_YTD']].sum()

evolucion_patrimonial_RM.loc['Otras', 'Variacion_diaria_%'] = (evolucion_patrimonial_RM.loc['Otras', 'AUM_daily']/evolucion_patrimonial_RM.loc['Otras', 'AUM_un_dia'])-1
evolucion_patrimonial_RM.loc['Otras', 'Variacion_MTD_%'] = (evolucion_patrimonial_RM.loc['Otras', 'AUM_daily']/evolucion_patrimonial_RM.loc['Otras', 'AUM_mtd'])-1
evolucion_patrimonial_RM.loc['Otras', 'Variacion_YTD_%'] = (evolucion_patrimonial_RM.loc['Otras', 'AUM_daily']/evolucion_patrimonial_RM.loc['Otras', 'AUM_ytd'])-1
evolucion_patrimonial_RM.loc['Total', 'Variacion_diaria_%'] = (evolucion_patrimonial_RM.loc['Total', 'AUM_daily']/evolucion_patrimonial_RM.loc['Total', 'AUM_un_dia'])-1
evolucion_patrimonial_RM.loc['Total', 'Variacion_MTD_%'] = (evolucion_patrimonial_RM.loc['Total', 'AUM_daily']/evolucion_patrimonial_RM.loc['Total', 'AUM_mtd'])-1
evolucion_patrimonial_RM.loc['Total', 'Variacion_YTD_%'] = (evolucion_patrimonial_RM.loc['Total', 'AUM_daily']/evolucion_patrimonial_RM.loc['Total', 'AUM_ytd'])-1

# Itero para calcular los aum por banco
for i, row in evolucion_patrimonial_RM.iterrows():
    evolucion_patrimonial_RM.at[i, 'MS_daily'] = row['AUM_daily'] / evolucion_patrimonial_RM.loc['Total', 'AUM_daily']

for i, row in evolucion_patrimonial_RM.iterrows():
    evolucion_patrimonial_RM.at[i, 'MS_MTD'] = row['AUM_mtd'] / evolucion_patrimonial_RM.loc['Total', 'AUM_mtd']

for i, row in evolucion_patrimonial_RM.iterrows():
    evolucion_patrimonial_RM.at[i, 'MS_YTD'] = row['AUM_ytd'] / evolucion_patrimonial_RM.loc['Total', 'AUM_ytd']


evolucion_patrimonial_RM.insert(0, 'Tipo de Renta', 'Renta Mixta')
evolucion_patrimonial_RM = evolucion_patrimonial_RM.rename_axis('sg_id')
evolucion_patrimonial_RM = pd.merge(evolucion_patrimonial_RM, matriz.groupby('sg_id').agg({'sociedad_gerente': 'first'}), on='sg_id', how='left')
evolucion_patrimonial_RM = evolucion_patrimonial_RM.iloc[:, [-1] + list(range(len(evolucion_patrimonial_RM.columns)-1))]
################################################################################################################################
# Evolución Patrimonial Infra
evolucion_patrimonial_INFRA = matriz_ars[matriz_ars['clasi_nombre'] == 'Infraestructura'].groupby('sg_id')[['AUM_daily', 'AUM_un_dia', 'AUM_mtd', 'AUM_ytd']].sum()
evolucion_patrimonial_INFRA['Variacion_diaria'] = (evolucion_patrimonial_INFRA['AUM_daily']-evolucion_patrimonial_INFRA['AUM_un_dia'])
evolucion_patrimonial_INFRA['Variacion_diaria_%'] = (evolucion_patrimonial_INFRA['AUM_daily']/evolucion_patrimonial_INFRA['AUM_un_dia']-1)
evolucion_patrimonial_INFRA['Variacion_MTD'] = (evolucion_patrimonial_INFRA['AUM_daily']-evolucion_patrimonial_INFRA['AUM_mtd'])
evolucion_patrimonial_INFRA['Variacion_MTD_%'] = (evolucion_patrimonial_INFRA['AUM_daily']/evolucion_patrimonial_INFRA['AUM_mtd']-1)
evolucion_patrimonial_INFRA['Variacion_YTD'] = (evolucion_patrimonial_INFRA['AUM_daily']-evolucion_patrimonial_INFRA['AUM_ytd'])
evolucion_patrimonial_INFRA['Variacion_YTD_%'] = (evolucion_patrimonial_INFRA['AUM_daily']/evolucion_patrimonial_INFRA['AUM_ytd']-1)
evolucion_patrimonial_INFRA = evolucion_patrimonial_INFRA.sort_values('AUM_daily', ascending=False)
top20_INFRA = evolucion_patrimonial_INFRA.nlargest(20, 'AUM_daily')

# Sumar los valores del resto de los bancos en columnas específicas
resto_INFRA = evolucion_patrimonial_INFRA[~evolucion_patrimonial_INFRA.index.isin(top20_INFRA.index)][['AUM_daily', 'AUM_un_dia', 'AUM_mtd',
                                                                                                       'AUM_ytd', 'Variacion_diaria',
                                                                                                       'Variacion_MTD', 'Variacion_YTD']].sum()
# Agregar una fila para el resto de los bancos
resto_INFRA.name = 'Otras'
evolucion_patrimonial_INFRA = pd.concat([top20_INFRA, resto_INFRA.to_frame().T])
evolucion_patrimonial_INFRA.loc['Total'] = evolucion_patrimonial_INFRA[['AUM_daily', 'AUM_un_dia', 'AUM_mtd',
                                                                        'AUM_ytd', 'Variacion_diaria',
                                                                        'Variacion_MTD', 'Variacion_YTD']].sum()

if evolucion_patrimonial_INFRA.loc['Otras', 'AUM_un_dia'] != 0:
    evolucion_patrimonial_INFRA.loc['Otras', 'Variacion_diaria_%'] = (evolucion_patrimonial_INFRA.loc['Otras', 'AUM_daily'] / evolucion_patrimonial_INFRA.loc['Otras', 'AUM_un_dia']) - 1
else:
    evolucion_patrimonial_INFRA.loc['Otras', 'Variacion_diaria_%'] = 0

if evolucion_patrimonial_INFRA.loc['Otras', 'AUM_mtd'] != 0:
    evolucion_patrimonial_INFRA.loc['Otras', 'Variacion_MTD_%'] = (evolucion_patrimonial_INFRA.loc['Otras', 'AUM_daily'] / evolucion_patrimonial_INFRA.loc['Otras', 'AUM_mtd']) - 1
else:
    evolucion_patrimonial_INFRA.loc['Otras', 'Variacion_MTD_%'] = 0

if evolucion_patrimonial_INFRA.loc['Otras', 'AUM_ytd'] != 0:
    evolucion_patrimonial_INFRA.loc['Otras', 'Variacion_YTD_%'] = (evolucion_patrimonial_INFRA.loc['Otras', 'AUM_daily'] / evolucion_patrimonial_INFRA.loc['Otras', 'AUM_ytd']) - 1
else:
    evolucion_patrimonial_INFRA.loc['Otras', 'Variacion_YTD_%'] = 0

evolucion_patrimonial_INFRA.loc['Total', 'Variacion_diaria_%'] = (evolucion_patrimonial_INFRA.loc['Total', 'AUM_daily']/evolucion_patrimonial_INFRA.loc['Total', 'AUM_un_dia'])-1
evolucion_patrimonial_INFRA.loc['Total', 'Variacion_MTD_%'] = (evolucion_patrimonial_INFRA.loc['Total', 'AUM_daily']/evolucion_patrimonial_INFRA.loc['Total', 'AUM_mtd'])-1
evolucion_patrimonial_INFRA.loc['Total', 'Variacion_YTD_%'] = (evolucion_patrimonial_INFRA.loc['Total', 'AUM_daily']/evolucion_patrimonial_INFRA.loc['Total', 'AUM_ytd'])-1

# Itero para calcular los aum por banco
for i, row in evolucion_patrimonial_INFRA.iterrows():
    evolucion_patrimonial_INFRA.at[i, 'MS_daily'] = row['AUM_daily'] / evolucion_patrimonial_INFRA.loc['Total', 'AUM_daily']

for i, row in evolucion_patrimonial_INFRA.iterrows():
    evolucion_patrimonial_INFRA.at[i, 'MS_MTD'] = row['AUM_mtd'] / evolucion_patrimonial_INFRA.loc['Total', 'AUM_mtd']

for i, row in evolucion_patrimonial_INFRA.iterrows():
    evolucion_patrimonial_INFRA.at[i, 'MS_YTD'] = row['AUM_ytd'] / evolucion_patrimonial_INFRA.loc['Total', 'AUM_ytd']


evolucion_patrimonial_INFRA.insert(0, 'Tipo de Renta', 'Infraestructura')
evolucion_patrimonial_INFRA = evolucion_patrimonial_INFRA.rename_axis('sg_id')
evolucion_patrimonial_INFRA = pd.merge(evolucion_patrimonial_INFRA, matriz.groupby('sg_id').agg({'sociedad_gerente': 'first'}), on='sg_id', how='left')
evolucion_patrimonial_INFRA = evolucion_patrimonial_INFRA.iloc[:, [-1] + list(range(len(evolucion_patrimonial_INFRA.columns)-1))]
################################################################################################################################
# Evolución Patrimonial ASG
evolucion_patrimonial_ASG = matriz_ars[matriz_ars['clasi_nombre'] == 'ASG'].groupby('sg_id')[['AUM_daily', 'AUM_un_dia', 'AUM_mtd', 'AUM_ytd']].sum()
evolucion_patrimonial_ASG['Variacion_diaria'] = (evolucion_patrimonial_ASG['AUM_daily']-evolucion_patrimonial_ASG['AUM_un_dia'])
evolucion_patrimonial_ASG['Variacion_diaria_%'] = (evolucion_patrimonial_ASG['AUM_daily']/evolucion_patrimonial_ASG['AUM_un_dia']-1)
evolucion_patrimonial_ASG['Variacion_MTD'] = (evolucion_patrimonial_ASG['AUM_daily']-evolucion_patrimonial_ASG['AUM_mtd'])
evolucion_patrimonial_ASG['Variacion_MTD_%'] = (evolucion_patrimonial_ASG['AUM_daily']/evolucion_patrimonial_ASG['AUM_mtd']-1)
evolucion_patrimonial_ASG['Variacion_YTD'] = (evolucion_patrimonial_ASG['AUM_daily']-evolucion_patrimonial_ASG['AUM_ytd'])
evolucion_patrimonial_ASG['Variacion_YTD_%'] = (evolucion_patrimonial_ASG['AUM_daily']/evolucion_patrimonial_ASG['AUM_ytd']-1)
evolucion_patrimonial_ASG = evolucion_patrimonial_ASG.sort_values('AUM_daily', ascending=False)
top20_ASG = evolucion_patrimonial_ASG.nlargest(20, 'AUM_daily')

# Sumar los valores del resto de los bancos en columnas específicas
resto_ASG = evolucion_patrimonial_ASG[~evolucion_patrimonial_ASG.index.isin(top20_ASG.index)][['AUM_daily', 'AUM_un_dia', 'AUM_mtd',
                                                                                               'AUM_ytd', 'Variacion_diaria',
                                                                                               'Variacion_MTD', 'Variacion_YTD']].sum()
# Agregar una fila para el resto de los bancos
resto_ASG.name = 'Otras'

evolucion_patrimonial_ASG = pd.concat([top20_ASG, resto_ASG.to_frame().T])
evolucion_patrimonial_ASG.loc['Total'] = evolucion_patrimonial_ASG[['AUM_daily', 'AUM_un_dia', 'AUM_mtd',
                                                                    'AUM_ytd', 'Variacion_diaria',
                                                                    'Variacion_MTD', 'Variacion_YTD']].sum()

if evolucion_patrimonial_ASG.loc['Otras', 'AUM_un_dia'] != 0:
    evolucion_patrimonial_ASG.loc['Otras', 'Variacion_diaria_%'] = (evolucion_patrimonial_ASG.loc['Otras', 'AUM_daily'] / evolucion_patrimonial_ASG.loc['Otras', 'AUM_un_dia']) - 1
else:
    evolucion_patrimonial_ASG.loc['Otras', 'Variacion_diaria_%'] = 0

if evolucion_patrimonial_ASG.loc['Otras', 'AUM_mtd'] != 0:
    evolucion_patrimonial_ASG.loc['Otras', 'Variacion_MTD_%'] = (evolucion_patrimonial_ASG.loc['Otras', 'AUM_daily'] / evolucion_patrimonial_ASG.loc['Otras', 'AUM_mtd']) - 1
else:
    evolucion_patrimonial_ASG.loc['Otras', 'Variacion_MTD_%'] = 0

if evolucion_patrimonial_ASG.loc['Otras', 'AUM_ytd'] != 0:
    evolucion_patrimonial_ASG.loc['Otras', 'Variacion_YTD_%'] = (evolucion_patrimonial_ASG.loc['Otras', 'AUM_daily'] / evolucion_patrimonial_ASG.loc['Otras', 'AUM_ytd']) - 1
else:
    evolucion_patrimonial_ASG.loc['Otras', 'Variacion_YTD_%'] = 0

evolucion_patrimonial_ASG.loc['Total', 'Variacion_diaria_%'] = (evolucion_patrimonial_ASG.loc['Total', 'AUM_daily']/evolucion_patrimonial_ASG.loc['Total', 'AUM_un_dia'])-1
evolucion_patrimonial_ASG.loc['Total', 'Variacion_MTD_%'] = (evolucion_patrimonial_ASG.loc['Total', 'AUM_daily']/evolucion_patrimonial_ASG.loc['Total', 'AUM_mtd'])-1
evolucion_patrimonial_ASG.loc['Total', 'Variacion_YTD_%'] = (evolucion_patrimonial_ASG.loc['Total', 'AUM_daily']/evolucion_patrimonial_ASG.loc['Total', 'AUM_ytd'])-1

# Itero para calcular los aum por banco
for i, row in evolucion_patrimonial_ASG.iterrows():
    evolucion_patrimonial_ASG.at[i, 'MS_daily'] = row['AUM_daily'] / evolucion_patrimonial_ASG.loc['Total', 'AUM_daily']

for i, row in evolucion_patrimonial_ASG.iterrows():
    evolucion_patrimonial_ASG.at[i, 'MS_MTD'] = row['AUM_mtd'] / evolucion_patrimonial_ASG.loc['Total', 'AUM_mtd']

for i, row in evolucion_patrimonial_ASG.iterrows():
    evolucion_patrimonial_ASG.at[i, 'MS_YTD'] = row['AUM_ytd'] / evolucion_patrimonial_ASG.loc['Total', 'AUM_ytd']

evolucion_patrimonial_ASG.insert(0, 'Tipo de Renta', 'ASG')
evolucion_patrimonial_ASG = evolucion_patrimonial_ASG.rename_axis('sg_id')
evolucion_patrimonial_ASG = pd.merge(evolucion_patrimonial_ASG, matriz.groupby('sg_id').agg({'sociedad_gerente': 'first'}),
                                     on='sg_id', how='left')

evolucion_patrimonial_ASG = evolucion_patrimonial_ASG.iloc[:, [-1] + list(range(len(evolucion_patrimonial_ASG.columns)-1))]
################################################################################################################################
# Evolución Patrimonial PYME
evolucion_patrimonial_PYME = matriz_ars[matriz_ars['clasi_nombre'] == 'PyMes'].groupby('sg_id')[['AUM_daily', 'AUM_un_dia', 'AUM_mtd', 'AUM_ytd']].sum()
evolucion_patrimonial_PYME['Variacion_diaria'] = (evolucion_patrimonial_PYME['AUM_daily']-evolucion_patrimonial_PYME['AUM_un_dia'])
evolucion_patrimonial_PYME['Variacion_diaria_%'] = (evolucion_patrimonial_PYME['AUM_daily']/evolucion_patrimonial_PYME['AUM_un_dia']-1)
evolucion_patrimonial_PYME['Variacion_MTD'] = (evolucion_patrimonial_PYME['AUM_daily']-evolucion_patrimonial_PYME['AUM_mtd'])
evolucion_patrimonial_PYME['Variacion_MTD_%'] = (evolucion_patrimonial_PYME['AUM_daily']/evolucion_patrimonial_PYME['AUM_mtd']-1)
evolucion_patrimonial_PYME['Variacion_YTD'] = (evolucion_patrimonial_PYME['AUM_daily']-evolucion_patrimonial_PYME['AUM_ytd'])
evolucion_patrimonial_PYME['Variacion_YTD_%'] = (evolucion_patrimonial_PYME['AUM_daily']/evolucion_patrimonial_PYME['AUM_ytd']-1)
evolucion_patrimonial_PYME = evolucion_patrimonial_PYME.sort_values('AUM_daily', ascending=False)
top20_PYME = evolucion_patrimonial_PYME.nlargest(20, 'AUM_daily')
sg_id_8 = evolucion_patrimonial_PYME.loc[8].to_frame().T  # Incluye al sg_id == 8 aunque no este en el top 20

# Sumar los valores del resto de los bancos en columnas específicas
resto_PYME = evolucion_patrimonial_PYME[~evolucion_patrimonial_PYME.index.isin(top20_PYME.index)][['AUM_daily', 'AUM_un_dia', 'AUM_mtd',
                                                                                                   'AUM_ytd', 'Variacion_diaria',
                                                                                                   'Variacion_MTD', 'Variacion_YTD']].sum()
resto_PYME = resto_PYME.drop(8, errors='ignore')
# Agregar una fila para el resto de los bancos
resto_PYME.name = 'Otras'
#evolucion_patrimonial_MM = top20_MM.append(resto_MM)
evolucion_patrimonial_PYME = pd.concat([top20_PYME, sg_id_8, resto_PYME.to_frame().T])
evolucion_patrimonial_PYME.loc['Total'] = evolucion_patrimonial_PYME[['AUM_daily', 'AUM_un_dia', 'AUM_mtd',
                                                                      'AUM_ytd', 'Variacion_diaria',
                                                                      'Variacion_MTD', 'Variacion_YTD']].sum()

evolucion_patrimonial_PYME.loc['Otras', 'Variacion_diaria_%'] = (evolucion_patrimonial_PYME.loc['Otras', 'AUM_daily']/evolucion_patrimonial_PYME.loc['Otras', 'AUM_un_dia'])-1
evolucion_patrimonial_PYME.loc['Otras', 'Variacion_MTD_%'] = (evolucion_patrimonial_PYME.loc['Otras', 'AUM_daily']/evolucion_patrimonial_PYME.loc['Otras', 'AUM_mtd'])-1
evolucion_patrimonial_PYME.loc['Otras', 'Variacion_YTD_%'] = (evolucion_patrimonial_PYME.loc['Otras', 'AUM_daily']/evolucion_patrimonial_PYME.loc['Otras', 'AUM_ytd'])-1
evolucion_patrimonial_PYME.loc['Total', 'Variacion_diaria_%'] = (evolucion_patrimonial_PYME.loc['Total', 'AUM_daily']/evolucion_patrimonial_PYME.loc['Total', 'AUM_un_dia'])-1
evolucion_patrimonial_PYME.loc['Total', 'Variacion_MTD_%'] = (evolucion_patrimonial_PYME.loc['Total', 'AUM_daily']/evolucion_patrimonial_PYME.loc['Total', 'AUM_mtd'])-1
evolucion_patrimonial_PYME.loc['Total', 'Variacion_YTD_%'] = (evolucion_patrimonial_PYME.loc['Total', 'AUM_daily']/evolucion_patrimonial_PYME.loc['Total', 'AUM_ytd'])-1

# Itero para calcular los aum por S.G.
for i, row in evolucion_patrimonial_PYME.iterrows():
    evolucion_patrimonial_PYME.at[i, 'MS_daily'] = row['AUM_daily'] / evolucion_patrimonial_PYME.loc['Total', 'AUM_daily']

for i, row in evolucion_patrimonial_PYME.iterrows():
    evolucion_patrimonial_PYME.at[i, 'MS_MTD'] = row['AUM_mtd'] / evolucion_patrimonial_PYME.loc['Total', 'AUM_mtd']

for i, row in evolucion_patrimonial_PYME.iterrows():
    evolucion_patrimonial_PYME.at[i, 'MS_YTD'] = row['AUM_ytd'] / evolucion_patrimonial_PYME.loc['Total', 'AUM_ytd']

evolucion_patrimonial_PYME.insert(0, 'Tipo de Renta', 'PyMes')
evolucion_patrimonial_PYME = evolucion_patrimonial_PYME.rename_axis('sg_id')
evolucion_patrimonial_PYME = pd.merge(evolucion_patrimonial_PYME, matriz.groupby('sg_id').agg({'sociedad_gerente': 'first'}), on='sg_id', how='left')

evolucion_patrimonial_PYME = evolucion_patrimonial_PYME.iloc[:, [-1] + list(range(len(evolucion_patrimonial_PYME.columns)-1))]
end_time = time.time()
total_time11 = end_time - start_time
print("Tiempo total de procesamiento Evol. Patr.: ", round(total_time11, 4), "segundos")

########################################################################################################################
#############################                AUM POR FONDO ICBC             ############################################
########################################################################################################################

# Armo un df con los datos de matriz en ARS, transformo la clase_nombre sacandole la clase.
AUM_por_fondo = matriz_ars.groupby(['sg_id', [item.split('-')[0] for item in matriz_ars['clase_nombre']], 'clasi_nombre'])['AUM_daily'].sum().reset_index()
AUM_por_fondo.rename(columns={'level_1': 'Fondo'}, inplace=True)
AUM_por_fondo.rename(columns={'level_2': 'clase_nombre'}, inplace=True)

# Lleno los espacios de la primera columna con los datos del banco anterior
AUM_por_fondo['sg_id'].fillna(method='ffill', inplace=True)
# Filtro el ICBC
AUM_por_fondo = AUM_por_fondo.loc[AUM_por_fondo['sg_id'] == 8]
AUM_por_fondo['AUM_USD'] = AUM_por_fondo['AUM_daily'] / tipo_de_cambio_bna
AUM_por_fondo.sort_values(by=['AUM_daily'], ascending=False, inplace=True)
########################################################################################################################
#############################                INDUSTRIA FCI-AUM            ##############################################
########################################################################################################################

clases2 = pd.DataFrame(equivalencias[['clase_id', 'Actividad', 'clasi_nombre', 'moneda']])
industria_aum = pd.merge(clases2, matriz_ars[['clase_id', 'AUM_daily']],  on='clase_id', how='left')
actividad, moneda, renta = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

actividad = industria_aum.groupby('Actividad')['AUM_daily'].sum()
actividad.sort_values(ascending=False, inplace=True)

moneda = industria_aum.groupby('moneda')['AUM_daily'].sum()
moneda.sort_values(ascending=False, inplace=True)

renta['Tipo_Renta_AUM'] = industria_aum.groupby('clasi_nombre')['AUM_daily'].sum()
renta = pd.merge(renta, industria_aum.groupby('clasi_nombre')['AUM_daily'].sum().reset_index(), on='clasi_nombre', how='right')
total_renta = renta['Tipo_Renta_AUM'].sum()
renta.loc['Total', 'Tipo_Renta_AUM'] = total_renta
renta['Peso relativo'] = renta['Tipo_Renta_AUM'] / renta['Tipo_Renta_AUM'].iloc[-1]

########################################################################################################################
#############################                 MARKET SHARE                  ############################################
########################################################################################################################
start_time = time.time()
clases = pd.DataFrame(equivalencias[["clase_id", "clase_nombre", "sg_id", "moneda"]])
principal_ars = pd.merge(clases, concat_princip_basedia[['clase_id', 'patrimonio', 'fecha']],  on='clase_id', how='left')
principal_ars = pd.merge(principal_ars, benchmark[['fecha', 'bna']],  on='fecha', how='left')
principal_ars['patrimonio_ars'] = principal_ars.apply(lambda row: float(row['patrimonio']) * float(row['bna']) if row['moneda'] == 'USD' else float(row['patrimonio']), axis=1)
matriz_MS_Industria = principal_ars.groupby("fecha")['patrimonio_ars'].sum().reset_index()
matriz_MS_ICBC = principal_ars[principal_ars['sg_id'] == 8].groupby('fecha')['patrimonio_ars'].sum().reset_index()
matriz_MS = pd.merge(matriz_MS_Industria, matriz_MS_ICBC,  on='fecha', how='left')
matriz_MS = matriz_MS.rename(columns={'patrimonio_ars_x': 'AUM Industria Diario'})
matriz_MS = matriz_MS.rename(columns={'patrimonio_ars_y': 'AUM ICBC Diario'})

matriz_MS['Market Share'] = matriz_MS['AUM ICBC Diario'] / matriz_MS['AUM Industria Diario']
matriz_MS['fecha'] = matriz_MS['fecha'].dt.date

matriz_MS_MTD = pd.DataFrame()
matriz_MS_MTD = matriz_MS.groupby(pd.PeriodIndex(matriz_MS['fecha'], freq="M"))[['AUM Industria Diario', 'AUM ICBC Diario']].mean().reset_index()
matriz_MS_MTD = matriz_MS_MTD.rename(columns={'AUM Industria Diario': 'AUM Industria MTD'})
matriz_MS_MTD = matriz_MS_MTD.rename(columns={'AUM ICBC Diario': 'AUM ICBC MTD'})
matriz_MS_MTD['Market Share MTD'] = matriz_MS_MTD['AUM ICBC MTD'] / matriz_MS_MTD['AUM Industria MTD']

end_time = time.time()
total_time12 = end_time - start_time
print("Tiempo total de procesamiento MS: ", round(total_time12, 4), "segundos")

########################################################################################################################
#############################                   VOLATILIDADES               ############################################
########################################################################################################################
start_time = time.time()

volatilidades_equivalencias = pd.DataFrame(equivalencias[["clase_id", "clase_nombre", "clasi_nombre", "moneda", "segmento_cajon"]])
volatilidades_principal = pd.DataFrame(concat_princip_basedia[["clase_id", "fecha", "patrimonio", "compute_0013"]])
# Filtro los ultimos 90 días del principal
volatilidades_principal = volatilidades_principal[(pd.to_datetime(volatilidades_principal["fecha"]).dt.date >= noventadias)]
volatilidades = pd.merge(volatilidades_equivalencias, volatilidades_principal,  on='clase_id', how='left')

volatilidades = volatilidades.sort_values(by=["clase_id", "fecha", "segmento_cajon"], ascending=[True, True, True])

volatilidades_mm = volatilidades[volatilidades['clasi_nombre'] == 'Mercado de Dinero'].copy()
volatilidades_otro = volatilidades[volatilidades['clasi_nombre'] != 'Mercado de Dinero'].copy()

volatilidades_mm.loc[:, 'Rendimiento'] = ((volatilidades_mm['compute_0013'] / (volatilidades_mm.groupby('clase_id')['compute_0013'].shift(1))) ** (1/((volatilidades_mm['fecha'] - volatilidades_mm['fecha'].shift(1)).dt.days))) - 1
volatilidades_otro.loc[:, 'Rendimiento'] = volatilidades_otro['compute_0013'] / (volatilidades_otro.groupby('clase_id')['compute_0013'].shift(1)) - 1

volatilidades = pd.concat([volatilidades_mm, volatilidades_otro], axis=0)

# Rendimiento ponerado del cajon
def rendimiento_ponderado(volatilidades):
    if volatilidades['patrimonio'].sum() != 0:
        return (volatilidades['Rendimiento'] * volatilidades['patrimonio']).sum()/volatilidades['patrimonio'].sum()
    else:
        return 0

volatilidades['fecha'] = pd.to_datetime(volatilidades['fecha'])

# Agrupamos los datos por cajon y Fecha
rendimiento_ponderado_cajon = pd.DataFrame()
rendimiento_ponderado_cajon['Rendimiento_ponderado_cajon'] = volatilidades.groupby(['fecha', 'segmento_cajon']).apply(rendimiento_ponderado)
rendimiento_ponderado_cajon = rendimiento_ponderado_cajon.reset_index()

# Calculo de tracking error
volatilidades = pd.merge(volatilidades, rendimiento_ponderado_cajon,  on=['fecha', 'segmento_cajon'], how='left')
volatilidades['Dif_rend_cuadr'] = (volatilidades['Rendimiento'] - volatilidades['Rendimiento_ponderado_cajon'])**2

# Desvio Estandard Clase
desvio_estandard = pd.DataFrame()
desvio_estandard['Desvio_Estandard_Clase'] = volatilidades.groupby('clase_id')['Rendimiento'].std()
desvio_estandard['Desvio_Estandard_Clase_Anualizado'] = (volatilidades.groupby('clase_id')['Rendimiento'].std()) * math.sqrt(252)
desvio_estandard.fillna(value={'Desvio_Estandard_Clase': 0, 'Desvio_Estandard_Clase_Anualizado': 0}, inplace=True)
volatilidades = pd.merge(volatilidades, desvio_estandard,  on=['clase_id'], how='left')

# Tracking error
tracking_error = pd.DataFrame()
tracking_error['Tracking_error'] = volatilidades.groupby('clase_id')['Dif_rend_cuadr'].sum()
N = len(volatilidades['fecha'].unique())-1

tracking_error['Tracking_error'] = (1/(N-1) * tracking_error['Tracking_error']).apply(math.sqrt)
volatilidades = pd.merge(volatilidades, tracking_error,  on=['clase_id'], how='left')

#Calculo de Covarianza
covarianza = volatilidades.groupby('clase_id')[['Rendimiento', 'Rendimiento_ponderado_cajon']].cov().unstack()
covarianza = covarianza['Rendimiento']['Rendimiento_ponderado_cajon']
covarianza = covarianza.to_frame().rename(columns={'Rendimiento_ponderado_cajon': 'Covarianza'})
covarianza = covarianza.reset_index()
volatilidades = pd.merge(volatilidades, covarianza,  on=['clase_id'], how='left')

# Desvio Estandard Cajon
desvio_estandard_cajon = pd.DataFrame()
desvio_estandard_cajon['Desvio_Estandard_Cajon'] = rendimiento_ponderado_cajon.groupby('segmento_cajon')['Rendimiento_ponderado_cajon'].std()
volatilidades = pd.merge(volatilidades, desvio_estandard_cajon,  on=['segmento_cajon'], how='left')

# Beta
volatilidades['Beta'] = volatilidades['Covarianza'] / volatilidades['Desvio_Estandard_Cajon']**2
volatilidades['Beta'].fillna(0, inplace=True)

# Formato de fechas
volatilidades['fecha'] = pd.to_datetime(volatilidades['fecha'], format='%d/%m/%Y')
#volatilidades.to_excel('volatilidades.xlsx')
# Particion para la matriz y marge con la matriz
volatilidades = volatilidades.loc[volatilidades['fecha'] == pd.to_datetime(fecha_informe, format='%Y/%m/%d')]
volatilidades = pd.DataFrame(volatilidades[["clase_id", "Desvio_Estandard_Clase_Anualizado", "Beta", "Tracking_error"]])
matriz_ars = pd.merge(matriz_ars, volatilidades,  on='clase_id', how='left')
matriz = pd.merge(matriz, volatilidades,  on='clase_id', how='left')

end_time = time.time()
total_time13 = end_time - start_time
print("Tiempo total de procesamiento Volatilidades: ", round(total_time13, 4), "segundos")

########################################################################################################################
#############################               Actualización del principal     ############################################
########################################################################################################################
start_time = time.time()
matriz_copia_2['fecha'] = fecha_informe
matriz_copia_2["fecha"] = pd.to_datetime(matriz_copia_2['fecha'], format='%Y/%m/%d')

matriz_copia_2 = matriz_copia_2.rename(columns={'VCP_daily': 'compute_0013'})
df_merged = pd.merge(concat_princip_basedia, matriz_copia_2, on=['clase_id', 'fecha'], how='left')

# Actualizar los valores de 'AUM' en df_merged usando los valores de df1
df_merged['compute_0013_x'].update(df_merged['compute_0013_y'])
df_merged = df_merged.drop(columns=['compute_0013_y']).rename(columns={'compute_0013_x': 'compute_0013'})  # Elimino la columna "compute_0013_y" que esta desactualizada
# Ordenar las columnas para que coincidan con el orden de df2
df_merged = df_merged[concat_princip_basedia.columns]
concat_princip_basedia = df_merged

concat_princip_basedia.drop_duplicates(subset=['clase_id', 'fecha', 'fecha_carga'], keep='last', inplace=True)

end_time = time.time()
total_time14 = end_time - start_time
print("Tiempo total de procesamiento Actualización del Principal: ", round(total_time14, 4), "segundos")
########################################################################################################################
#############################                Calculo del rto. ponderado     ############################################
########################################################################################################################
start_time = time.time()

# RENDIMIENTO PONDERADO MO

# Rto ponderado daily
rendimiento_ponderado_cajon_daily = matriz.groupby('segmento_cajon').apply(lambda x: ((x['rend_1_dia'] * x['AUM_daily']).sum() / x['AUM_daily'].sum()) if x['AUM_daily'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_daily.columns = ['segmento_cajon', 'Daily']

# Rto ponderado MTD
rendimiento_ponderado_cajon_mtd = matriz.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_mtd'] * x['AUM_mtd']).sum() / x['AUM_mtd'].sum()) if x['AUM_mtd'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_mtd.columns = ['segmento_cajon', 'MTD']

# Rto ponderado 30 días
rendimiento_ponderado_cajon_treintadias = matriz.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_30_dias'] * x['AUM_30_dias']).sum() / x['AUM_30_dias'].sum()) if x['AUM_30_dias'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_treintadias.columns = ['segmento_cajon', '1_mes']

# Rto ponderado 3 meses
rendimiento_ponderado_cajon_3meses = matriz.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_3_meses'] * x['AUM_3_meses']).sum() / x['AUM_3_meses'].sum()) if x['AUM_3_meses'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_3meses.columns = ['segmento_cajon', '3_meses']

# Rto ponderado 6 meses
rendimiento_ponderado_cajon_6meses = matriz.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_6_meses'] * x['AUM_6_meses']).sum() / x['AUM_6_meses'].sum()) if x['AUM_6_meses'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_6meses.columns = ['segmento_cajon', '6_meses']

# Rto ponderado YTD
rendimiento_ponderado_cajon_ytd = matriz.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_ytd'] * x['AUM_ytd']).sum() / x['AUM_ytd'].sum()) if x['AUM_ytd'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_ytd.columns = ['segmento_cajon', 'YTD']

# Rto ponderado 12 meses
rendimiento_ponderado_cajon_12meses = matriz.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_12_meses'] * x['AUM_12_meses']).sum() / x['AUM_12_meses'].sum()) if x['AUM_12_meses'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_12meses.columns = ['segmento_cajon', '12_meses']

# Rto ponderado Desvio clase
rendimiento_ponderado_desvio = matriz.groupby('segmento_cajon').apply(lambda x: ((x['Desvio_Estandard_Clase_Anualizado'] * x['AUM_ytd']).sum() / x['AUM_ytd'].sum()) if x['AUM_ytd'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_desvio.columns = ['segmento_cajon', 'Desvio']

# Rto ponderado Fee FY
rendimiento_ponderado_fee = matriz.groupby('segmento_cajon').apply(lambda x: ((x['Fee FY'] * x['AUM_ytd']).sum() / x['AUM_ytd'].sum()) if x['AUM_ytd'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_fee.columns = ['segmento_cajon', 'Fee_FY']

# Rto ponderado 3 Meses Bruto
rendimiento_ponderado_cajon_3meses_bruto = matriz.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_3_meses_bruto'] * x['AUM_3_meses']).sum() / x['AUM_3_meses'].sum()) if x['AUM_3_meses'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_3meses_bruto.columns = ['segmento_cajon', '3_meses_Bruto']

# Rto ponderado YTD Bruto
rendimiento_ponderado_cajon_ytd_bruto = matriz.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_ytd_bruto'] * x['AUM_ytd']).sum() / x['AUM_ytd'].sum()) if x['AUM_ytd'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_ytd_bruto.columns = ['segmento_cajon', 'YTD_Bruto']

# Creo la lista de DataFrames

rend_ponderados_list = [rendimiento_ponderado_cajon_daily, rendimiento_ponderado_cajon_mtd,
                        rendimiento_ponderado_cajon_treintadias, rendimiento_ponderado_cajon_3meses,
                        rendimiento_ponderado_cajon_6meses, rendimiento_ponderado_cajon_ytd,
                        rendimiento_ponderado_cajon_12meses, rendimiento_ponderado_fee,
                        rendimiento_ponderado_desvio, rendimiento_ponderado_cajon_3meses_bruto,
                        rendimiento_ponderado_cajon_ytd_bruto]

rend_ponderados = rend_ponderados_list[0]

for df in rend_ponderados_list[1:]:
    # Realizar la unión utilizando la columna "segmento_cajon" como clave
    rend_ponderados = rend_ponderados.merge(df, on='segmento_cajon', how='right')
rend_ponderados.index.name = 'Rto. Pond. MO'

# RENDIMIENTO PONDERADO ARS

# Rto ponderado daily
rendimiento_ponderado_cajon_daily_ars = matriz_ars.groupby('segmento_cajon').apply(lambda x: ((x['rend_1_dia'] * x['AUM_daily']).sum() / x['AUM_daily'].sum()) if x['AUM_daily'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_daily_ars.columns = ['segmento_cajon', 'Daily']

# Rto ponderado MTD
rendimiento_ponderado_cajon_mtd_ars = matriz_ars.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_mtd'] * x['AUM_mtd']).sum() / x['AUM_mtd'].sum()) if x['AUM_mtd'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_mtd_ars.columns = ['segmento_cajon', 'MTD']

# Rto ponderado 30 días
rendimiento_ponderado_cajon_treintadias_ars = matriz_ars.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_30_dias'] * x['AUM_30_dias']).sum() / x['AUM_30_dias'].sum()) if x['AUM_30_dias'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_treintadias_ars.columns = ['segmento_cajon', '1_mes']

# Rto ponderado 3 meses
rendimiento_ponderado_cajon_3meses_ars = matriz_ars.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_3_meses'] * x['AUM_3_meses']).sum() / x['AUM_3_meses'].sum()) if x['AUM_3_meses'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_3meses_ars.columns = ['segmento_cajon', '3_meses']

# Rto ponderado 6 meses
rendimiento_ponderado_cajon_6meses_ars = matriz_ars.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_6_meses'] * x['AUM_6_meses']).sum() / x['AUM_6_meses'].sum()) if x['AUM_6_meses'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_6meses_ars.columns = ['segmento_cajon', '6_meses']

# Rto ponderado YTD
rendimiento_ponderado_cajon_ytd_ars = matriz_ars.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_ytd'] * x['AUM_ytd']).sum() / x['AUM_ytd'].sum()) if x['AUM_ytd'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_ytd_ars.columns = ['segmento_cajon', 'YTD']

# Rto ponderado 12 meses
rendimiento_ponderado_cajon_12meses_ars = matriz_ars.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_12_meses'] * x['AUM_12_meses']).sum() / x['AUM_12_meses'].sum()) if x['AUM_12_meses'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_12meses_ars.columns = ['segmento_cajon', '12_meses']

# Rto ponderado Fee FY
rendimiento_ponderado_fee_ars = matriz_ars.groupby('segmento_cajon').apply(lambda x: ((x['Fee FY'] * x['AUM_ytd']).sum() / x['AUM_ytd'].sum()) if x['AUM_ytd'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_fee_ars.columns = ['segmento_cajon', 'Fee_FY']

# Rto ponderado 3 Meses Bruto
rendimiento_ponderado_cajon_3meses_Bruto_ars = matriz_ars.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_3_meses_bruto'] * x['AUM_3_meses']).sum() / x['AUM_3_meses'].sum()) if x['AUM_3_meses'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_3meses_Bruto_ars.columns = ['segmento_cajon', '3_meses_Bruto']

# Rto ponderado YTD Bruto
rendimiento_ponderado_cajon_ytd_bruto_ars = matriz_ars.groupby('segmento_cajon').apply(lambda x: ((x['rend_vcp_ytd_bruto'] * x['AUM_ytd']).sum() / x['AUM_ytd'].sum()) if x['AUM_ytd'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_cajon_ytd_bruto_ars.columns = ['segmento_cajon', 'YTD_Bruto']

# Rto ponderado Fee FY
rendimiento_ponderado_fee_ars = matriz_ars.groupby('segmento_cajon').apply(lambda x: ((x['Fee FY'] * x['AUM_ytd']).sum() / x['AUM_ytd'].sum()) if x['AUM_ytd'].sum() != 0 else 0).reset_index()
rendimiento_ponderado_fee_ars.columns = ['segmento_cajon', 'Fee_FY']


# Creo la lista de DataFrames
rend_ponderados_list_ars = [rendimiento_ponderado_cajon_daily_ars, rendimiento_ponderado_cajon_mtd_ars,
                            rendimiento_ponderado_cajon_treintadias_ars, rendimiento_ponderado_cajon_3meses_ars,
                            rendimiento_ponderado_cajon_6meses_ars, rendimiento_ponderado_cajon_ytd_ars,
                            rendimiento_ponderado_cajon_12meses_ars, rendimiento_ponderado_fee_ars,
                            rendimiento_ponderado_desvio, rendimiento_ponderado_cajon_3meses_Bruto_ars,
                            rendimiento_ponderado_cajon_ytd_bruto_ars]

rend_ponderados_ars = rend_ponderados_list_ars[0]

for df in rend_ponderados_list_ars[1:]:
    # Realizar la unión utilizando la columna "segmento_cajon" como clave
    rend_ponderados_ars = rend_ponderados_ars.merge(df, on='segmento_cajon', how='right')

rend_ponderados_ars.index.name = 'Rto. Pond. ARS'

end_time = time.time()
total_time15 = end_time - start_time
print("Tiempo total de procesamiento Rto. Ponderado: ", round(total_time15, 4), "segundos")

########################################################################################################################
#############################                   Ventas Netas                ############################################
########################################################################################################################
start_time = time.time()

# Estimacion de Ventas Netas Diarias

principal_diario = concat_princip_basedia.loc[concat_princip_basedia['fecha'] >= pd.to_datetime(fecha_informe - timedelta(days=dif_1), format='%Y/%m/%d')]
ventas_netas_diario = pd.DataFrame(principal_diario[["clase_id", "clase_nombre", "sg_nombre", "moneda_cod",
                                                     "clasi_nombre", "compute_0013", "cuotapartes", "fecha"]])
ventas_netas_diario = ventas_netas_diario.sort_values(by=["clase_id", "fecha"], ascending=[True, True])

# Calcular la columna 'VCP_ARS' basada en la condición 'moneda_cod'
ventas_netas_diario = pd.merge(ventas_netas_diario, benchmark[['fecha', 'bna']], on='fecha', how='left')
ventas_netas_diario['VCP_ARS'] = ventas_netas_diario.apply(lambda x: x['compute_0013'] * x['bna'] if x['moneda_cod'] == 'USD' else x['compute_0013'], axis=1)

# Calcular la columna 'Ventas' dentro de cada grupo de 'clase_id'
ventas_netas_diario['Ventas'] = (ventas_netas_diario['cuotapartes'] - ventas_netas_diario.groupby('clase_id')['cuotapartes'].shift(1)) * ventas_netas_diario['VCP_ARS']
ventas_netas_diario['Ventas'] = ventas_netas_diario['Ventas'] / 1000

# Copiar el DataFrame 'ventas_netas_diario' para calcular 'Ventas_MO'
ventas_netas_diario_mo = ventas_netas_diario.copy()

# Calcular la columna 'Ventas_MO' dentro de cada grupo de 'clase_id'
ventas_netas_diario_mo['Ventas_MO'] = (ventas_netas_diario_mo['cuotapartes'] - ventas_netas_diario_mo.groupby('clase_id')['cuotapartes'].shift(1)) * ventas_netas_diario_mo['compute_0013']
ventas_netas_diario_mo['Ventas_MO'] = ventas_netas_diario_mo['Ventas_MO'] / 1000

# Merge con 'equivalencias' para agregar 'Actividad' y 'personería' a 'ventas_netas_diario'
ventas_netas_diario = pd.merge(ventas_netas_diario, equivalencias[['clase_id', 'Actividad', 'personería']],
                               on='clase_id', how='left')
ventas_netas_diario.drop_duplicates(subset='clase_id', keep='last', inplace=True)
ventas_netas_diario_mo.drop_duplicates(subset='clase_id', keep='last', inplace=True)

# Merge de 'ventas_netas_diario' con 'matriz_ars' y 'matriz' para agregar las ventas diarias a las matrices
matriz_ars = pd.merge(matriz_ars, ventas_netas_diario[['clase_id', 'Ventas']], on='clase_id', how='left')
matriz = pd.merge(matriz, ventas_netas_diario_mo[['clase_id', 'Ventas_MO']], on='clase_id', how='left')

ventas_netas_diario['Ventas'].fillna(0, inplace=True)
ventas_netas_diario.loc[ventas_netas_diario['personería'] == 'Wholesale - Por monto', 'personería'] = 'Wholesale'
ventas_netas_diario.loc[ventas_netas_diario['personería'] == 'Retail - Por monto', 'personería'] = 'Retail'
ventas_netas_diario.loc[ventas_netas_diario['personería'] == 'Clase Unica', 'personería'] = 'General'

# Filas y columnas del cuadro de doble entrada
columnas_adicionales = ['General', 'Retail', 'Wholesale']
filas_adicionales = ['Mercado de Dinero', 'Renta Fija', 'Renta Mixta', 'Renta Variable', 'PyMes']

# ICBC Diario
df_icbc_diario = ventas_netas_diario[ventas_netas_diario['sg_nombre'] == 'ICBC Investments Argentina S.A.U.S.G.F.C.I.']
tabla_ICBC_diario = df_icbc_diario.pivot_table(index='clasi_nombre', columns='personería', values='Ventas', aggfunc='sum', fill_value=0)
tabla_ICBC_diario = tabla_ICBC_diario.reindex(index=filas_adicionales, columns=columnas_adicionales)
tabla_ICBC_diario.index.name = 'ICBC - Diario'
tabla_ICBC_diario.loc['Total'] = tabla_ICBC_diario[['General', 'Retail', 'Wholesale']].sum()
tabla_ICBC_diario['Total'] = tabla_ICBC_diario.sum(axis=1)

# Banco Competidor Diario
df_banco_competidor_diario = ventas_netas_diario[ventas_netas_diario['Actividad'] == 'Banco Competidor']
tabla_banco_competidor_diario = df_banco_competidor_diario.pivot_table(index='clasi_nombre', columns='personería', values='Ventas', aggfunc='sum', fill_value=0)
tabla_banco_competidor_diario = tabla_banco_competidor_diario.reindex(index=filas_adicionales, columns=columnas_adicionales)
tabla_banco_competidor_diario.index.name = 'Banco Competidor - Diario'
tabla_banco_competidor_diario.loc['Total'] = tabla_banco_competidor_diario[['General', 'Retail', 'Wholesale']].sum()
tabla_banco_competidor_diario['Total'] = tabla_banco_competidor_diario.sum(axis=1)

# Banco Resto Diario
df_banco_resto_diario = ventas_netas_diario[ventas_netas_diario['Actividad'] == 'Banco Resto']
tabla_banco_resto_diario = df_banco_resto_diario.pivot_table(index='clasi_nombre', columns='personería', values='Ventas', aggfunc='sum', fill_value=0)
tabla_banco_resto_diario = tabla_banco_resto_diario.reindex(index=filas_adicionales, columns=columnas_adicionales)
tabla_banco_resto_diario.index.name = 'Banco Resto - Diario'
tabla_banco_resto_diario.loc['Total'] = tabla_banco_resto_diario[['General', 'Retail', 'Wholesale']].sum()
tabla_banco_resto_diario['Total'] = tabla_banco_resto_diario.sum(axis=1)

# Independientes c/ALYC Diario
df_indep_c_alyc_diario = ventas_netas_diario[ventas_netas_diario['Actividad'] == 'Independientes c/ALYC']
tabla_indep_c_alyc_diario = df_indep_c_alyc_diario.pivot_table(index='clasi_nombre', columns='personería', values='Ventas', aggfunc='sum', fill_value=0)
tabla_indep_c_alyc_diario = tabla_indep_c_alyc_diario.reindex(index=filas_adicionales, columns=columnas_adicionales)
tabla_indep_c_alyc_diario.index.name = 'Independientes con Alycs - Diario'
tabla_indep_c_alyc_diario.loc['Total'] = tabla_indep_c_alyc_diario[['General', 'Retail', 'Wholesale']].sum()
tabla_indep_c_alyc_diario['Total'] = tabla_indep_c_alyc_diario.sum(axis=1)

# Independientes s/ALYC Diario
df_indep_s_alyc_diario = ventas_netas_diario[ventas_netas_diario['Actividad'] == 'Independientes s/ALYC']
tabla_indep_s_alyc_diario = df_indep_s_alyc_diario.pivot_table(index='clasi_nombre', columns='personería', values='Ventas', aggfunc='sum', fill_value=0)
tabla_indep_s_alyc_diario = tabla_indep_s_alyc_diario.reindex(index=filas_adicionales, columns=columnas_adicionales)
tabla_indep_s_alyc_diario.index.name = 'Independientes sin Alycs - Diario'
tabla_indep_s_alyc_diario.loc['Total'] = tabla_indep_s_alyc_diario[['General', 'Retail', 'Wholesale']].sum()
tabla_indep_s_alyc_diario['Total'] = tabla_indep_s_alyc_diario.sum(axis=1)

# Estimacion de Ventas Netas YTD

principal_ytd = concat_princip_basedia.loc[concat_princip_basedia['fecha'] >= pd.to_datetime(fecha_informe - timedelta(days=dif_ytd), format='%Y/%m/%d')]
ventas_netas_ytd = pd.DataFrame(principal_ytd[["clase_id", "clase_nombre", "sg_nombre", "moneda_cod", "clasi_nombre", "compute_0013", "cuotapartes", "fecha"]])
ventas_netas_ytd = ventas_netas_ytd.sort_values(by=["clase_id", "fecha"], ascending=[True, True])
ventas_netas_ytd = pd.merge(ventas_netas_ytd, benchmark[['fecha', 'bna']],  on='fecha', how='left')
ventas_netas_ytd['VCP_ARS'] = ventas_netas_ytd.apply(lambda x: x['compute_0013'] * x['bna'] if x['moneda_cod'] == 'USD' else x['compute_0013'], axis=1)
ventas_netas_ytd.loc[:, 'Ventas'] = (ventas_netas_ytd['cuotapartes'] - (ventas_netas_ytd.groupby('clase_id')['cuotapartes'].shift(1))) * ventas_netas_ytd['VCP_ARS']
ventas_netas_ytd['Ventas'] = ventas_netas_ytd['Ventas'] / 1000

ventas_netas_ytd = pd.merge(ventas_netas_ytd, equivalencias[['clase_id', 'Actividad', 'personería']],  on='clase_id', how='left')

ventas_netas_ytd['Ventas'].fillna(0, inplace=True)
ventas_netas_ytd.loc[ventas_netas_ytd['personería'] == 'Wholesale - Por monto', 'personería'] = 'Wholesale'
ventas_netas_ytd.loc[ventas_netas_ytd['personería'] == 'Retail - Por monto', 'personería'] = 'Retail'
ventas_netas_ytd.loc[ventas_netas_ytd['personería'] == 'Clase Unica', 'personería'] = 'General'

# Filas y columnas del cuadro de doble entrada
columnas_adicionales = ['General', 'Retail', 'Wholesale']
filas_adicionales = ['Mercado de Dinero', 'Renta Fija', 'Renta Mixta', 'Renta Variable', 'PyMes']

# ICBC YTD
df_icbc_ytd = ventas_netas_ytd[ventas_netas_ytd['sg_nombre'] == 'ICBC Investments Argentina S.A.U.S.G.F.C.I.']
tabla_ICBC_ytd = df_icbc_ytd.pivot_table(index='clasi_nombre', columns='personería', values='Ventas', aggfunc='sum', fill_value=0)
tabla_ICBC_ytd = tabla_ICBC_ytd.reindex(index=filas_adicionales, columns=columnas_adicionales)
tabla_ICBC_ytd.index.name = 'ICBC - YTD'
tabla_ICBC_ytd.loc['Total'] = tabla_ICBC_ytd[['General', 'Retail', 'Wholesale']].sum()
tabla_ICBC_ytd['Total'] = tabla_ICBC_ytd.sum(axis=1)

# Banco Competidor YTD
df_banco_competidor_ytd = ventas_netas_ytd[ventas_netas_ytd['Actividad'] == 'Banco Competidor']
tabla_banco_competidor_ytd = df_banco_competidor_ytd.pivot_table(index='clasi_nombre', columns='personería', values='Ventas', aggfunc='sum', fill_value=0)
tabla_banco_competidor_ytd = tabla_banco_competidor_ytd.reindex(index=filas_adicionales, columns=columnas_adicionales)
tabla_banco_competidor_ytd.index.name = 'Banco Competidor - YTD'
tabla_banco_competidor_ytd.loc['Total'] = tabla_banco_competidor_ytd[['General', 'Retail', 'Wholesale']].sum()
tabla_banco_competidor_ytd['Total'] = tabla_banco_competidor_ytd.sum(axis=1)

# Banco Resto YTD
df_banco_resto_ytd = ventas_netas_ytd[ventas_netas_ytd['Actividad'] == 'Banco Resto']
tabla_banco_resto_ytd = df_banco_resto_ytd.pivot_table(index='clasi_nombre', columns='personería', values='Ventas', aggfunc='sum', fill_value=0)
tabla_banco_resto_ytd = tabla_banco_resto_ytd.reindex(index=filas_adicionales, columns=columnas_adicionales)
tabla_banco_resto_ytd.index.name = 'Banco Resto - YTD'
tabla_banco_resto_ytd.loc['Total'] = tabla_banco_resto_ytd[['General', 'Retail', 'Wholesale']].sum()
tabla_banco_resto_ytd['Total'] = tabla_banco_resto_ytd.sum(axis=1)

# Independientes c/ALYC YTD
df_indep_c_alyc_ytd = ventas_netas_ytd[ventas_netas_ytd['Actividad'] == 'Independientes c/ALYC']
tabla_indep_c_alyc_ytd = df_indep_c_alyc_ytd.pivot_table(index='clasi_nombre', columns='personería', values='Ventas', aggfunc='sum', fill_value=0)
tabla_indep_c_alyc_ytd = tabla_indep_c_alyc_ytd.reindex(index=filas_adicionales, columns=columnas_adicionales)
tabla_indep_c_alyc_ytd.index.name = 'Independientes con Alycs - YTD'
tabla_indep_c_alyc_ytd.loc['Total'] = tabla_indep_c_alyc_ytd[['General', 'Retail', 'Wholesale']].sum()
tabla_indep_c_alyc_ytd['Total'] = tabla_indep_c_alyc_ytd.sum(axis=1)

# Independientes s/ALYC YTD
df_indep_s_alyc_ytd = ventas_netas_ytd[ventas_netas_ytd['Actividad'] == 'Independientes s/ALYC']
tabla_indep_s_alyc_ytd = df_indep_s_alyc_ytd.pivot_table(index='clasi_nombre', columns='personería', values='Ventas', aggfunc='sum', fill_value=0)
tabla_indep_s_alyc_ytd = tabla_indep_s_alyc_ytd.reindex(index=filas_adicionales, columns=columnas_adicionales)
tabla_indep_s_alyc_ytd.index.name = 'Independientes sin Alycs - YTD'
tabla_indep_s_alyc_ytd.loc['Total'] = tabla_indep_s_alyc_ytd[['General', 'Retail', 'Wholesale']].sum()
tabla_indep_s_alyc_ytd['Total'] = tabla_indep_s_alyc_ytd.sum(axis=1)

'''
#Ventas por S.G de Bancos Competidores
columnas_adicionales = ['General', 'Retail', 'Wholesale']
filas_adicionales = ['Santander Rio Asset Management G.F.C.I.S.A.', 'BBVA Frances Asset Management S.A.G.F.C.I.',
                     'Galicia Administradora de Fondos S.A.', 'Itau Asset Management S.A.S.G.F.C.I.']

df_sg_bancos_competidores_diario = ventas_netas_diario[ventas_netas_diario['Actividad'] == 'Banco Competidor']

tabla_sg_bancos_competidores_diario = df_sg_bancos_competidores_diario.pivot_table(index='sg_nombre', columns='personería', values='Ventas', aggfunc='sum', fill_value=0)
tabla_sg_bancos_competidores_diario = tabla_sg_bancos_competidores_diario.reindex(index=filas_adicionales, columns=columnas_adicionales)
tabla_sg_bancos_competidores_diario.index.name = 'Bancos Competidores - Daily'
tabla_sg_bancos_competidores_diario.loc['Total'] = tabla_sg_bancos_competidores_diario[['General', 'Retail', 'Wholesale']].sum()
tabla_sg_bancos_competidores_diario['Total'] = tabla_sg_bancos_competidores_diario.sum(axis=1)
'''

end_time = time.time()
total_time16 = end_time - start_time
print("Tiempo total de procesamiento Ventas Netas: ", round(total_time16, 4), "segundos")
########################################################################################################################
#############################                EXPORTACION A EXCEL            ############################################
########################################################################################################################
start_time = time.time()

# Crear el objeto writer
writer = pd.ExcelWriter(f'Matriz de Salida {fecha_informe}.xlsx', engine='xlsxwriter')

# Exporto los DataFrames en diferentes hojas del archivo "Matriz de Salida"
matriz_ars.to_excel(writer, sheet_name='Matriz ARS', index=False)
matriz.to_excel(writer, sheet_name='Matriz Moneda Original', index=False)
calculo_fechas.to_excel(writer, sheet_name='Matriz de fechas y Controles', index=False)
clases_noinformaron.to_excel(writer, sheet_name='Matriz de fechas y Controles', startrow=12, index=False)
clases_sin_patrimonio.to_excel(writer, sheet_name='Matriz de fechas y Controles', startrow=12, startcol=2, index=False)
clases_con_0.to_excel(writer, sheet_name='Matriz de fechas y Controles', startrow=12, startcol=4, index=False)
s_clases_nuevas.to_excel(writer, sheet_name='Matriz de fechas y Controles', startrow=12, startcol=6, index=False)
clases_moneda_diferente.to_excel(writer, sheet_name='Matriz de fechas y Controles', startrow=12, startcol=8, index=False)
clases_renta_diferente.to_excel(writer, sheet_name='Matriz de fechas y Controles', startrow=12, startcol=11, index=False)
AUM_por_fondo.to_excel(writer, sheet_name='AUM por fondo - ICBC', index=False)
actividad.to_excel(writer, sheet_name='AUM por fondo - ICBC', startcol=7, index=True)
moneda.to_excel(writer, sheet_name='AUM por fondo - ICBC', startcol=10, index=True)
renta.to_excel(writer, sheet_name='AUM por fondo - ICBC', startcol=13, index=False)
evolucion_patrimonial.to_excel(writer, sheet_name='Evolucion patrimonial', index=True)
evolucion_patrimonial_MM.to_excel(writer, sheet_name='Evolucion patrimonial', startcol=21, index=True)
evolucion_patrimonial_RF.to_excel(writer, sheet_name='Evolucion patrimonial', startcol=38, index=True)
evolucion_patrimonial_RV.to_excel(writer, sheet_name='Evolucion patrimonial', startcol=55, index=True)
evolucion_patrimonial_RM.to_excel(writer, sheet_name='Evolucion patrimonial', startcol=72, index=True)
evolucion_patrimonial_INFRA.to_excel(writer, sheet_name='Evolucion patrimonial', startcol=89, index=True)
evolucion_patrimonial_PYME.to_excel(writer, sheet_name='Evolucion patrimonial', startcol=106, index=True)
evolucion_patrimonial_ASG.to_excel(writer, sheet_name='Evolucion patrimonial', startcol=123, index=True)
matriz_MS.to_excel(writer, sheet_name='Market Share', index=False)
matriz_MS_MTD.to_excel(writer, sheet_name='Market Share', startcol=7, index=False)
rend_ponderados.to_excel(writer, sheet_name='Rend. Ponderados', startcol=1, index=True)
rend_ponderados_ars.to_excel(writer, sheet_name='Rend. Ponderados', startcol=15, index=True)
tabla_ICBC_ytd.to_excel(writer, sheet_name='Ventas Netas', startrow=1, index=True)
tabla_banco_competidor_ytd.to_excel(writer, sheet_name='Ventas Netas', startrow=9, index=True)
tabla_banco_resto_ytd.to_excel(writer, sheet_name='Ventas Netas', startrow=17, index=True)
tabla_indep_s_alyc_ytd.to_excel(writer, sheet_name='Ventas Netas', startrow=25, index=True)
tabla_indep_c_alyc_ytd.to_excel(writer, sheet_name='Ventas Netas', startrow=33, index=True)
tabla_ICBC_diario.to_excel(writer, sheet_name='Ventas Netas', startrow=1, startcol=7, index=True)
tabla_banco_competidor_diario.to_excel(writer, sheet_name='Ventas Netas', startrow=9, startcol=7, index=True)
tabla_banco_resto_diario.to_excel(writer, sheet_name='Ventas Netas', startrow=17, startcol=7, index=True)
tabla_indep_s_alyc_diario.to_excel(writer, sheet_name='Ventas Netas', startrow=25, startcol=7, index=True)
tabla_indep_c_alyc_diario.to_excel(writer, sheet_name='Ventas Netas', startrow=33, startcol=7, index=True)
writer.close()

# Copiar el archivo original con un nuevo nombre
shutil.copyfile(f'Matriz de Salida {fecha_informe}.xlsx', 'Matriz de Salida.xlsx')

concat_princip_basedia.to_csv(fr"C:\Users\lr110574\PycharmProjects\Informe_Diario\Salidas\principal_{fecha_concat}.csv", index=False, sep=';')

if not s_clases_nuevas.empty:
    equivalencias.to_excel(r"C:\Users\lr110574\PycharmProjects\Informe_Diario\Equivalencias.xlsx", index=False)

end_time = time.time()
total_time17 = end_time - start_time
print("Tiempo total de procesamiento exportaciones: ", round(total_time17, 4), "segundos")


tiempo_total = 0
for i in range(1, 16):
    tiempo_total += globals()["total_time" + str(i)]
print('\n')
print("Tiempo total del proceso:", round(tiempo_total, 4), "segundos")
########################################################################################################################
#############################                ENVIO DE EMAIL                 ############################################
########################################################################################################################
'''
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
start_time = time.time()
# Crear el mensaje
msg = MIMEMultipart()

# Establecer los parametros del mensaje
password = "xzsgkpzpczgbzmlq"
msg['From'] = "llambiruben@gmail.com"  # Remitente
msg['To'] = "ruben.llambi@icbc.com.ar"  # Destinatario
msg['Subject'] = "Envío Automatico de Python ;) - Informe Diario de Fondos - ICBC - {}".format(fecha_informe.date())  # Asunto
# adjuntar el archivo al mensaje
with open(f'Matriz de Salida {fecha_informe.date()}.xlsx', "rb") as fil:
    part = MIMEApplication(
        fil.read(),
        Name=f'Matriz de Salida {fecha_informe.date()}.xlsx'
    )

    part['Content-Disposition'] = 'attachment; filename="%s"' % f'Matriz de Salida {fecha_informe.date()}.xlsx'
    msg.attach(part)

# Adjuntar el archivo Informe Industria Fondos Comunes de Inversion Completo v1 al mail
with open(f'Informe Industria Fondos Comunes de Inversión Completo.xlsx', "rb") as fil:
    part = MIMEApplication(
        fil.read(),
        Name=f'Informe Industria Fondos Comunes de Inversión Completo.xlsx'
    )

    part['Content-Disposition'] = 'attachment; filename="%s"' % f'Informe Industria Fondos Comunes de Inversión Completo.xlsx'
    msg.attach(part)

server = smtplib.SMTP('smtp.gmail.com: 587')  # Crear el servidor de envio de correo

server.starttls()  # Cifrar la conexion

server.login(msg['From'], password)  # Iniciar sesion en el servidor

# Solicitar confirmación al usuario
print('\n')
confirmacion = input("¿Deseas enviar el correo electrónico? (si/no): ")
print('\n')
# Verificar la confirmación del usuario
if confirmacion.lower() == 'si':
    # Enviar el correo electrónico
    server.sendmail(msg['From'], msg['To'], msg.as_string())  # Enviar el mensaje por el servidor, agregar una preguntar para confirmar el envio del mail
    print("El correo electrónico ha sido enviado.")
else:
    print("El correo electrónico no ha sido enviado.")

server.quit()  # Cerrar la conexion

end_time = time.time()
total_time = end_time - start_time
print("Tiempo total de procesamiento mail: ", total_time, "segundos")
'''
########################################################################################################################