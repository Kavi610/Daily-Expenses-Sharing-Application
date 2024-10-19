from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Expense, Split

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ['user', 'mobile_number']

class SplitSerializer(serializers.ModelSerializer):
    user = ProfileSerializer()

    class Meta:
        model = Split
        fields = ['user', 'amount', 'percentage']

class ExpenseSerializer(serializers.ModelSerializer):
    payer = ProfileSerializer()
    splits = SplitSerializer(many=True)

    class Meta:
        model = Expense
        fields = ['payer', 'total_amount', 'description', 'splits']
