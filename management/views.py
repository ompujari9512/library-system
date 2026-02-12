from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator  # <--- Added for Pagination
from .models import Book, CartItem, IssuedBook

# --- SECURITY CHECK FUNCTION ---
def is_librarian(user):
    return user.is_superuser

# --- LOGIN VIEW ---
def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'management/login.html')

# --- SIGNUP VIEW ---
def signup_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        e = request.POST.get('email')
        p1 = request.POST.get('password')
        p2 = request.POST.get('confirm_password')
        if p1 != p2:
            messages.error(request, "Passwords do not match!")
            return render(request, 'management/signup.html')
        if User.objects.filter(username=u).exists():
            messages.error(request, "Username already taken!")
            return render(request, 'management/signup.html')
        try:
            user = User.objects.create_user(username=u, email=e, password=p1)
            user.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login') 
        except Exception as e:
            messages.error(request, "An error occurred during signup.")
    return render(request, 'management/signup.html')

# --- GUEST LOGIN ---
def guest_login_view(request):
    logout(request) 
    return redirect('dashboard')

# --- DASHBOARD ---
def dashboard(request):
    # 1. Search Logic
    search_query = request.GET.get('q', '')
    if search_query:
        books = Book.objects.filter(
            Q(title__icontains=search_query) | 
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    else:
        books = Book.objects.all()
    
    # 2. Cart Logic
    cart_book_ids = []
    if request.user.is_authenticated:
        cart_book_ids = list(CartItem.objects.filter(user=request.user).values_list('book_id', flat=True))

    # 3. Stats Logic (Pending & Issued) - FIXED: Now inside the flow
    pending_count = 0
    issued_count = 0
    
    if request.user.is_authenticated:
        if request.user.is_superuser:
            # Admin sees GLOBAL stats
            pending_count = IssuedBook.objects.filter(status='Pending').count()
            issued_count = IssuedBook.objects.filter(status='Issued').count()
        else:
            # Student sees PERSONAL stats
            pending_count = IssuedBook.objects.filter(user=request.user, status='Pending').count()
            issued_count = IssuedBook.objects.filter(user=request.user, status='Issued').count()

    return render(request, 'management/dashboard.html', {
        'books': books,
        'search_query': search_query,
        'cart_book_ids': cart_book_ids, 
        'total_books': books.count(),
        'pending_count': pending_count,
        'issued_count': issued_count,
    })

# --- ALL BOOKS (With Pagination) ---
def all_books(request):
    query = request.GET.get('q')
    
    # Order by ID to ensure consistent pagination
    books_list = Book.objects.all().order_by('-id')
    
    if query:
        books_list = books_list.filter(
            Q(title__icontains=query) | 
            Q(author__icontains=query) |
            Q(isbn__icontains=query) |
            Q(category__icontains=query)
        )
    
    # PAGINATION LOGIC: Show 8 books per page
    paginator = Paginator(books_list, 8) 
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)

    return render(request, 'management/all_books.html', {
        'books': books,
        'search_query': query if query else ''
    })

# --- VIEW SINGLE BOOK ---
def view_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'management/view_book.html', {'book': book})

# --- ADD BOOK (LIBRARIAN ONLY) ---
# --- ADD BOOK (DEBUG VERSION) ---
@login_required(login_url='login')
@user_passes_test(is_librarian, login_url='dashboard')
def add_book(request):
    if request.method == 'POST':
        print("--- ATTEMPTING TO ADD BOOK ---") # DEBUG PRINT
        
        # Get data
        t = request.POST.get('title')
        a = request.POST.get('author')
        i = request.POST.get('isbn')
        q = request.POST.get('quantity')
        c = request.POST.get('category')
        bf = request.POST.get('book_format')
        f = request.FILES.get('pdf_file')
        img = request.FILES.get('cover_image')

        # Print data to terminal to check if it's empty
        print(f"Title: {t}, Author: {a}, Category: {c}, ISBN: {i}")

        try:
            # Attempt to save
            new_book = Book.objects.create(
                title=t, author=a, isbn=i, quantity=q, 
                category=c, book_format=bf, 
                pdf_file=f, cover_image=img
            )
            new_book.save()
            
            print("--- SUCCESS: BOOK SAVED ---") # DEBUG PRINT
            messages.success(request, "Book added successfully!")
            return redirect('dashboard')
            
        except Exception as e:
            # THIS IS THE IMPORTANT PART
            print(f"!!! ERROR SAVING BOOK: {e} !!!") # DEBUG PRINT
            messages.error(request, f"Error adding book: {e}")

    return render(request, 'management/add_book.html', {
        # We don't strictly need these choices context if we use the custom dropdown
        # but keeping them doesn't hurt.
    })

# --- EDIT BOOK (LIBRARIAN ONLY) ---
@login_required(login_url='login')
@user_passes_test(is_librarian, login_url='dashboard')
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.isbn = request.POST.get('isbn')
        book.quantity = request.POST.get('quantity')
        book.category = request.POST.get('category')
        book.book_format = request.POST.get('book_format')
        if request.FILES.get('pdf_file'):
            book.pdf_file = request.FILES.get('pdf_file')
        if request.FILES.get('cover_image'):
            book.cover_image = request.FILES.get('cover_image')
        book.save()
        messages.success(request, "Book updated successfully!")
        return redirect('dashboard')
    return render(request, 'management/edit_book.html', {
        'book': book,
        'categories': Book.CATEGORY_CHOICES,
        'formats': Book.FORMAT_CHOICES
    })

