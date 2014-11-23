import argparse
import csv
import code
from locale import *
setlocale(LC_NUMERIC, '')

parser = argparse.ArgumentParser(description='Load an ETF into a database')
parser.add_argument('vanguard_file', help='The CSV file to parse.')
parser.add_argument('morningstar_file', help='The CSV file to parse.')
args  =  parser.parse_args()

fundsDict = {}

with open(args.vanguard_file, 'r') as f:
	f_csv = csv.DictReader(f)
	for row in f_csv:
		#	print(row)
		ticker = row['Ticker']
		fundsDict[ticker] = {}
		for k in row.keys():
			fundsDict[ticker][k] = row[k]

with open(args.morningstar_file, 'r') as f:
	f_csv = csv.DictReader(f)
	for row in f_csv:
		#	print(row)
		ticker = row['Symbol']
		#fundsDict[ticker] = {}
		for k in row.keys():
			fundsDict[ticker][k] = row[k]


with open("vanguard_db.psv",  'w') as fp:
	keys = ['Index','TaxManaged','Tax Exempt','Name','Ticker','Geographical',
			'Asset','AssetClass','ExpenseRatio1','SECYield','','YTD','1-year','5-year','10-year','Since inception','FundNo','ExpenseRatio',
			'PurchaseFee','RedemptionFee',
			'MorningstarCategory','BestFitIndex','MinInitialPurchase']
	dict_writer = csv.DictWriter(fp,keys,extrasaction='ignore', delimiter='|')
	dict_writer.writer.writerow(keys)
	for fund in fundsDict.keys():
		dict_writer.writerow(fundsDict[fund])


import code
code.interact(local=locals())
