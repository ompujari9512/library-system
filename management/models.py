from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
    

from django.db import models

class Book(models.Model):
    # --- DROPDOWN OPTIONS ---
    CATEGORY_CHOICES = [
        ('Fiction', (
            ('fantasy', 'Fantasy'),
            ('scifi', 'Science Fiction'),
            ('mystery', 'Mystery / Detective'),
            ('thriller', 'Thriller / Suspense'),
            ('romance', 'Romance'),
            ('horror', 'Horror'),
            ('historical', 'Historical Fiction'),
            ('adventure', 'Adventure'),
            ('ya', 'Young Adult (YA)'),
            ('short_story', 'Short Stories'),
        )),
        ('Non-Fiction', (
            ('biography', 'Biography / Autobiography'),
            ('self_help', 'Self-Help'),
            ('history', 'History'),
            ('science', 'Science & Technology'),
            ('philosophy', 'Philosophy'),
            ('psychology', 'Psychology'),
            ('business', 'Business & Economics'),
            ('travel', 'Travel'),
            ('health', 'Health & Fitness'),
            ('essays', 'Essays'),
        )),
        ('Academic', (
            ('textbook', 'Textbooks'),
            ('reference', 'Reference Books'),
            ('research', 'Research Papers'),
            ('journal', 'Journals'),
            ('exam', 'Exam Preparation'),
        )),
        ('Children', (
            ('picture', 'Picture Books'),
            ('early', 'Early Readers'),
            ('fairy', 'Fairy Tales'),
            ('comic', 'Comics & Graphic Novels'),
        )),
        ('Style', (
            ('novel', 'Novels'),
            ('novella', 'Novellas'),
            ('poetry', 'Poetry'),
            ('drama', 'Drama / Plays'),
        )),
    ]

    FORMAT_CHOICES = [
        ('hardcover', 'Hardcover'),
        ('paperback', 'Paperback'),
        ('ebook', 'E-book'),
        ('audiobook', 'Audiobook'),
    ]

    # --- DATABASE FIELDS ---
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    quantity = models.IntegerField(default=5)
    
    # New Fields with Default values to prevent errors
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='novel')
    book_format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='paperback')
    
    pdf_file = models.FileField(upload_to='books/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)

    def __str__(self):
        return self.title
    

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
    

from datetime import timedelta
from django.utils import timezone

# ... existing models ...

class IssuedBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issued_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(blank=True, null=True) # Will be set automatically

    status_choices = [
        ('Pending', 'Pending'),
        ('Issued', 'Issued'),
        ('Returned', 'Returned')
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='Issued')
    
    def save(self, *args, **kwargs):
        # Automatically set return date to 15 days from now if not set
        if not self.return_date:
            self.return_date = timezone.now() + timedelta(days=15)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} issued to {self.user.username}"
    

