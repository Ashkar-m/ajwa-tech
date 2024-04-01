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
    path('ordermng/',views.adminOrdermng ,name='ordermng'),
    path('editorder/<pk>', views.editOrder,name='editorder'),
    path('cancelorder/<pk>',views.cancelOrder,name='cancelorder'),

    path('productoffers/',views.ProductOffers,name='productoffers'),
    path('addproductoffer/',views.addProductOffer,name='addproductoffer'),
    path('editproductoffer/<pk>', views.editProductOffer,name='editproductoffer'),
    path('unlistproductoffer/<pk>',views.unlistProductOffer,name='unlistproductoffer'),
    path('listproductoffer/<pk>',views.listProductOffer,name='listproductoffer'),
    path('categoryoffers/',views.categoryOffers,name='categoryoffers'),
    path('addcategoryoffer/',views.addCategoryOffer,name='addcategoryoffer'),
    path('editcategoryoffer/<pk>', views.editCategoryOffer,name='editcategoryoffer'),
    path('unlistcategoryoffer/<pk>',views.unlistCategoryOffer,name='unlistcategoryoffer'),
    path('listcategoryoffer/<pk>',views.listCategoryOffer,name='listcategoryoffer'),

    path('couponlist/',views.couponList,name='couponlist'),
    path('addcoupon/',views.addCoupon,name='addcoupon'),
    path('editcoupon/<pk>', views.editCoupon,name='editcoupon'),
    path('deletecoupon/<pk>',views.deleteCoupon,name='deletecoupon'),
    path('retaincoupon/<pk>',views.retainCoupon,name='retaincoupon'),


    path('adminindex/',views.adminIndex,name='adminindex'),
    # path('dailyreport/',views.dailyReport,name='dailyreport'),
    
]