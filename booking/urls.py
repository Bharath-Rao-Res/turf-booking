from django.urls import path
from . import views
from .views import(landing, home, book_turf, external_available_slots, external_details)


urlpatterns = [
    path('', landing, name='landing'),
    path('home/', home, name='home'),
    path('book/', book_turf, name='book_turf'),

    #External
    path('external-slots/', external_available_slots, name='external_slots'),
    path("external-details/", views.external_details, name="external_details"),
    path("external-receipt/", views.external_receipt_upload, name="external_receipt"),
    path('external-confirmation/', views.external_confirmation, name='external_confirmation'),

    #Internal
    path("internal/", views.internal_home, name="internal_home"),

    # STUDENT
    path("internal/student/signup/", views.student_signup, name="student_signup"),
    path("internal/student/signin/", views.student_signin, name="student_signin"),

    # FACULTY
    path("internal/faculty/signup/", views.faculty_signup, name="faculty_signup"),
    path("internal/faculty/signin/", views.faculty_signin, name="faculty_signin"),

    # INTERNAL SLOTS
     path("internal/slots/", views.internal_available_slots, name="internal_slots"),

    # LOGOUT
    path("logout/", views.logout_user, name="logout"),

    path('internal-details/', views.internal_details, name='internal_details'),


]
