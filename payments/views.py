# payments/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from .models import PaymentMethod, Transaction, PaymentInitiation
from .serializers import PaymentMethodSerializer, TransactionSerializer, PaymentInitiationSerializer


class PaymentMethodViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(student__user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(student__user=self.request.user)

    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        student_id = request.data.get('student_id')
        amount = request.data.get('amount')
        payment_method_id = request.data.get('payment_method_id')
        
        if not all([student_id, amount, payment_method_id]):
            return Response({'error': 'student_id, amount and payment_method_id are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        transaction = Transaction.objects.create(
            student_id=student_id,
            amount=amount,
            payment_method_id=payment_method_id,
            reference_id=f"TXN-{student_id}-{Transaction.objects.count()+1}",
            status='pending'
        )
        
        serializer = self.get_serializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentInitiateViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentInitiationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PaymentInitiation.objects.filter(student__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        student_id = request.data.get('student_id')
        amount = request.data.get('amount')
        description = request.data.get('description', 'Payment')
        payment_gateway = request.data.get('payment_gateway', 'stripe')
        callback_url = request.data.get('callback_url')

        if not all([student_id, amount]):
            return Response({'error': 'student_id and amount are required'}, status=status.HTTP_400_BAD_REQUEST)

        payment_init = PaymentInitiation.objects.create(
            student_id=student_id,
            amount=amount,
            description=description,
            payment_gateway=payment_gateway,
            callback_url=callback_url,
            status='pending'
        )

        serializer = self.get_serializer(payment_init)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        payment_init = self.get_object()
        payment_method_id = request.data.get('payment_method_id')

        if not payment_method_id:
            return Response({'error': 'payment_method_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        transaction = Transaction.objects.create(
            student_id=payment_init.student_id,
            amount=payment_init.amount,
            payment_method_id=payment_method_id,
            reference_id=f"TXN-{payment_init.id}",
            status='completed',
            completed_at=datetime.now()
        )

        payment_init.transaction = transaction
        payment_init.status = 'completed'
        payment_init.save()

        serializer = self.get_serializer(payment_init)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel_payment(self, request, pk=None):
        payment_init = self.get_object()
        payment_init.status = 'cancelled'
        payment_init.save()
        
        serializer = self.get_serializer(payment_init)
        return Response(serializer.data, status=status.HTTP_200_OK)
