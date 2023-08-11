import datetime as dt
import math
import time
from datetime import timedelta
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', None)
start_time = time.time()
benchmark = pd.read_excel(r"C:\Rubén\Fondos\Informe\Benchmark informe.xls",
                          skiprows=5, header=None)
benchmark = benchmark.tail(370)
# Elimina las columnas con fecha menos la primera que uso de indice y las columnas que tienen en TODAS las columnas NaN
# Agrego la columna 0 porque la exlui en [:1]
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
    'Fecha', 'MERVAL Index', 'bna', 'dti', 'ccl', 'IBOV $', 'INDU Index', 'SX5P Index', 'BADLARPP Index',
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
benchmark.reset_index(drop=True, inplace=True)
benchmark['BNA/DTI'] = benchmark['bna'] / benchmark['dti']
benchmark.at[0, 'Badlar_Index'] = 100

print(benchmark)
fecha_informe = '2023-07-20'
noventadias = '2023-04-20'
Year_to_date = '2022-12-30'
dif_90 = 91
dif_ytd = 202

rendimientos_tres_meses = benchmark[(benchmark['Fecha'] == noventadias) | (benchmark['Fecha'] == fecha_informe)].iloc[:, 1:]
rendimientos_ytd = benchmark[(benchmark['Fecha'] == Year_to_date) | (benchmark['Fecha'] == fecha_informe)].iloc[:, 1:]

# Imprimir las columnas con valores faltantes
#print(benchmark.isnull().any())

# Cálculo para la fila 'ytd'
rendimientos = pd.DataFrame(rendimientos_ytd.iloc[-1] / rendimientos_ytd.iloc[0] - 1).T
rendimientos.index = ['ytd']

# Cálculo para la fila '3meses'
rendimientos_3meses = pd.DataFrame(rendimientos_tres_meses.iloc[-1] / rendimientos_tres_meses.iloc[0] - 1).T
rendimientos_3meses.index = ['3meses']

# Agregar la fila '3meses' al DataFrame 'rendimientos'
rendimientos = pd.concat([rendimientos, rendimientos_3meses])


print(rendimientos)

end_time = time.time()
total_time1 = end_time - start_time
print("Tiempo total de procesamiento benchmark: ", total_time1, "segundos")