# --- DELETE BOOK (LIBRARIAN ONLY) ---
@login_required(login_url='login')
@user_passes_test(is_librarian, login_url='dashboard')
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    messages.success(request, "Book deleted successfully!")
    return redirect('dashboard')

# --- CART: ADD ---
def add_to_cart(request, book_id):
    if not request.user.is_authenticated:
        messages.error(request, "Please login to add books to your bag.")
        return redirect('login')
    book = get_object_or_404(Book, id=book_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, book=book)
    if created:
        messages.success(request, f"Added '{book.title}' to your bag!")
    else:
        messages.info(request, "This book is already in your bag.")
    return redirect('dashboard')

# --- CART: REMOVE ---
def remove_from_cart(request, book_id):
    if not request.user.is_authenticated:
        return redirect('login')
    book = get_object_or_404(Book, id=book_id)
    CartItem.objects.filter(user=request.user, book=book).delete()
    messages.success(request, "Removed from your bag.")
    return redirect('dashboard')

# --- VIEW CART ---
@login_required(login_url='login')
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    requested_books = IssuedBook.objects.filter(user=request.user).exclude(status='Returned').order_by('-issued_date')
    return render(request, 'management/cart.html', {
        'cart_items': cart_items,
        'requested_books': requested_books
    })

# --- CHECKOUT ---
@login_required(login_url='login')
def checkout(request):
    if request.method == 'POST':
        f_date = request.POST.get('from_date')
        t_date = request.POST.get('to_date')
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items:
            messages.error(request, "Your bag is empty!")
            return redirect('dashboard')
        for item in cart_items:
            IssuedBook.objects.create(
                user=request.user, 
                book=item.book,
                issued_date=f_date,  
                return_date=t_date,
                status='Pending'
            )
        cart_items.delete()
        messages.success(request, "Request sent to Admin! Check 'My Books' for status.")
        return redirect('my_books')
    return redirect('dashboard')

# --- ADMIN: VIEW REQUESTS ---
@login_required(login_url='login')
@user_passes_test(is_librarian, login_url='dashboard')
def view_requests(request):
    pending_requests = IssuedBook.objects.filter(status='Pending').order_by('-issued_date')
    issued_books = IssuedBook.objects.filter(status='Issued').order_by('-issued_date')
    return render(request, 'management/admin_requests.html', {
        'requests': pending_requests,
        'issued_books': issued_books
    })

# --- ADMIN: APPROVE REQUEST ---
@login_required(login_url='login')
@user_passes_test(is_librarian, login_url='dashboard')
def approve_request(request, request_id):
    issue_request = get_object_or_404(IssuedBook, id=request_id)
    book = issue_request.book
    if book.quantity > 0:
        issue_request.status = 'Issued'
        issue_request.save()
        book.quantity -= 1
        book.save()
        messages.success(request, f"Request approved! '{book.title}' is now issued.")
    else:
        messages.error(request, "Cannot approve: Book is Out of Stock.")
    return redirect('view_requests')

# --- ADMIN: REJECT / DELETE REQUEST ---
@login_required(login_url='login')
@user_passes_test(is_librarian, login_url='dashboard')
def delete_request(request, request_id):
    request_to_delete = get_object_or_404(IssuedBook, id=request_id)
    request_to_delete.delete()
    messages.success(request, "Request rejected and removed.")
    return redirect('view_requests')

# --- ADMIN: RETURN BOOK ---
@login_required(login_url='login')
@user_passes_test(is_librarian, login_url='dashboard')
def return_book(request, request_id):
    issue_request = get_object_or_404(IssuedBook, id=request_id)
    issue_request.status = 'Returned'
    issue_request.return_date = timezone.now()
    issue_request.save()
    book = issue_request.book
    book.quantity += 1
    book.save()
    messages.success(request, f"Book '{book.title}' returned successfully. Stock updated.")
    return redirect('view_requests')

# --- STUDENT: MY BOOKS ---
@login_required(login_url='login')
def my_books(request):
    my_books = IssuedBook.objects.filter(user=request.user).order_by('-issued_date')
    return render(request, 'management/my_books.html', {'my_books': my_books})


# --- STUDENT: RETURN BOOK ---
@login_required(login_url='login')
def student_return_book(request, record_id):
    if request.method == 'POST':
        record = get_object_or_404(IssuedBook, id=record_id, user=request.user)
        if record.status == 'Issued':
            record.status = 'Returned'
            record.return_date = timezone.now()
            record.save()
            
            book = record.book
            book.quantity += 1
            book.save()
            
            messages.success(request, f"Successfully returned '{book.title}'!")
        else:
            messages.warning(request, "This book is not currently issued to you.")
            
    return redirect('my_books')


# --- PROFILE VIEW ---
@login_required(login_url='login')
def profile(request):
    return render(request, 'management/profile.html', {
        'user': request.user
    })

# --- MEMBERS PAGE ---
@login_required(login_url='login')
def members_list(request):
    members = User.objects.all().order_by('-date_joined')
    return render(request, 'management/members.html', {
        'members': members
    })

# --- DELETE MEMBER (Admin Only) ---
@login_required(login_url='login')
def delete_member(request, user_id):
    if request.user.is_superuser:
        user_to_delete = get_object_or_404(User, id=user_id)
        if user_to_delete != request.user: 
            user_to_delete.delete()
            messages.success(request, "Member removed successfully.")
        else:
            messages.error(request, "You cannot delete your own account here.")
    return redirect('members_list')