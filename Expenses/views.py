from django.forms import ValidationError
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Profile,Expense, Split
from .serializers import UserSerializer, ProfileSerializer,ExpenseSerializer
from rest_framework import status
from .models import Expense, Split, Profile
import pandas as pd
from django.http import HttpResponse
# Create your views here.
@api_view(['POST'])
def create_user(request):
    data = request.data
    user = User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
    profile = Profile.objects.create(user=user, mobile_number=data['mobile_number'])
    return Response(UserSerializer(user).data)

@api_view(['GET'])
def get_user(request, user_id):
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=user)
    return Response(ProfileSerializer(profile).data)

@api_view(['POST'])
def add_expense(request):
    data = request.data
    payer = Profile.objects.get(user_id=data['payer_id'])
    expense = Expense.objects.create(payer=payer, total_amount=data['total_amount'], description=data['description'])
    
    participants = Profile.objects.filter(id__in=data['participants'])
    
    # Handling different split types
    if data['split_type'] == 'equal':
        split_equally(expense, participants)
    elif data['split_type'] == 'exact':
        split_exact(expense, data['amounts'])
    elif data['split_type'] == 'percentage':
        split_percentage(expense, data['percentages'])

    return Response(ExpenseSerializer(expense).data, status=status.HTTP_201_CREATED)

def split_equally(expense, participants):
    amount_per_person = expense.total_amount / len(participants)
    for user in participants:
        Split.objects.create(expense=expense, user=user, amount=amount_per_person)

def split_exact(expense, amounts):
    for user_id, amount in amounts.items():
        user = Profile.objects.get(id=user_id)
        Split.objects.create(expense=expense, user=user, amount=amount)

def split_percentage(expense, percentages):
    total_percentage = sum(percentages.values())
    if total_percentage != 100:
        raise ValidationError("Percentages must add up to 100%")
    
    for user_id, percentage in percentages.items():
        user = Profile.objects.get(id=user_id)
        amount = expense.total_amount * (percentage / 100)
        Split.objects.create(expense=expense, user=user, amount=amount, percentage=percentage)
@api_view(['GET'])
def get_user_expenses(request, user_id):
    user = Profile.objects.get(user_id=user_id)
    expenses = Expense.objects.filter(splits__user=user)
    return Response(ExpenseSerializer(expenses, many=True).data)

@api_view(['GET'])
def get_all_expenses(request):
    expenses = Expense.objects.all()
    return Response(ExpenseSerializer(expenses, many=True).data)
def download_balance_sheet(request):
    expenses = Expense.objects.all()
    splits = Split.objects.select_related('user', 'expense')

    # Prepare data for CSV or Excel
    data = [{
        "User": split.user.user.username,
        "Amount": split.amount,
        "Expense": split.expense.description,
        "Date": split.expense.created_at,
    } for split in splits]

    df = pd.DataFrame(data)

    # Prepare the response for an Excel file download
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="balance_sheet.xlsx"'

    # Save the dataframe to an Excel file and return it in the response
    df.to_excel(response, index=False)
    return response
