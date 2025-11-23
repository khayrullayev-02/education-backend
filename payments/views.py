from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PaymentMethod, Transaction
from .serializers import PaymentMethodSerializer, TransactionSerializer


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
        
        transaction = Transaction.objects.create(
            student_id=student_id,
            amount=amount,
            payment_method_id=payment_method_id,
            reference_id=f"TXN-{student_id}-{Transaction.objects.count()}"
        )
        
        serializer = self.get_serializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
