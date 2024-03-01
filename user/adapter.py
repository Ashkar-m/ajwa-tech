# # allauth_adapter.py

# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from django.shortcuts import redirect

# class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
#     def pre_social_login(self, request, sociallogin):
#         # Check if the user is already logged in
#         if request.user.is_authenticated:
#             return redirect('index')  # Redirect to home page if the user is already logged in
