from django.urls import path

from first_app import views

from first_app.views import AllFlowerView

from first_app.views import BoHoaTuoiView, ChauHoaView, HoaSapView, HoaChiaBuonView, \
    HoaChucMungView, HoaCuoiView, HoaSinhNhatView, HoaTinhYeuView

app_name = "dropdown"

urlpatterns = [
    path ('all_flower/',AllFlowerView.as_view(), name='all_flower'),
    path ('bo_hoa_tuoi/',BoHoaTuoiView.as_view(), name='bo_hoa_tuoi'),
    path ('chau_hoa/',ChauHoaView.as_view(), name='chau_hoa'),
    path ('hoa_sap/', HoaSapView.as_view(), name='hoa_sap'),

    path('hoa_chia_buon/', HoaChiaBuonView.as_view(), name='hoa_chia_buon'),
    path('hoa_chuc_mung/',HoaChucMungView.as_view(), name='hoa_chuc_mung'),
    path('hoa_cuoi/', HoaCuoiView.as_view(), name='hoa_cuoi'),
    path('hoa_sinh_nhat/',HoaSinhNhatView.as_view(), name='hoa_sinh_nhat'),
    path('hoa_tinh_yeu/', HoaTinhYeuView.as_view(), name='hoa_tinh_yeu'),
]