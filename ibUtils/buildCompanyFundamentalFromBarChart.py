import sys

# Path is needed to save the data
from pathlib import Path

sys.path.append('/home/michael/jupyter/local-packages')
from localUtilities.webScrape import getBarChartData as companyInfo
from localUtilities.webScrape import getBarChartOptionsSelenium as companyOptions
import pandas as pd

#plot imports
from localUtilities.plotEarnings import getEarningsData

theBaseCompaniesDirectory = '/home/michael/jupyter/earningDateData/Companies/'
csvSuffix = '.csv'
excelSuffix = '.xlsx'

def buildExcelFile(aStock, startday, theExpiryDateText = '2020-05-29-w'):

    # Get the company info from BarChart
    stockInfo = companyInfo.getCompanyStockInfo(aStock)
    stockOverview = companyInfo.getCompanyOverview(aStock)
    stockFundamentals = companyInfo.getCompanyFundamentals(aStock)
    aText, stockRatings = companyInfo.getCompanyRatings(aStock)

    # get the company Option info
    callOptions, putOptions, expiryText = companyOptions.scrapeCompanyOptionData(aStock, theExpiryDateText)

    # Setup Excel output file
    outExcelFile = theBaseCompaniesDirectory + startday + '/' + aStock + '_SummaryWeekOf-' + startday + excelSuffix

    sheetIsFundamentals = aStock + '-Fundamentals'
    sheetRowStart = 4
    sheetColStart = 1

    writer = pd.ExcelWriter(outExcelFile, engine='xlsxwriter')

    fundamentalsWorkbook = writer.book
    fmt = fundamentalsWorkbook.add_format()

    percentFormat  = fundamentalsWorkbook.add_format({'num_format': '0.0%'})
    currencyFormat = fundamentalsWorkbook.add_format({'num_format': '$#,##0.00'})

    stockFundamentalsTranposed = stockFundamentals.T

    # Add the Ratings next
    stockRatings.to_excel(writer, sheet_name= sheetIsFundamentals,
                                        startrow=sheetRowStart+3, startcol= sheetColStart)
    # Add the fundamentals
    stockInfo.to_excel(writer, sheet_name= sheetIsFundamentals,  startrow=sheetRowStart+7,
                       startcol=sheetColStart, header=False)
    stockFundamentalsTranposed.to_excel(writer, sheet_name= sheetIsFundamentals, startrow=sheetRowStart+7,
                                        startcol= sheetColStart+3, header=False)
    stockOverview.to_excel(writer, sheet_name= sheetIsFundamentals,
                           startrow=sheetRowStart+7, startcol= sheetColStart+6, header=False)

    # Add the text info on Expiry and Recommendations
    fundamentalsWorkbookSheet = writer.sheets[sheetIsFundamentals]
    fundamentalsWorkbookSheet.write(sheetRowStart+1,1, aText)
    fundamentalsWorkbookSheet.write(sheetRowStart,1, expiryText)

    # setup the Option Excel Sheets
    # include the DF header as Excel Header
    callOptions.to_excel(writer, sheet_name= aStock + '-Call Options',
                                        startrow=0, header=True)
    putOptions.to_excel(writer, sheet_name= aStock + '-Put Options',
                                        startrow=0, header=True)

    #=================================================================
    # add data from Raw CSV files
    #=================================================================
    # Get aStock CSV file and add as a sheet
    # companyEarningsWeek = theBaseCompaniesDirectory + startday + '/rawData/'
    # inCsvFile_aSymbol = companyEarningsWeek + aStock + csvSuffix
    # yahooEarningsDf_aSymbol = pd.read_csv(inCsvFile_aSymbol, index_col=0)
    # yahooEarningsDf_aSymbol.to_excel(writer, sheet_name= aStock+'-EarningsHistory',
    #                                     startrow=2, startcol= sheetColStart)


    # Get aStock Excel file and add as a sheet
    inExcelFile = theBaseCompaniesDirectory + startday +\
                          '/SummaryWeekOf-' + startday + excelSuffix
    # Need to use pd.ExcelFile to read in the file to manipulate
    yahooEarningsDf_aSymbol_Sheet = pd.ExcelFile(inExcelFile).parse(aStock)
    # Add the aStock sheet to our Company Info
    yahooEarningsDf_aSymbol_Sheet.to_excel(writer, sheet_name= aStock+'-EarningsHistory',
                                           startrow=2, startcol= sheetColStart)

    # get 2 rows of summary data
    summaryRow = yahooEarningsDf_aSymbol_Sheet.iloc[3,4 :]
    summaryRow = summaryRow.to_frame().T
    summaryRow.to_excel(writer, sheet_name= sheetIsFundamentals,
                        startrow=0, startcol= 1, index=False)

    plotEarningPngFile(aStock, startday)

    aStockEarningsPlot = theBaseCompaniesDirectory + startday + '/rawData/' + aStock + '.png'
    summaryRow.to_excel(writer, sheet_name= aStock + '-Earnings History Plot',
                        startrow=1, startcol= 1)
    imageWorksheet = writer.sheets[aStock + '-Earnings History Plot']
    # imageWorksheet.set_column('E:F', 3)
    # # imageWorksheet = imageSheetFormatting(fundamentalsWorkbook)
    imageWorksheet.insert_image('B5',aStockEarningsPlot)

    # Save excel
    writer.save()


def plotEarningPngFile(aStock, startday):

    # Get weekly earnings
    theEarningsDataList = getEarningsData.getWeeklyExcelSummary(startday, aStock)

    earnings1DayMove_np = theEarningsDataList[0]
    earnings4DayMove_np = theEarningsDataList[1]
    earningsMdate_np = theEarningsDataList[2]
    earnings1DayCandlestick = theEarningsDataList[3]
    earningsDayEPS = theEarningsDataList[4]

    # earningsDayEPS
    getEarningsData.plotEarnings(earningsMdate_np, earnings1DayMove_np, earnings4DayMove_np,
                                 earningsDayEPS, startday, aStock)


# def imageSheetFormatting(fundamentalsWorkbook):
#
#     imageWorkbookSheet = fundamentalsWorkbook[']
#     imageWorkbookSheet.set_row(3, 'E:E', 10, percentFormat)
#     # imageWorkbookSheet.set_column('M:M', 10, currencyFormat)
#     # imageWorkbookSheet.set_column('N:O', 10, percentFormat)
#     # imageWorkbookSheet.set_column('P:T', 10, currencyFormat)
#     return imageWorkbookSheet