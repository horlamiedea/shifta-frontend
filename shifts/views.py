from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.router import route
from .services import ShiftCreateService, ShiftApplyService, ShiftManageApplicationService, ClockInService, ClockOutService
from .cancellation_services import FacilityCancelShiftService, ProfessionalCancelShiftService
from .approval_services import ApproveShiftStartService
from .selectors import ShiftSelector
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, inline_serializer
from rest_framework import serializers

@extend_schema(
    parameters=[
        OpenApiParameter(name='specialty', description='Filter by specialty', required=False, type=str),
    ],
    responses={
        200: inline_serializer(
            name='ShiftListResponse',
            many=True,
            fields={
                'id': serializers.CharField(),
                'facility': serializers.CharField(),
                'role': serializers.CharField(),
                'specialty': serializers.CharField(),
                'start_time': serializers.DateTimeField(),
                'rate': serializers.DecimalField(max_digits=10, decimal_places=2)
            }
        )
    }
)

@route("shifts/", name="shift-list-create")
class ShiftListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        selector = ShiftSelector()
        # Filter by specialty if provided
        specialty = request.query_params.get("specialty")
        shifts = selector.list_open_shifts(specialty=specialty)
        
        data = [{
            "id": str(s.id),
            "facility": s.facility.name,
            "role": s.role,
            "specialty": s.specialty,
            "start_time": s.start_time,
            "rate": s.rate
        } for s in shifts]
        
        return Response(data)

    @extend_schema(
        request=inline_serializer(
            name='ShiftCreateRequest',
            fields={
                'role': serializers.CharField(),
                'specialty': serializers.CharField(),
                'quantity_needed': serializers.IntegerField(),
                'start_time': serializers.DateTimeField(),
                'end_time': serializers.DateTimeField(),
                'rate': serializers.DecimalField(max_digits=10, decimal_places=2),
                'is_negotiable': serializers.BooleanField(required=False),
                'min_rate': serializers.DecimalField(max_digits=10, decimal_places=2, required=False),
            }
        ),
        responses={
            201: inline_serializer(
                name='ShiftCreateResponse',
                fields={
                    'id': serializers.UUIDField(),
                    'status': serializers.CharField()
                }
            ),
            403: inline_serializer(name='ShiftCreatePermissionError', fields={'error': serializers.CharField()}),
            400: inline_serializer(name='ShiftCreateValidationError', fields={'error': serializers.CharField()})
        }
    )
    def post(self, request):
        service = ShiftCreateService()
        try:
            shift = service(
                user=request.user,
                role=request.data.get("role"),
                specialty=request.data.get("specialty"),
                quantity_needed=request.data.get("quantity_needed"),
                start_time=request.data.get("start_time"),
                end_time=request.data.get("end_time"),
                rate=request.data.get("rate"),
                is_negotiable=request.data.get("is_negotiable", False),
                min_rate=request.data.get("min_rate")
            )
            return Response({"id": shift.id, "status": "created"}, status=201)
        except PermissionError as e:
            return Response({"error": str(e)}, status=403)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

@extend_schema(
    responses={
        200: inline_serializer(
            name='ShiftApplyResponse',
            fields={
                'status': serializers.CharField(),
                'application_id': serializers.IntegerField()
            }
        ),
        403: inline_serializer(name='ApplyPermissionError', fields={'error': serializers.CharField()}),
        400: inline_serializer(name='ApplyValidationError', fields={'error': serializers.CharField()})
    }
)
@route("shifts/<uuid:shift_id>/apply/", name="shift-apply")
class ShiftApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, shift_id):
        service = ShiftApplyService()
        try:
            application = service(user=request.user, shift_id=shift_id)
            return Response({"status": "applied", "application_id": application.id})
        except PermissionError as e:
            return Response({"error": str(e)}, status=403)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

