# # middleware.py

# from django.shortcuts import redirect
# from django.urls import reverse

# class PreventBackToLoginMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if request.user.is_authenticated and request.path == reverse('userlog'):
#             return redirect('index')  # Redirect to the home page
        
#         response = self.get_response(request)
#         return response
