import csv
import json
import random
import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Portfolio, StockHolding
from django.views.decorators.csrf import csrf_exempt
from riskprofile.models import RiskProfile
from riskprofile.views import risk_profile

# AlphaVantage API
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
import subprocess as sp


def get_alphavantage_key():
  alphavantage_keys = [
    "N8UW6MVBRDUBK0ZV",
    "8O2STDP914IENLRT",
    "A32T4E8ZOAQYIHTZ",
    "H7ROJYZACU81ZE53",
    "7A5TEU5TI23QVJVW",
    "L7O1NFYNDWUDFJQN",
  ]
  return random.choice(alphavantage_keys)
portfolio_nameid="portfolio1"
@login_required
def dashboard(request):
  if True:
    try:
      portfolio = Portfolio.objects.get(user=request.user,portfolio_name = "portfolio1")
    except:
      # updates in backend and makes table
      portfolio = Portfolio.objects.create(user=request.user,portfolio_name = "portfolio2")
      portfolio = Portfolio.objects.create(user=request.user,portfolio_name = "portfolio3")
      portfolio = Portfolio.objects.create(user=request.user,portfolio_name = "portfolio1")
    context = updatePortfolio(request)

    return render(request, 'dashboard/dashboard.html', context)
  else:
    return redirect(risk_profile)
    
def updatePortfolio(request):
      # obj=Portfolio_()
      # response=obj.updatePortfolio(request)
      # return response


    port = Portfolio.objects.filter(user=request.user)
    portf = {}
    for idx,portfolio in enumerate(port):
#         print(portfolio)
        portfolio.update_investment()
        holding_companies = StockHolding.objects.filter(portfolio=portfolio)
        holdings = []
        sectors = [[], []]
        sector_wise_investment = {}
        stocks = [[], []]
        for c in holding_companies:
         company_symbol = c.company_symbol
         company_name = c.company_name
         number_shares = c.number_of_shares
         investment_amount = c.investment_amount
         average_cost = investment_amount / number_shares
         holdings.append({
           'CompanySymbol': company_symbol,
           'CompanyName': company_name,
           'NumberShares': number_shares,
           'InvestmentAmount': investment_amount,
           'AverageCost': average_cost,
         })

         stocks[0].append(round((investment_amount / portfolio.total_investment) * 100, 2))
         stocks[1].append(company_symbol)
         if c.sector in sector_wise_investment:
           sector_wise_investment[c.sector] += investment_amount
         else:
           sector_wise_investment[c.sector] = investment_amount
        for sec in sector_wise_investment.keys():
         sectors[0].append(round((sector_wise_investment[sec] / portfolio.total_investment) * 100, 2))
         sectors[1].append(sec)
        context = {
          'holdings': holdings,
          'totalInvestment': portfolio.total_investment,
          'stocks': stocks,
          'sectors': sectors,
        }
#         print(idx)
        portf[portfolio.portfolio_name]=context
#     print(portf)
    return portf

def get_portfolio_insights(request):
  # obj = DetailedPNL()
  # response=obj.get_portfolio_insights(request)
  # print(response)
  # return JsonResponse(response)
  
  try:
    portfolio_beta = 0
    portfolio_pe = 0
    port = Portfolio.objects.filter(user=request.user)
    for portfolio in port:
        holding_companies = StockHolding.objects.filter(portfolio=portfolio)
        fd = FundamentalData(key=get_alphavantage_key(), output_format='json')
        for c in holding_companies:
          data, meta_data = fd.get_company_overview(symbol=c.company_symbol)
          print("pe")
          # Getting values of beta and pe
          portfolio_beta += float(0.6) * (c.investment_amount / portfolio.total_investment)
          portfolio_pe += float(14) * (c.investment_amount / portfolio.total_investment)
          print(portfolio_pe)
    print(portfolio_pe)
    return JsonResponse({"PortfolioBeta": portfolio_beta, "PortfolioPE": portfolio_pe}) 
  except Exception as e:
    print(e)
    return JsonResponse({"Error": str(e)})


def update_values(request):
  # obj = Portfolio_()
  # response=obj.update_values(request)
  # print(response)
  # return JsonResponse(response)
  try:
    por = Portfolio.objects.filter(user=request.user)
    portfoliodata ={}
    for portfolio in por:
#         print(portfolio_nameid)
#         print(portfolio.portfolio_name)
        current_value = 0
        unrealized_pnl = 0
        growth = 0
        holding_companies = StockHolding.objects.filter(portfolio=portfolio)
#         print(holding_companies)
        stockdata = {}
        for idx,c in enumerate(holding_companies):
          ts = TimeSeries(key=get_alphavantage_key(), output_format='json')
          data, meta_data = ts.get_quote_endpoint(symbol=c.company_symbol)
          last_trading_price = float(data['05. price'])
          pnl = (last_trading_price * c.number_of_shares) - c.investment_amount
          net_change = pnl / c.investment_amount
          stockdata[c.company_symbol] = {
            'LastTradingPrice': last_trading_price,
            'PNL': pnl,
            'NetChange': net_change * 100
          }
          current_value += (last_trading_price * c.number_of_shares)
#           print("hello")
          unrealized_pnl += pnl
#           print(unrealized_pnl)
#         print("working")
        if portfolio.total_investment>0:     
          growth = unrealized_pnl
        else:
          growth=0
        print(growth)
        ctx = {
            "StockData": stockdata, 
            "CurrentValue": current_value,
            "UnrealizedPNL": unrealized_pnl,
            "Growth": growth * 100
            }
        portfoliodata[portfolio.portfolio_name] = ctx
#         print(ctx)
    print(portfoliodata)
    return JsonResponse(portfoliodata)
  except Exception as e:
    print(e)
    return JsonResponse({"Error": str(e)})


def get_financials(request):
  # obj = DetailedPNL()
  # response=obj.get_financials(request)
  # print(response)
  # return JsonResponse(response)
  try:
    fd = FundamentalData(key=get_alphavantage_key(), output_format='json')
    print("get finance TILL HERE")

    data, meta_data = fd.get_company_overview(symbol=request.GET.get('symbol'))
    financials = {
      "52WeekHigh": data['52WeekHigh'],
      "52WeekLow": data['52WeekLow'],
      "Beta": data['Beta'],
      "BookValue": data['BookValue'],
      "EBITDA": data['EBITDA'],
      "EVToEBITDA": data['EVToEBITDA'],
      "OperatingMarginTTM": data['OperatingMarginTTM'],
      "PERatio": data['PERatio'],
      "PriceToBookRatio": data['PriceToBookRatio'],
      "ProfitMargin": data['ProfitMargin'],
      "ReturnOnAssetsTTM": data['ReturnOnAssetsTTM'],
      "ReturnOnEquityTTM": data['ReturnOnEquityTTM'],
      "Sector": data['Sector'],
    }
    return JsonResponse({ "financials": financials })
  except Exception as e:
    return JsonResponse({"Error": str(e)})

def create_portfolio(request):
  if request.method == "POST":
      name = request.POST['portfolioname']
      portfolio = Portfolio.objects.create(user=request.user,portfolio_name = name)
      print(request.user)
      return HttpResponse("Success")
      
@csrf_exempt
def set_portfolio(request):
  if request.method == "POST":
      print(request)
      portfolio_nameid = request.POST['name']
      portfolio = Portfolio.objects.get(user=request.user,portfolio_name = "portfolio2")
      updatePortfolio(request,portfolio)
      print(portfolio_nameid)
      return HttpResponse("Success")
           
# Transaction
def add_holding(request):
  if request.method == "POST":
  #     obj = Transaction()
  #     response=obj.add_holding(request)
  #     return HttpResponse(response)
        
    try:
      print("add holding")
      print(request.POST['portfolio_select'])
      portfolio = Portfolio.objects.get(user=request.user,portfolio_name=request.POST['portfolio_select'])
      holding_companies = StockHolding.objects.filter(portfolio=portfolio)
      company_symbol = request.POST['company'].split('(')[1].split(')')[0]
      company_name = request.POST['company'].split('(')[0].strip()
      number_stocks = int(request.POST['number-stocks'])
      ts = TimeSeries(key=get_alphavantage_key() ,output_format='json')
      data, meta_data = ts.get_intraday(symbol=company_symbol, interval='60min',outputsize='full')
      buy_price = float(data[request.POST['date']+" 13:00:00"]['4. close'])
      fd = FundamentalData(key=get_alphavantage_key(), output_format='json')
      data, meta_data = fd.get_company_overview(symbol=company_symbol)
      sector = data['Sector']
      

      found = False
      for c in holding_companies:
        if c.company_symbol == company_symbol:
          c.buying_value.append([buy_price, number_stocks])
          c.save()
          found = True

      if not found:
        c = StockHolding.objects.create(
          portfolio=portfolio, 
          portfolio_nameid = portfolio.portfolio_name,
          company_name=company_name, 
          company_symbol=company_symbol,
          number_of_shares=number_stocks,
          sector=sector
        )
        c.buying_value.append([buy_price, number_stocks])
        c.save()

      return HttpResponse("Success")
    except Exception as e:
      print(e)
      return HttpResponse(e)

