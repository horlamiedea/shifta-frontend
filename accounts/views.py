from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from core.router import route
from .services import UserRegisterService, UserLoginService, AdminVerifyFacilityService, AdminVerifyProfessionalService, ProfessionalUpdateService
from .selectors import UserSelector

@route("auth/register/", name="register")
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user_type = request.data.get("user_type") # professional or facility
        
        # Extract specific fields based on type
        extra_data = {}
        if user_type == "professional":
            extra_data["license_number"] = request.data.get("license_number")
            # Add other fields as needed
        elif user_type == "facility":
            extra_data["name"] = request.data.get("name")
            extra_data["address"] = request.data.get("address")
            extra_data["rc_number"] = request.data.get("rc_number")

        service = UserRegisterService()
        try:
            user, token = service(email=email, password=password, user_type=user_type, **extra_data)
            
            return Response({
                "token": token,
                "user_id": user.id,
                "email": user.email,
                "role": user_type
            }, status=201)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

@route("auth/login/", name="login")
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        
        service = UserLoginService()
        try:
            user, token = service(email=email, password=password)
            
            return Response({
                "token": token,
                "user_id": user.id,
                "email": user.email
            })
        except ValueError as e:
            return Response({"error": str(e)}, status=401)

@route("auth/profile/", name="profile")
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        selector = UserSelector()
        data = selector.get_profile_data(request.user)
        return Response(data)

    def put(self, request):
        user = request.user
        # Only professionals for now based on Epic 2
        if user.is_professional:
            specialties = request.data.get("specialties")
            location_lat = request.data.get("location_lat")
            location_lng = request.data.get("location_lng")
            cv_url = request.data.get("cv_url")
            certificate_url = request.data.get("certificate_url")
            
            service = ProfessionalUpdateService()
            try:
                service(user=user, specialties=specialties, location_lat=location_lat, location_lng=location_lng, cv_url=cv_url, certificate_url=certificate_url)
                return Response({"status": "updated"})
            except ValueError as e:
                return Response({"error": str(e)}, status=400)
        
        return Response({"status": "not implemented for this user type"}, status=400)


@route("admin/verify-facility/", name="verify-facility")
class AdminVerifyFacilityView(APIView):
    permission_classes = [IsAuthenticated] # Should be IsAdminUser really

    def post(self, request):
        facility_id = request.data.get("facility_id")
        tier = request.data.get("tier")
        credit_limit = request.data.get("credit_limit")
        
        service = AdminVerifyFacilityService()
        try:
            facility = service(facility_id=facility_id, tier=tier, credit_limit=credit_limit, admin_user=request.user)
            return Response({"status": "verified", "facility": facility.name})
        except PermissionError as e:
            return Response({"error": str(e)}, status=403)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

@route("admin/verify-professional/", name="verify-professional")
class AdminVerifyProfessionalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        professional_id = request.data.get("professional_id")
        
        service = AdminVerifyProfessionalService()
        try:
            professional = service(professional_id=professional_id, admin_user=request.user)
            return Response({"status": "verified", "professional": professional.user.email})
        except PermissionError as e:
            return Response({"error": str(e)}, status=403)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

@route("auth/waitlist/", name="waitlist-create")
class WaitlistCreateView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        from .models import WaitlistProfessional
        
        email = request.data.get("email")
        full_name = request.data.get("full_name")
        phone_number = request.data.get("phone_number")
        medical_type = request.data.get("medical_type")
        bio_data = request.data.get("bio_data")
        location = request.data.get("location")
        preferred_work_address = request.data.get("preferred_work_address")
        shift_rate_9hr = request.data.get("shift_rate_9hr")
        years_of_experience = request.data.get("years_of_experience")
        
        cv_file = request.FILES.get("cv_file")
        license_file = request.FILES.get("license_file")
        
        if not email or not full_name:
             return Response({"error": "Email and Name are required"}, status=400)
             
        if WaitlistProfessional.objects.filter(email=email).exists():
            return Response({"message": "Already on waitlist"}, status=200)
            
        WaitlistProfessional.objects.create(
            email=email,
            full_name=full_name,
            phone_number=phone_number,
            medical_type=medical_type,
            bio_data=bio_data,
            location=location,
            preferred_work_address=preferred_work_address,
            shift_rate_9hr=shift_rate_9hr,
            years_of_experience=years_of_experience,
            cv_file=cv_file,
            license_file=license_file
        )
        
        return Response({"status": "success", "message": "Added to waitlist"}, status=201)

@route("facility/documents/", name="facility-document-upload")
class FacilityDocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if not request.user.is_facility:
            return Response({"error": "Only facilities can upload documents"}, status=403)
            
        facility = request.user.facility
        
        cac_file = request.FILES.get("cac_file")
        license_file = request.FILES.get("license_file")
        other_documents = request.FILES.get("other_documents")
        
        if cac_file:
            facility.cac_file = cac_file
        if license_file:
            facility.license_file = license_file
        if other_documents:
            facility.other_documents = other_documents
            
        facility.save()
        
        return Response({"status": "success", "message": "Documents uploaded successfully"})

@route("facility/staff/", name="facility-staff-list")
class FacilityStaffListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_facility:
            return Response({"error": "Only facilities can view staff"}, status=403)
            
        facility = request.user.facility
        # Get all staff associated with this facility
        # Note: The FacilityStaff model links User to Facility. 
        # We need to fetch FacilityStaff objects where facility=facility
        from .models import FacilityStaff
        
        staff_members = FacilityStaff.objects.filter(facility=facility)
        
        data = [{
            "id": str(s.id),
            "email": s.user.email,
            "role": s.role,
            "permissions": {
                "can_create_shifts": s.can_create_shifts,
                "can_manage_staff": s.can_manage_staff
            }
        } for s in staff_members]
        
        return Response(data)

