from rest_framework import serializers
from bank_app.models import Transction, BankAccounts
from django.utils import timezone
from django.db.models import Sum


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transction
        fields = ['amount',]

    def validate(self, data):
        amount = data.get('amount')
        if float(amount) > 5000:
            raise serializers.ValidationError(
                'You can deposit up to 5000 at a time')

        # check total amount of 24 hours
        today = timezone.now().date()
        user = self.context['user']
        total_withdrawal = Transction.objects.filter(
            user=user, transction_type=Transction.TRANSACTION_TYPE_CHOICES[0][0], current_time__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
        if total_withdrawal + int(amount) > 30000:
            raise serializers.ValidationError(
                "You have reached the maximum daily withdrawal limit of 25,000.")
        return data


class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transction
        fields = ['amount',]

    def validate(self, data):
        amount = data.get('amount')
        user = self.context['user']

        trans = Transction.objects.filter(user=user).first()
        if trans:
            if trans.balance < int(amount):
                raise serializers.ValidationError(
                    "Low balance. Unable to withdraw amount.")
        else:
            raise serializers.ValidationError(
                "Unable to withdraw amount.")

        if float(amount) > 5000:
            raise serializers.ValidationError(
                'You can withdraw up to 10,000 at a time.')

          # check total amount of 24 hours
        today = timezone.now().date()
        total_withdrawal = Transction.objects.filter(
            user=user, transction_type=Transction.TRANSACTION_TYPE_CHOICES[0][0], current_time__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
        if total_withdrawal + int(amount) > 30000:
            raise serializers.ValidationError(
                "You have reached the maximum daily withdrawal limit of 30,000.")
        return data


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transction
        fields = "__all__"


class BankAccountSerializer(serializers.ModelSerializer):
    account_number = serializers.SerializerMethodField()

    def get_account_number(self, obj):
        return self.context.get("account_number")

    class Meta:
        model = BankAccounts
        fields = ['nickname', 'account_number']


class TransctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transction
        fields = "__all__"


class TransferamountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transction
        fields = ["amount",]


class BalanceUserSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(decimal_places=2, max_digits=12)

    class Meta:
        model = Transction
        fields = ["user", "balance",]
