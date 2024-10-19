from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.create_user, name='create_user'),
    path('users/<int:user_id>/', views.get_user, name='get_user'),
    path('expenses/', views.add_expense, name='add_expense'),
    path('expenses/user/<int:user_id>/', views.get_user_expenses, name='get_user_expenses'),
    path('expenses/all/', views.get_all_expenses, name='get_all_expenses'),
    path('expenses/balance-sheet/download/', views.download_balance_sheet, name='download_balance_sheet'),
]
