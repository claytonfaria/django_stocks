from django.shortcuts import render, redirect
from . models import Stock
from . forms import StockForm
from django.contrib import messages
import requests
import json
import pandas as pd
from django.db import models
from django_pandas.managers import DataFrameManager
from collections import namedtuple

def home(request):


	if request.method == 'POST':
		 
		ticker = request.POST['ticker'].upper()

		stock = ticker

		url_histdata = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="+ ticker +".SA&outputsize=compact&apikey=8O3XROC4HDBLWGE8"

		sec_data = namedtuple("SecurityData", ["Date", "Open", "High","Low", "AdjClose","Volume","DivAmt","Split"])

		url_profile = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/" + ticker + ".SA?modules=assetProfile"

		api_profile_request = requests.request("GET",url_profile)
		api_histdata_request = requests.request("GET",url_histdata)

		all_data = []

		try:
			api_profile = json.loads(api_profile_request.content)
			api_histdata = json.loads(api_histdata_request.content)
			
		except Exception as e:
			api_profile, api_histdata = "Erro, tente novamente"

		summary = api_profile['quoteSummary']
		summary_results = summary['result']
		asset_profile = summary_results[0]['assetProfile']
		stock_name_slice = slice(summary_results[0]['assetProfile'].get("longBusinessSummary").index("S.A.") +4)
		stock_name = summary_results[0]['assetProfile'].get("longBusinessSummary")[stock_name_slice]

		if api_histdata is not None:

			hist_data = api_histdata['Time Series (Daily)']

			for time, prices in hist_data.items():
				data = sec_data(time, prices['1. open'], prices['2. high'],prices['3. low'],prices['5. adjusted close'],prices['6. volume'],prices['7. dividend amount'],prices['8. split coefficient'])
				all_data.append(data)
				
		return render(request,'home.html', {'api_profile': api_profile,'api_histdata': api_histdata, 'asset_profile' : asset_profile , 'summary_results' : summary_results , 'summary_results' : summary_results, 'stock' : stock, 'stock_name' : stock_name, 'all_data' : all_data})
	
	else:

		return render(request,'home.html', {'stock': "Busque uma ação na caixa de pesquisa."})

def about(request):
	return render(request,'about.html',{})

def add_stock(request):

	if request.method == 'POST':

		form = StockForm(request.POST or None)

		if form.is_valid():

			form.save()
			messages.success(request, ("A ação foi adicionada ao portfolio!"))
			return redirect('add_stock')

	else:

		ticker = Stock.objects.all()
		return render(request,'add_stock.html',{'ticker':ticker})

def delete (request, stock_id):

	item = Stock.objects.get(pk=stock_id)
	item.delete()
	messages.success(request,("A Ação foi excluída com sucesso!"))
	return redirect (add_stock)