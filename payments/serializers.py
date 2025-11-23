from rest_framework import serializers
from .models import PaymentMethod, Transaction

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'student', 'payment_type', 'is_primary', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'student', 'amount', 'status', 'payment_method', 
                  'reference_id', 'created_at', 'completed_at']
        read_only_fields = ['created_at', 'completed_at']
