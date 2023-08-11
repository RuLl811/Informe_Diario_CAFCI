import datetime as dt
import math
from datetime import timedelta
import pandas as pd

pd.set_option('display.max_columns', None)
equivalencias = pd.read_excel(r"C:\Users\lr110574\PycharmProjects\Informe_Diario\Equivalencias.xlsx")
principal = pd.read_csv(r"C:\Users\lr110574\PycharmProjects\Informe_Diario\Salidas\principal_28072023.csv", sep=';')

fecha_hoy = '28/7/2023'  # Poner la fecha del informe
fecha_hoy = dt.datetime.strptime(fecha_hoy, '%d/%m/%Y') # Formato
principal['fecha'] = pd.to_datetime(principal['fecha'], format='%Y-%m-%d')  # Formato
principal = principal.loc[principal['fecha'] >= pd.to_datetime(fecha_hoy - timedelta(days=210), format='%Y/%m/%d')]  # Restale la cant de dias hasta el YTD
ventas_netas = pd.DataFrame(principal[["clase_id", "clase_nombre", "sg_nombre", "moneda_cod", "clasi_nombre", "compute_0013", "cuotapartes", "fecha"]])  # Filtro las columnas
ventas_netas = ventas_netas.sort_values(by=["clase_id", "fecha"], ascending=[True, True])

# Benchmark
benchmark = pd.read_excel(r"C:\Rubén\Fondos\Informe\Benchmark informe.xls", skiprows=5, header=None)
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

# Pesificación de los fondos en USD
ventas_netas = pd.merge(ventas_netas, benchmark[['fecha', 'bna']],  on='fecha', how='left')  # Le agrego la columna de TC
ventas_netas['VCP_ARS'] = ventas_netas.apply(lambda x: x['compute_0013'] * x['bna'] if x['moneda_cod'] == 'USD' else x['compute_0013'], axis=1)  # Pesifico el VCP para fondos es USD

# Calculo de venta neta
ventas_netas.loc[:, 'Ventas'] = ((ventas_netas['cuotapartes'] - (ventas_netas.groupby('clase_id')['cuotapartes'].shift(1))) * ventas_netas['VCP_ARS']) / 1000

# Le sumo la columna personeria, viene de equivalencias.
ventas_netas = pd.merge(ventas_netas, equivalencias[['clase_id', 'personería']],  on='clase_id', how='left')  # Le agrego la actividad y la personeria

ventas_netas['Ventas'].fillna(0, inplace=True)  # Relleno con 0 los NaN
ventas_netas['personería'] = ventas_netas['personería'].replace({'Wholesale - Por monto': 'Wholesale', 'Retail - Por monto': 'Retail', 'Clase unica': 'General'})
ventas_netas = ventas_netas[['sg_nombre', 'clasi_nombre', 'clase_nombre', 'personería', 'fecha', 'Ventas']]
ventas_netas['personeria_clase'] = ventas_netas['clasi_nombre'] + ' - ' + ventas_netas['personería']

# Filas y columnas del cuadro de doble entrada
columnas_adicionales = ventas_netas['personeria_clase'].unique().tolist()
columnas_adicionales = [valor for valor in columnas_adicionales if pd.notna(valor)]
columnas_adicionales = sorted(columnas_adicionales)

filas_adicionales = ventas_netas['sg_nombre'].unique()

# SG YTD
tabla_ytd = ventas_netas.pivot_table(index='sg_nombre', columns=['personeria_clase'], values='Ventas', aggfunc='sum', fill_value=0)
tabla_ytd = tabla_ytd.reindex(index=filas_adicionales, columns=columnas_adicionales)
tabla_ytd.index.name = 'Ventas por SG - YTD'

tabla_ytd['Total'] = tabla_ytd.sum(axis=1)
tabla_ytd = tabla_ytd.sort_values(by='Total', ascending=False)
tabla_ytd.loc['Total'] = tabla_ytd[columnas_adicionales].sum()
'''
# VENTAS SG JUNIO
ventas_netas_junio = ventas_netas.loc[(ventas_netas['fecha'].dt.year == 2023) & (ventas_netas['fecha'].dt.month == 6)]
tabla_junio = ventas_netas_junio.pivot_table(index='sg_nombre', columns='personería', values='Ventas', aggfunc='sum', fill_value=0)
tabla_junio = tabla_junio.reindex(index=filas_adicionales, columns=columnas_adicionales)
tabla_junio.index.name = 'Ventas por SG - Junio'
tabla_junio.loc['Total'] = tabla_junio[columnas_adicionales].sum()
tabla_junio['Total'] = tabla_junio.sum(axis=1)

# VENTAS SG JULIO
ventas_netas_julio = ventas_netas.loc[(ventas_netas['fecha'].dt.year == 2023) & (ventas_netas['fecha'].dt.month == 7)]
tabla_julio = ventas_netas_julio.pivot_table(index='sg_nombre', columns='personería', values='Ventas', aggfunc='sum', fill_value=0)
tabla_julio = tabla_julio.reindex(index=filas_adicionales, columns=columnas_adicionales)
tabla_julio.index.name = 'Ventas por SG - Julio'
tabla_julio.loc['Total'] = tabla_julio[columnas_adicionales].sum()
tabla_julio['Total'] = tabla_julio.sum(axis=1)
'''
# Exportacion
writer = pd.ExcelWriter(f'Ventas Netas.xlsx', engine='xlsxwriter')

tabla_ytd.to_excel(writer, sheet_name='Ventas Netas', startcol=1, index=True)
#tabla_junio.to_excel(writer, sheet_name='Ventas Netas', startcol=7, index=True)
#tabla_julio.to_excel(writer, sheet_name='Ventas Netas', startcol=13, index=True)
writer.close()