def send_company_list(request):
  with open('nasdaq-listed.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    rows = []
    for row in csv_reader:
      if line_count == 0:
        line_count += 1
      else:
        rows.append([row[0], row[1]])
        line_count += 1
  return JsonResponse({"data": rows})

def backtesting(request):
  print('Function Called')
  try:
    # obj = DetailedPNL()
    # obj.backtesting()
    output = sp.check_output("quantdom", shell=True)
  except sp.CalledProcessError:
    output = 'No such command'
  return HttpResponse("Success")



# class DetailedPNL():
  
#   def get_portfolio_insights(self,request):
#     try:
#       # print(1000)
#       portfolio_beta = 0
#       portfolio_pe = 0
#       port = Portfolio.objects.filter(user=request.user)
#       for portfolio in port:
#           holding_companies = StockHolding.objects.filter(portfolio=portfolio)
#           fd = FundamentalData(key=get_alphavantage_key(), output_format='json')
#           for c in holding_companies:
#             data, meta_data = fd.get_company_overview(symbol=c.company_symbol)
#             print("pe")
#             # Getting values of beta and pe
#             portfolio_beta += float(data['Beta']) * (c.investment_amount / portfolio.total_investment)
#             portfolio_pe += float(data['PERatio']) * (c.investment_amount / portfolio.total_investment)
#             print(portfolio_pe)
#       print(portfolio_pe)
#       # return JsonResponse({"PortfolioBeta": portfolio_beta, "PortfolioPE": portfolio_pe})
#       return {"PortfolioBeta": portfolio_beta, "PortfolioPE": portfolio_pe}
#     except Exception as e:
#       print(e)
#       return {"Error": str(e)}

  # def get_financials(self,request):
  #   try:
  #     fd = FundamentalData(key=get_alphavantage_key(), output_format='json')
  #     print("get finance TILL HERE")

  #     data, meta_data = fd.get_company_overview(symbol=request.GET.get('symbol'))
  #     financials = {
  #       "52WeekHigh": data['52WeekHigh'],
  #       "52WeekLow": data['52WeekLow'],
  #       "Beta": data['Beta'],
  #       "BookValue": data['BookValue'],
  #       "EBITDA": data['EBITDA'],
  #       "EVToEBITDA": data['EVToEBITDA'],
  #       "OperatingMarginTTM": data['OperatingMarginTTM'],
  #       "PERatio": data['PERatio'],
  #       "PriceToBookRatio": data['PriceToBookRatio'],
  #       "ProfitMargin": data['ProfitMargin'],
  #       "ReturnOnAssetsTTM": data['ReturnOnAssetsTTM'],
  #       "ReturnOnEquityTTM": data['ReturnOnEquityTTM'],
  #       "Sector": data['Sector'],
  #     }
  #     # return JsonResponse({ "financials": financials })
  #     return { "financials": financials }
  #   except Exception as e:
  #     # return JsonResponse({"Error": str(e)})
  #     return {"Error": str(e)}


class Portfolio_():

  def updatePortfolio(self,request):
    port = Portfolio.objects.filter(user=request.user)
    portf = {}
    for idx,portfolio in enumerate(port):
#         print(portfolio)
        portfolio.update_investment()
        holding_companies = StockHolding.objects.filter(portfolio=portfolio)
        holdings = []
        sectors = [[], []]
        sector_wise_investment = {}
        stocks = [[], []]
        for c in holding_companies:
         company_symbol = c.company_symbol
         company_name = c.company_name
         number_shares = c.number_of_shares
         investment_amount = c.investment_amount
         average_cost = investment_amount / number_shares
         holdings.append({
           'CompanySymbol': company_symbol,
           'CompanyName': company_name,
           'NumberShares': number_shares,
           'InvestmentAmount': investment_amount,
           'AverageCost': average_cost,
         })

         stocks[0].append(round((investment_amount / portfolio.total_investment) * 100, 2))
         stocks[1].append(company_symbol)
         if c.sector in sector_wise_investment:
           sector_wise_investment[c.sector] += investment_amount
         else:
           sector_wise_investment[c.sector] = investment_amount
        for sec in sector_wise_investment.keys():
         sectors[0].append(round((sector_wise_investment[sec] / portfolio.total_investment) * 100, 2))
         sectors[1].append(sec)
        context = {
          'holdings': holdings,
          'totalInvestment': portfolio.total_investment,
          'stocks': stocks,
          'sectors': sectors,
        }
#         print(idx)
        portf[portfolio.portfolio_name]=context
#     print(portf)
    return portf
  
  def update_values(self,request):
    try:
      por = Portfolio.objects.filter(user=request.user)
      portfoliodata ={}
      for portfolio in por:
        current_value = 0
        unrealized_pnl = 0
        growth = 0
        holding_companies = StockHolding.objects.filter(portfolio=portfolio)
  #         print(holding_companies)
        stockdata = {}
        for idx,c in enumerate(holding_companies):
          ts = TimeSeries(key=get_alphavantage_key(), output_format='json')
          data, meta_data = ts.get_quote_endpoint(symbol=c.company_symbol)
          last_trading_price = float(data['05. price'])
          pnl = (last_trading_price * c.number_of_shares) - c.investment_amount
          net_change = pnl / c.investment_amount
          stockdata[c.company_symbol] = {
            'LastTradingPrice': last_trading_price,
            'PNL': pnl,
            'NetChange': net_change * 100
          }
          current_value += (last_trading_price * c.number_of_shares)
  #           print("hello")
          unrealized_pnl += pnl
  #           print(unrealized_pnl)
  #         print("working")
          if portfolio.total_investment>0:     
            growth = unrealized_pnl
          else:
            growth=0
          print(growth)
          ctx = {
              "StockData": stockdata, 
              "CurrentValue": current_value,
              "UnrealizedPNL": unrealized_pnl,
              "Growth": growth * 100
              }
          portfoliodata[portfolio.portfolio_name] = ctx
  #         print(ctx)
      print(portfoliodata)
      # return JsonResponse(portfoliodata)
      return portfoliodata

    except Exception as e:
      print(e)
      # return JsonResponse({"Error": str(e)})
      return {"Error": str(e)}

 


# class Transaction():
#   def add_holding(self,request):
#     if request.method == "POST":
#       try:
#         print("add holding")
#         print(request.POST['portfolio_select'])
#         portfolio = Portfolio.objects.get(user=request.user,portfolio_name=request.POST['portfolio_select'])
#         holding_companies = StockHolding.objects.filter(portfolio=portfolio)
#         company_symbol = request.POST['company'].split('(')[1].split(')')[0]
#         company_name = request.POST['company'].split('(')[0].strip()
#         number_stocks = int(request.POST['number-stocks'])
#         ts = TimeSeries(key=get_alphavantage_key() ,output_format='json')
#         data, meta_data = ts.get_intraday(symbol=company_symbol, interval='60min',outputsize='full')
#         buy_price = float(data[request.POST['date']+" 13:00:00"]['4. close'])
#         fd = FundamentalData(key=get_alphavantage_key(), output_format='json')
#         data, meta_data = fd.get_company_overview(symbol=company_symbol)
#         sector = data['Sector']
        

#         found = False
#         for c in holding_companies:
#           if c.company_symbol == company_symbol:
#             c.buying_value.append([buy_price, number_stocks])
#             c.save()
#             found = True

#         if not found:
#           c = StockHolding.objects.create(
#             portfolio=portfolio, 
#             portfolio_nameid = portfolio.portfolio_name,
#             company_name=company_name, 
#             company_symbol=company_symbol,
#             number_of_shares=number_stocks,
#             sector=sector
#           )
#           c.buying_value.append([buy_price, number_stocks])
#           c.save()

#         # return HttpResponse("Success")
#         return ("Success")
#       except Exception as e:
#         print(e)
#         # return HttpResponse(e)
#         return e
    
          



