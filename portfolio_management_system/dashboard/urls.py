from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('company-list', views.send_company_list, name="company-list"),
    path('update-prices', views.update_values, name="update-prices"),
    path('create-portfolio', views.create_portfolio, name="create-portfolio"),
    path('set-portfolio', views.set_portfolio, name="set-portfolio"),
    path('get-financials', views.get_financials, name="get-financials"),
    path('add-holding', views.add_holding, name="add-holding"),
    path('get-portfolio-insights', views.get_portfolio_insights, name="get-portfolio-insights"),
    path('backtesting', views.backtesting, name="backtesting"),
]