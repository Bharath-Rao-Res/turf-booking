from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import Profile
import re
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pytz
from django.utils.timezone import localtime, now
from openpyxl import load_workbook
from .models import InternalBooking
from django.utils import timezone


def book_turf(request):
    if request.method == "POST":
        Booking.objects.create(
            name=request.POST['name'],
            phone=request.POST['phone'],
            date=request.POST['date'],
            time_slot=request.POST['time_slot']
        )
        return render(request, 'success.html')
    return render(request, 'book.html')

def landing(request):
    return render(request, 'landing.html')

def home(request):
    return render(request, 'home.html')

def external_available_slots(request):
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    # DEFAULT to today
    selected_day = request.GET.get("day", "today")
    slots = []

    def format_slot(start_hour):
        start = datetime.strptime(f"{start_hour}", "%H")
        end = datetime.strptime(f"{start_hour + 1}", "%H")
        return f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}"

    def get_slots(date_obj):
        day = date_obj.weekday()  # Mon=0 ... Sun=6

        if day <= 4:  # Monday–Friday
            hours = range(8, 15)   # 8 AM – 3 PM
        else:         # Saturday–Sunday
            hours = range(7, 21)   # 7 AM – 9 PM

        return [format_slot(h) for h in hours]

    if selected_day == "today":
        slots = get_slots(today)
    elif selected_day == "tomorrow":
        slots = get_slots(tomorrow)

    context = {
        "today_label": today.strftime("Today – %a (%d %b)"),
        "tomorrow_label": tomorrow.strftime("Tomorrow – %a (%d %b)"),
        "selected_day": selected_day,
        "slots": slots,
    }

    return render(request, "external_slots.html", context)


def external_details(request):
    day = request.GET.get("day")
    slot = request.GET.get("slot")

    if day == "today":
        date_obj = datetime.now().date()
    else:
        date_obj = (datetime.now() + timedelta(days=1)).date()

    context = {
        "day": day,
        "date": date_obj.strftime("%d %b %Y"),
        "slot": slot,
    }
    return render(request, "external_details.html", context)

def external_receipt_upload(request):
    if request.method == "POST":
        receipt = request.FILES.get("receipt")

        if not receipt:
            return render(request, "external_receipt.html", {
                "error": "Please upload payment receipt"
            })

        # For now just confirm upload (later we can save to DB)
        return render(request, "external_receipt.html", {
            "success": "Receipt uploaded successfully!"
        })

    return render(request, "external_receipt.html")


def external_receipt_upload(request):
    if request.method == "POST":
        receipt = request.FILES.get("receipt")

        if not receipt:
            return render(request, "external_receipt.html", {
                "error": "Receipt is required"
            })

        # Later you can save receipt to DB
        return redirect("external_confirmation")

    return render(request, "external_receipt.html")

def external_confirmation(request):
    return render(request, "external_confirmation.html")



def internal_home(request):
    return render(request, "internal_home.html")

def student_signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # ✅ CHECK IF EMAIL ALREADY EXISTS
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email is already registered")
            return redirect("student_signup")

        # ✅ CREATE USER
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        # ✅ AUTO LOGIN
        login(request, user)
        return redirect("internal_slots")

    return render(request, "student_signup.html")


def student_signin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # 🔑 Authenticate using username=email
        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("internal_slots")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "student_signin.html")

def faculty_signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # ❌ NO email restriction for faculty

        if User.objects.filter(username=email).exists():
            messages.error(request, "This email is already registered")
            return redirect("faculty_signup")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name,
            is_staff=True   # optional (good practice)
        )

        login(request, user)
        return redirect("internal_slots")

    return render(request, "faculty_signup.html")


def faculty_signin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("internal_slots")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "faculty_signin.html")



@login_required(login_url="student_signin")
def internal_slots(request):
    return render(request, "internal_slots.html")

@login_required
def internal_slots(request):
    return render(request, "internal_slots.html")

def logout_user(request):
    logout(request)
    return redirect("home")



