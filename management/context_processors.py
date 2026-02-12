from .models import Book, CartItem, IssuedBook

def library_stats(request):
    """
    Returns global stats for the sidebar and navbar (Total Books, Cart, Pending Requests).
    """
    stats = {
        'total_books': Book.objects.count(),  # Always count total books
        'cart_count': 0,                      # Default 0
        'pending_count': 0,                   # Default 0
    }

    if request.user.is_authenticated:
        # 1. Get Cart Count for the logged-in user
        stats['cart_count'] = CartItem.objects.filter(user=request.user).count()

        # 2. Get Pending Requests Count (Smart Logic)
        if request.user.is_superuser:
            # Admin sees ALL pending requests from everyone
            stats['pending_count'] = IssuedBook.objects.filter(status='Pending').count()
        else:
            # Students see only THEIR OWN pending requests
            stats['pending_count'] = IssuedBook.objects.filter(user=request.user, status='Pending').count()

    return stats