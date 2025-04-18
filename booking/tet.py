from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import date
from .models import Booking

class UserDashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()

        total_bookings = Booking.objects.filter(user=user).count()
        active_booking = Booking.objects.filter(
            user=user,
            start_time__date=today
        ).order_by('start_time').first()

        return Response({
            "my_bookings": total_bookings,
            "active_booking": {
                "seat": active_booking.seat.label if active_booking else None,
                "workspace": active_booking.seat.workspace.name if active_booking else None,
                "start_time": active_booking.start_time if active_booking else None,
                "end_time": active_booking.end_time if active_booking else None,
            } if active_booking else None,
            "booking_history_url": "/api/bookings/my/"
        })