def internal_available_slots(request):
    today = localtime(now())
    tomorrow = today + timedelta(days=1)

    selected_day = request.GET.get("day", "today")
    slots = []

    def weekend_slots():
        # 7:00 AM – 9:00 PM (1 hour slots)
        result = []
        for h in range(7, 21):
            start = datetime.strptime(str(h), "%H")
            end = datetime.strptime(str(h + 1), "%H")
            result.append(
                f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}"
            )
        return result

    def weekday_slots():
        return [
            "05:30 AM - 06:30 AM",
            "06:30 AM - 07:30 AM",
            "04:30 PM - 05:30 PM (Girls Only)",
            "05:30 PM - 06:30 PM",
            "06:30 PM - 07:30 PM",
            "07:30 PM - 08:30 PM",
            "08:30 PM - 09:30 PM",
        ]

    def get_slots(date_obj):
        day = date_obj.weekday()  # Mon=0 ... Sun=6
        if day <= 4:  # Monday–Friday
            return weekday_slots()
        else:         # Saturday–Sunday
            return weekend_slots()

    if selected_day == "today":
        slots = get_slots(today)
    elif selected_day == "tomorrow":
        slots = get_slots(tomorrow)

    context = {
        "today_label": today.strftime("Today – %a (%d %b)"),
        "tomorrow_label": tomorrow.strftime("Tomorrow – %a (%d %b)"),
        "selected_day": selected_day,
        "slots": slots,
    }

    return render(request, "internal_slots.html", context)

def internal_details(request):
    day = request.GET.get('day') or request.POST.get('day')
    slot = request.GET.get('slot') or request.POST.get('slot')

    is_faculty = request.user.is_staff  # ✅ KEY LINE

    if request.method == "POST":
        num_persons = int(request.POST.get('num_persons'))
        excel_file = request.FILES.get('persons_file')

        try:
            wb = load_workbook(excel_file)
            sheet = wb.active
            rows = list(sheet.iter_rows(min_row=2, values_only=True))
        except Exception:
            return render(request, 'internal_details.html', {
                'day': day,
                'slot': slot,
                'error': 'Invalid Excel file'
            })

        # 🔹 Person count check
        if len(rows) != num_persons:
            return render(request, 'internal_details.html', {
                'day': day,
                'slot': slot,
                'error': 'Number of persons does not match Excel rows'
            })

        one_week_ago = timezone.now() - timedelta(days=7)

        # ================= FACULTY FLOW =================
        if is_faculty:
            header = [cell.value for cell in sheet[1]]
            if header != ['Name']:
                return render(request, 'internal_details.html', {
                    'day': day,
                    'slot': slot,
                    'error': 'Excel must contain only Name column for faculty'
                })

            for index, row in enumerate(rows, start=2):
                name = row[0]
                if not name:
                    return render(request, 'internal_details.html', {
                        'day': day,
                        'slot': slot,
                        'error': f'Empty name at row {index}'
                    })

            # ✅ Save faculty booking (no reg numbers)
            for _ in rows:
                InternalBooking.objects.create(
                    reg_no=None   # or 'FACULTY'
                )

        # ================= STUDENT FLOW =================
        else:
            header = [cell.value for cell in sheet[1]]
            if header[:2] != ['Name', 'Register Number']:
                return render(request, 'internal_details.html', {
                    'day': day,
                    'slot': slot,
                    'error': 'Excel must have Name and Register Number columns'
                })

            for index, row in enumerate(rows, start=2):
                name, reg_no = row[0], row[1]

                if not name or not reg_no:
                    return render(request, 'internal_details.html', {
                        'day': day,
                        'slot': slot,
                        'error': f'Empty value at row {index}'
                    })

                reg_no = str(reg_no).strip()

                if not re.match(r'^(21|22|23|24|25)\d{14}$', reg_no):
                    return render(request, 'internal_details.html', {
                        'day': day,
                        'slot': slot,
                        'error': f'Invalid register number at row {index}'
                    })

                weekly_count = InternalBooking.objects.filter(
                    reg_no=reg_no,
                    booking_date__gte=one_week_ago
                ).count()

                if weekly_count >= 5:
                    return render(request, 'internal_details.html', {
                        'day': day,
                        'slot': slot,
                        'error': f'Register number {reg_no} exceeded weekly limit'
                    })

            # ✅ Save student bookings
            for row in rows:
                reg_no = str(row[1]).strip()
                    

        return render(request, 'success.html', {
            'day': day,
            'slot': slot,
            'num_persons': num_persons
        })

    return render(request, 'internal_details.html', {
        'day': day,
        'slot': slot
    })