from django.urls import path,include
from .  import views

urlpatterns = [
    path('log/',views.adminLogin ,name='adminlog'),
    path('home/',views.adminHome ,name='adminhome'),
    path('usermng/',views.adminUsermng ,name='usermng'),
    path('productmng/',views.adminProductmng ,name='productmng'),
    path('categorymng/',views.adminCategorymng ,name='categorymng'),
    path('addproduct/',views.adminAddProduct ,name='addproduct'),
    path('deleteproduct/<pk>', views.deleteProduct,name='deleteproduct'),
    path('undodeleteproduct/<pk>', views.undodeleteProduct,name='undodeleteproduct'),
    path('addcategory/',views.adminAddcategory ,name='addcategory'),
    path('deletecategory/<pk>', views.deleteCategory,name='deletecategory'),
    path('editproduct/<pk>', views.editProduct,name='editproduct'),
    path('editcategory/<pk>', views.editCategory,name='editcategory'),
    path('addproductimage/<pk>',views.addProductImage ,name='addproductimage'),
    path('deleteproductimage/<pk>',views.deleteProductImage ,name='deleteproductimage'),
    path('blockuser/<pk>',views.blockUser ,name='blockuser'),
    path('unblockuser/<pk>',views.unblockUser ,name='unblockuser'),
    path('adminout/',views.adminlogout ,name='adminout'),
    path('undodeletecategory/<pk>',views.undodeleteCategory ,name='undodeletecategory'),
    
]