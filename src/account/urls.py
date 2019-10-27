from django.urls import path, reverse_lazy, re_path, include
from django.conf import settings
from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordResetView,\
                                      PasswordResetConfirmView, PasswordResetCompleteView, PasswordResetDoneView
# from .views import PasswordReset, PasswordResetConfirm, PasswordResetDone, PasswordResetComplete, CustomLoginView,
from .views import RegisterInvestor, CustomLoginView, ConfirmEmail, GetStatesAndCC, CheckUsername, RegisterInvestor2
from .views import EmailSent, Dashboard, EditProfile, EditProfilePicture, AddDecision, DecisionView, EditDecision
from .views import SendBackupToEmail

urlpatterns = [
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
    path('register/', RegisterInvestor.as_view(), name='register-investor'),
    path('email-sent/', EmailSent.as_view(), name='email-sent'),
    path('confirm-email/<str:username>/<slug:otp>/', ConfirmEmail.as_view(), name='confirm-email'),
    path('<str:username>/complete-registration/', RegisterInvestor2.as_view(), name='register-investor-2'),
    path('login/', CustomLoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('change-password/', PasswordChangeView.as_view(success_url='/account/login'), name='password_change'),
    path('reset-password/', PasswordResetView.as_view(), name='password_reset'),
    path('reset-password-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password-done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password-complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('get_states_and_cc/', GetStatesAndCC.as_view(), name='get-states-and-cc'),
    path('check_username/', CheckUsername.as_view(), name='check-username'),
    path('edit_profile/', EditProfile.as_view(), name='edit_profile'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('send_backup_to_email/', SendBackupToEmail.as_view(), name='send_backup'),
    path('edit_profile_picture/', EditProfilePicture.as_view(), name='edit_profile_picture'),
    path('add_decision/', AddDecision.as_view(), name='add_decision'),
    path('edit_decision/', EditDecision.as_view(), name='edit_decision'),
    path('decisions/', DecisionView.as_view(), name='decisions'),

]

if settings.DEBUG:
    from .views import PopulateFlagDB
    urlpatterns = [

                    path('populate_flag_db/', PopulateFlagDB.as_view(), name='populate_flag_db'),

                    ] + urlpatterns