@extend_schema(
    request=inline_serializer(
        name='ShiftApplicationManageRequest',
        fields={
            'action': serializers.ChoiceField(choices=['CONFIRM', 'REJECT']),
        }
    ),
    responses={
        200: inline_serializer(
            name='ShiftApplicationManageResponse',
            fields={'status': serializers.CharField()}
        ),
        403: inline_serializer(name='ManagePermissionError', fields={'error': serializers.CharField()}),
        400: inline_serializer(name='ManageValidationError', fields={'error': serializers.CharField()})
    }
)
@route("shifts/applications/<int:application_id>/manage/", name="shift-application-manage")
class ShiftApplicationManageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, application_id):
        action = request.data.get("action") # CONFIRM or REJECT
        service = ShiftManageApplicationService()
        try:
            service(user=request.user, application_id=application_id, action=action)
            return Response({"status": "success"})
        except PermissionError as e:
            return Response({"error": str(e)}, status=403)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

@extend_schema(
    responses={
        200: inline_serializer(
            name='FacilityQRCodeResponse',
            fields={'qr_data': serializers.CharField()}
        ),
        403: inline_serializer(name='QRCodePermissionError', fields={'error': serializers.CharField()})
    }
)
@route("facility/qrcode/", name="facility-qrcode")
class FacilityQRCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_facility:
            return Response({"error": "Only facilities have QR codes"}, status=403)
            
        # Return the facility ID as the QR code data
        # Frontend will generate the QR image from this string.
        return Response({"qr_data": str(request.user.facility.id)})

@extend_schema(
    request=inline_serializer(
        name='ShiftClockInRequest',
        fields={
            'lat': serializers.FloatField(),
            'lng': serializers.FloatField(),
            'qr_code_data': serializers.CharField(),
        }
    ),
    responses={
        200: inline_serializer(
            name='ShiftClockInResponse',
            fields={'status': serializers.CharField()}
        ),
        403: inline_serializer(name='ClockInPermissionError', fields={'error': serializers.CharField()}),
        400: inline_serializer(name='ClockInValidationError', fields={'error': serializers.CharField()})
    }
)
@route("shifts/<uuid:shift_id>/clock-in/", name="shift-clock-in")
class ShiftClockInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, shift_id):
        lat = request.data.get("lat")
        lng = request.data.get("lng")
        qr_code_data = request.data.get("qr_code_data")
        
        service = ClockInService()
        try:
            service(user=request.user, shift_id=shift_id, lat=lat, lng=lng, qr_code_data=qr_code_data)
            return Response({"status": "clocked_in"})
        except PermissionError as e:
            return Response({"error": str(e)}, status=403)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

@extend_schema(
    request=inline_serializer(
        name='ShiftClockOutRequest',
        fields={
            'lat': serializers.FloatField(),
            'lng': serializers.FloatField(),
            'qr_code_data': serializers.CharField(),
        }
    ),
    responses={
        200: inline_serializer(
            name='ShiftClockOutResponse',
            fields={'status': serializers.CharField()}
        ),
        403: inline_serializer(name='ClockOutPermissionError', fields={'error': serializers.CharField()}),
        400: inline_serializer(name='ClockOutValidationError', fields={'error': serializers.CharField()})
    }
)
@route("shifts/<uuid:shift_id>/clock-out/", name="shift-clock-out")
class ShiftClockOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, shift_id):
        lat = request.data.get("lat")
        lng = request.data.get("lng")
        qr_code_data = request.data.get("qr_code_data")
        
        service = ClockOutService()
        try:
            service(user=request.user, shift_id=shift_id, lat=lat, lng=lng, qr_code_data=qr_code_data)
            return Response({"status": "clocked_out"})
        except PermissionError as e:
            return Response({"error": str(e)}, status=403)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

@extend_schema(
    request=inline_serializer(
        name='ShiftCancelRequest',
        fields={
            'professional_id': serializers.CharField(required=False, help_text='Required for facility cancellation'),
        }
    ),
    responses={
        200: inline_serializer(
            name='ShiftCancelResponse',
            fields={'status': serializers.CharField(), 'message': serializers.CharField(required=False)}
        ),
        403: inline_serializer(name='CancelPermissionError', fields={'error': serializers.CharField()}),
        400: inline_serializer(name='CancelValidationError', fields={'error': serializers.CharField()})
    }
)
@route("shifts/<uuid:shift_id>/cancel/", name="shift-cancel")
class ShiftCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, shift_id):
        try:
            if request.user.is_facility:
                professional_id = request.data.get("professional_id")
                service = FacilityCancelShiftService()
                result = service(user=request.user, shift_id=shift_id, professional_id=professional_id)
                return Response(result)
            elif request.user.is_professional:
                service = ProfessionalCancelShiftService()
                result = service(user=request.user, shift_id=shift_id)
                return Response(result)
            else:
                return Response({"error": "Invalid user role"}, status=403)
        except PermissionError as e:
            return Response({"error": str(e)}, status=403)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

