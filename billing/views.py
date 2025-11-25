from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from core.router import route
from .models import Invoice, Transaction
from .services import WithdrawalService, ReleaseFundsService
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, inline_serializer
from rest_framework import serializers

@extend_schema(
    responses={
        200: inline_serializer(
            name='InvoiceListResponse',
            many=True,
            fields={
                'id': serializers.UUIDField(),
                'month': serializers.CharField(),
                'amount': serializers.DecimalField(max_digits=12, decimal_places=2),
                'status': serializers.CharField(),
                'pdf_url': serializers.URLField()
            }
        ),
        403: inline_serializer(name='InvoicePermissionError', fields={'error': serializers.CharField()})
    }
)

@route("billing/invoices/", name="invoice-list")
class InvoiceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_facility:
             return Response({"error": "Only facilities have invoices"}, status=403)
             
        invoices = Invoice.objects.filter(facility=request.user.facility).order_by('-created_at')
        data = [{
            "id": i.id,
            "month": i.month,
            "amount": i.amount,
            "status": i.status,
            "pdf_url": i.pdf_url
        } for i in invoices]
        return Response(data)

@extend_schema(
    responses={
        200: inline_serializer(
            name='TransactionListResponse',
            many=True,
            fields={
                'id': serializers.UUIDField(),
                'type': serializers.CharField(),
                'amount': serializers.DecimalField(max_digits=12, decimal_places=2),
                'status': serializers.CharField(),
                'created_at': serializers.DateTimeField()
            }
        )
    }
)
@route("billing/transactions/", name="transaction-list")
class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
        data = [{
            "id": t.id,
            "type": t.transaction_type,
            "amount": t.amount,
            "status": t.status,
            "created_at": t.created_at
        } for t in transactions]
        return Response(data)

@extend_schema(
    request=inline_serializer(
        name='WithdrawalRequest',
        fields={
            'amount': serializers.DecimalField(max_digits=12, decimal_places=2),
        }
    ),
    responses={
        200: inline_serializer(
            name='WithdrawalResponse',
            fields={'status': serializers.CharField(), 'transaction_id': serializers.UUIDField()}
        ),
        400: inline_serializer(name='WithdrawalValidationError', fields={'error': serializers.CharField()})
    }
)
@route("billing/withdraw/", name="withdraw")
class WithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        if not amount:
            return Response({"error": "Amount is required"}, status=400)
            
        service = WithdrawalService()
        result = service(user=request.user, amount=Decimal(amount))
        return Response(result)

@extend_schema(
    responses={
        200: inline_serializer(
            name='ReleaseFundsResponse',
            fields={'status': serializers.CharField()}
        )
    }
)
@route("billing/release-funds/<uuid:application_id>/", name="release-funds")
class ReleaseFundsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, application_id):
        service = ReleaseFundsService()
        result = service(user=request.user, application_id=application_id)
        return Response(result)

