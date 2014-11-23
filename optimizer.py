#!/opt/local/bin/python2.7
import csv
import code
import pymprog
from locale import *
from pylab import *
import textwrap
setlocale(LC_NUMERIC, '')

def loadFundDB(db_file):
	fundsDict = {}
	with open(db_file, 'r') as f:
		f_csv = csv.DictReader(f, delimiter='|')
		for row in f_csv:
			ticker = row['Ticker']
			fundsDict[ticker] = {}
			for k in row.keys():
				fundsDict[ticker][k] = row[k]
	return fundsDict



def pie_chart_portfolio ( fundLabels, fundAmounts, fee):
	#print(fundLabels)
	#print(fundAmounts)
	# make a square figure and axes
	figure(1, figsize=(8,8))
	ax = axes([0.1, 0.1, 0.8, 0.8])
	fee_str = 'Satisfying Allocation, Fee: %2.2f' % ( fee *1e4)
	explode = [0.03] * len(fundLabels)
	pie(fundAmounts, explode=explode, labels=fundLabels, autopct='%1.1f%%', shadow=True, startangle=90)
	title(title_str, bbox={'facecolor':'0.8', 'pad':5})
	show()


######################################################################
######

def setupLP(minPurchaseFlag = False, geoFlag = False, assetFlag = False ):
	totalDollars = 100000
	numFunds = len(fundsDict)
	fundFees = range(numFunds)
	fundMinInvest = range(numFunds)
	bigM          = range(numFunds)
	cid, amounts,fundMins1,fundMins2,binaries   = range(numFunds), range(numFunds),range(numFunds),range(numFunds),range(numFunds)
	#binaries = [0] * numFunds
	fundList = []


	def pretty_print_portfolio():
		fundLabels = list()
		fundWeights = list()
		for i in cid:
			if fundAmounts[i].primal > 0:
				l = textwrap.wrap(fundList[i]["Name"]+"\n"+fundList[i]["Ticker"], 16)
				fundLabels.append("\n".join(l))
				fundWeights.append(fundAmounts[i].primal/dollars.primal)
				print("%g %s : %s : %g : binary: %g" %
					  (i, fundList[i]["Ticker"], fundList[i]["Name"], fundAmounts[i].primal, fundMinBinary[i].primal)
				  )
		pie_chart_portfolio(fundLabels, fundWeights, (portfolio.vobj()/dollars.primal))
		print("Total Fees Are: %g" % (portfolio.vobj()/dollars.primal))

	for index,k in enumerate(sorted(fundsDict.keys()), start=0):
		f = fundsDict[k]
		f['index'] = index
		fundFees[index] = .01*(float(f['ExpenseRatio']) + float(f['PurchaseFee']) + float(f['RedemptionFee']))
		fundMinInvest[index] = atof(f['MinInitialPurchase'])
		bigM[index] = 1e9
		#if fundMinInvest[index] > totalDollars:
		#		bigM[index] = 3*fundMinInvest[index]
		#	else:
		#		bigM[index] = 3*totalDollars

		# print("%g : %s min is %g" %(index, f['Ticker'], fundMinInvest[index]))

		fundList.append(f)

	numGeographies = len(set(fundsDict[k]['Geographical'] for k in fundsDict.keys()))


	portfolio = pymprog.model('portfolio')

	fundAmounts = portfolio.var(amounts, 'X')
	portfolio.min(sum(fundFees[i] * fundAmounts[i] for i in cid), 'port_objective')

	########################
	## Constraint 1
	## Sum (Allocations) <= Total Dollars

	dollars=portfolio.st(
		( totalDollars *0.99 ) <= sum(fundAmounts[i] for i in cid) <= totalDollars
	)

	fundMinBinary = portfolio.var(binaries, 'Bool',bool)
	######################################## END CONSTRAINT 1

	########################################
	## Constraint 2
	## For each fund, mininum allocation is met

	if minPurchaseFlag is True:
		for i in range(numFunds):
			# print("st:%g %s min is %g" % (i, fundList[i]['Ticker'], fundMinInvest[i]))
			fundMins1[i] = portfolio.st( fundAmounts[i] <= (fundMinBinary[i] * bigM[i]))
			fundMins2[i] = portfolio.st( fundAmounts[i] >= (fundMinInvest[i] - bigM[i] + (fundMinBinary[i] * bigM[i])))

			#for i in range(numFunds):
			#	print(fundMins1[i])
			#	print(fundMins2[i])
	################################ END CONSTRAINT 2

	################################
	## Constraint 3
	## Geo constraints
	if geoFlag is True:
		geoLabels = ['Developed', 'Emerging', 'Global', 'Asia', 'US']
		numGeoLabels = len(geoLabels)
		geoWeights   = [0.2, 0.3, 0, 0, 0.5]
		geoConstraints = range(numGeoLabels)
		fundGeoFlags  = range(numGeoLabels)

		for g in range(numGeoLabels):
			fundGeoFlags[g] = range(numFunds)
			for f in range(numFunds):
				### if this fund is in this geoGraphy
				if fundList[f]['Geographical'] == geoLabels[g]:
					fundGeoFlags[g][f] = 1
				else:
					fundGeoFlags[g][f] = 0

			geoConstraints[g] = portfolio.st ( sum ( fundGeoFlags[g][f] * fundAmounts[f] for f in cid ) <= (totalDollars* geoWeights[g]))
	######################## END Constraint 3

	################################
	## Constraint 4
	## AssetClass constraints
	if assetFlag is True:
		assetClasses   = ['Bond', 'RealEstate', 'Stock']
		numAssetClasses = len(assetClasses)
		assetClassWeights    = [ 0.2, 0.2, 0.6]
		assetClassConstraints = range(numAssetClasses)
		fundAssetFlags   = range(numAssetClasses)

		for a in range(numAssetClasses):
			fundAssetFlags[a] = range(numFunds)
			for f in range(numFunds):
				### if this fund is in this assetClass
				if fundList[f]['Asset'] == assetClasses[a]:
					fundAssetFlags[a][f] = 1
				else:
					fundAssetFlags[a][f] = 0

			assetClassConstraints[a] = portfolio.st ( sum ( fundAssetFlags[a][f] * fundAmounts[f] for f in cid ) <= (totalDollars* assetClassWeights[a]))

	#################################### END Constraint 4


	portfolio.solvopt(integer='advanced')
	portfolio.solve()
	print "Solve status: ", portfolio.status()

	#pretty_print_portfolio ( fundAmounts, portfolio, dollars, cid, fundList )
	pretty_print_portfolio ()
	### main

fundsDict= loadFundDB("./vanguard_db.psv")

code.interact(local=locals())