@extend_schema(
    responses={
        200: inline_serializer(
            name='FacilityShiftListResponse',
            many=True,
            fields={
                'id': serializers.UUIDField(),
                'role': serializers.CharField(),
                'start_time': serializers.DateTimeField(),
                'end_time': serializers.DateTimeField(),
                'status': serializers.CharField(),
                'quantity_needed': serializers.IntegerField(),
                'quantity_filled': serializers.IntegerField(),
                'rate': serializers.DecimalField(max_digits=10, decimal_places=2)
            }
        ),
        403: inline_serializer(name='FacilityShiftListPermissionError', fields={'error': serializers.CharField()})
    }
)
@route("shifts/facility/", name="facility-shift-list")
class FacilityShiftListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_facility:
            return Response({"error": "Only facilities can view this."}, status=403)
            
        selector = ShiftSelector()
        shifts = selector.list_facility_shifts(request.user.facility)
        
        data = [{
            "id": shift.id,
            "role": shift.role,
            "start_time": shift.start_time,
            "end_time": shift.end_time,
            "status": shift.status,
            "quantity_needed": shift.quantity_needed,
            "quantity_filled": shift.quantity_filled,
            "rate": shift.rate
        } for shift in shifts]
        
        return Response(data)

@extend_schema(
    responses={
        200: inline_serializer(
            name='FacilityDashboardStatsResponse',
            fields={
                'active_shifts': serializers.IntegerField(),
                'staff_on_duty': serializers.IntegerField(),
                'pending_applications': serializers.IntegerField(),
                'total_spent': serializers.DecimalField(max_digits=12, decimal_places=2),
                'is_verified': serializers.BooleanField()
            }
        ),
        403: inline_serializer(name='StatsPermissionError', fields={'error': serializers.CharField()})
    }
)
@route("facility/dashboard/stats/", name="facility-dashboard-stats")
class FacilityDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_facility:
            return Response({"error": "Only facilities can view stats"}, status=403)
            
        facility = request.user.facility
        from .models import Shift, ShiftApplication
        
        active_shifts = Shift.objects.filter(facility=facility, status='OPEN').count()
        # Staff on duty: Confirmed applications for shifts happening now (simplified to IN_PROGRESS or just CONFIRMED for now)
        # For better accuracy we'd check time, but let's use status if available or just confirmed count
        staff_on_duty = ShiftApplication.objects.filter(shift__facility=facility, status__in=['IN_PROGRESS', 'CONFIRMED']).count()
        pending_applications = ShiftApplication.objects.filter(shift__facility=facility, status='PENDING').count()
        
        # Total Spent (Placeholder for Phase 2)
        total_spent = 0 
        
        return Response({
            "active_shifts": active_shifts,
            "staff_on_duty": staff_on_duty,
            "pending_applications": pending_applications,
            "total_spent": total_spent,
            "is_verified": facility.is_verified
        })

@extend_schema(
    responses={
        200: inline_serializer(
            name='ProfessionalShiftListResponse',
            many=True,
            fields={
                'id': serializers.UUIDField(),
                'facility': serializers.CharField(),
                'role': serializers.CharField(),
                'start_time': serializers.DateTimeField(),
                'end_time': serializers.DateTimeField(),
                'rate': serializers.DecimalField(max_digits=10, decimal_places=2),
                'distance': serializers.CharField()
            }
        ),
        403: inline_serializer(name='ProfShiftListPermissionError', fields={'error': serializers.CharField()})
    }
)
@route("shifts/professional/", name="professional-shift-list")
class ProfessionalShiftListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_professional:
            return Response({"error": "Only professionals can view this."}, status=403)
            
        selector = ShiftSelector()
        shifts = selector.list_professional_shifts(request.user.professional)
        
        data = [{
            "id": shift.id,
            "facility": shift.facility.name,
            "role": shift.role,
            "start_time": shift.start_time,
            "end_time": shift.end_time,
            "rate": shift.rate,
            "distance": "5km" # Placeholder or calculate
        } for shift in shifts]
        
        return Response(data)



