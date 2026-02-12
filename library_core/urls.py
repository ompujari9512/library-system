from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from management import views
from django.contrib.auth.views import LogoutView

from management.views import (
    login_view, signup_view, dashboard, guest_login_view, 
    all_books, view_book, add_book, edit_book, delete_book,
    add_to_cart, remove_from_cart, view_cart, checkout,
    view_requests, approve_request, delete_request, return_book,
    my_books
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth
    path('', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('guest/', guest_login_view, name='guest_login'),
    
    # Main
    path('dashboard/', dashboard, name='dashboard'),
    path('all-books/', all_books, name='all_books'),
    path('book/<int:book_id>/', view_book, name='view_book'),
    
    # Librarian Actions
    path('add-book/', add_book, name='add_book'),
    path('edit-book/<int:book_id>/', edit_book, name='edit_book'),
    path('delete-book/<int:book_id>/', delete_book, name='delete_book'),
    
    # Cart & Checkout
    path('add-to-cart/<int:book_id>/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:book_id>/', remove_from_cart, name='remove_from_cart'),
    path('my-bag/', view_cart, name='view_cart'),
    path('checkout/', checkout, name='checkout'),
    
    # Requests & Admin
    path('admin-requests/', view_requests, name='view_requests'),
    path('approve-request/<int:request_id>/', views.approve_request, name='approve_request'),
    path('delete-request/<int:request_id>/', views.delete_request, name='delete_request'),
    path('return-book/<int:request_id>/', views.return_book, name='return_book'),
    path('my-books/return/<int:record_id>/', views.student_return_book, name='student_return_book'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.guest_login_view, name='logout'),

    # Student Section
    path('my-books/', my_books, name='my_books'),

    #Members
    path('members/', views.members_list, name='members_list'),
    path('members/delete/<int:user_id>/', views.delete_member, name='delete_member'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



