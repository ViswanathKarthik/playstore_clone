# Full views.py content as generated earlier (omitted here to save space)
# In the zip, it will include the complete code provided above for views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F
from django.http import JsonResponse
from .models import App, AppReview, StagingReview
from .forms import SignupForm, LoginForm, ReviewForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import connection
from .models import App
from django.shortcuts import render
from django.utils import timezone

# Home / login redirect
@login_required(login_url='/login/')
def home(request):
    # Get top 10 apps ordered by rating descending, then reviews_int descending
    top_apps = App.objects.exclude(rating__isnull=True).order_by('-rating', '-reviews_int')[:10]

    return render(request, 'apps/home.html', {'top_apps': top_apps})

def delete_review(request, review_id):
    if request.method == "POST" and request.user.is_staff:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM staging_reviews WHERE id = %s", [review_id])
        messages.success(request, "Review deleted successfully.")
    return redirect('admin_dashboard')


# Signup
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('login_view')
    else:
        form = SignupForm()
    return render(request, 'apps/signup.html', {'form': form})

# Login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data['username']
            pwd = form.cleaned_data['password']
            user = authenticate(username=uname, password=pwd)
            if user:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'apps/login.html', {'form': form})

# Logout
def logout_view(request):
    logout(request)
    return redirect('login_view')

def search_results(request):
    query = request.GET.get('query', '')
    results = []

    if query and len(query) >= 2:  # minimum 2 chars
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, app, rating, reviews_int
                FROM apps
                WHERE app ILIKE %s
                ORDER BY rating DESC, reviews_int DESC
                LIMIT 10
            """, [f"%{query}%"])
            results = cursor.fetchall()

    return render(request, 'apps/search_results.html', {'results': results, 'query': query})



# Search suggestions (AJAX)
@login_required
def search_suggestions(request):
    query = request.GET.get('query', '').strip()
    suggestions = []

    if query:
        prefix = f"{query}%"  # prefix filter for speed
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT app
                FROM apps
                WHERE app ILIKE %s
                ORDER BY similarity(app, %s) DESC, COALESCE(rating,0) DESC, COALESCE(reviews_int,0) DESC
                LIMIT 5
            """, [prefix, query])
            suggestions = [row[0] for row in cursor.fetchall()]

    return JsonResponse({'suggestions': suggestions})

# Search results
@login_required
def app_list(request):
    q = request.GET.get('q', '')
    apps = App.objects.all()
    if q:
        apps = apps.filter(app__icontains=q).order_by('-rating', '-reviews_int')
    return render(request, 'apps/app_list.html', {'apps': apps, 'query': q})

# App details with first 5 reviews
@login_required(login_url='/login/')
def app_detail(request, app_id):
    app = get_object_or_404(App, pk=app_id)

    # User review (approved or under review)
    user_review = AppReview.objects.filter(app=app, approved_by=request.user.username).first()
    under_review = False
    if not user_review:
        user_review = StagingReview.objects.filter(app=app, submitted_by=request.user.username).first()
        if user_review:
            under_review = True

    # Top 5 approved reviews excluding user
    reviews = AppReview.objects.filter(app=app).exclude(approved_by=request.user.username).order_by("-created_at")
    top_reviews = reviews[:5]
    other_reviews = reviews[5:]

    # Prepare stars for reviews
    def generate_stars(rating):
        if rating is None:
            return "☆" * 5
        rating = int(round(rating))
        return "★" * rating + "☆" * (5 - rating)

    # User stars
    user_stars = generate_stars(user_review.rating) if user_review else ""

    # Average stars
    avg_rating = round(app.rating, 1) if app.rating else 0
    avg_stars = generate_stars(avg_rating)

    # Add stars to all reviews
    for review in top_reviews:
        review.stars = generate_stars(review.rating)
    for review in other_reviews:
        review.stars = generate_stars(review.rating)

    # Combine top + other reviews for modal
    all_reviews = list(top_reviews) + list(other_reviews)

    return render(request, "apps/app_detail.html", {
        "app": app,
        "user_review": user_review,
        "under_review": under_review,
        "top_reviews": top_reviews,
        "other_reviews": other_reviews,
        "all_reviews": all_reviews,
        "avg_rating": avg_rating,
        "avg_stars": avg_stars,
        "user_stars": user_stars
    })





# See all reviews
@login_required
def all_reviews(request, app_id):
    app = get_object_or_404(App, pk=app_id)
    reviews = AppReview.objects.filter(app=app).order_by('-created_at')
    return render(request, 'apps/all_reviews.html', {'app': app, 'reviews': reviews})

# Submit review
@login_required
def submit_review(request, app_id):
    app = get_object_or_404(App, pk=app_id)

    # 1️⃣ Try to get user's approved review
    user_review = AppReview.objects.filter(app=app, approved_by=request.user.username).first()
    is_approved = True if user_review else False

    # 2️⃣ If not approved, check staging review
    if not user_review:
        user_review = StagingReview.objects.filter(app=app, submitted_by=request.user.username).first()
        is_approved = False

    # 3️⃣ Handle POST
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=user_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.app = app
            if is_approved:
                # Update existing approved review
                review.approved_by = request.user.username
                review.approved_at = timezone.now()
                review.save()
                messages.success(request, "Your approved review has been updated!")
            else:
                # Update or create staging review
                review.submitted_by = request.user.username
                review.save()
                messages.success(request, "Your review has been submitted and is pending approval.")
            return redirect('app_detail', app_id=app.id)
    else:
        form = ReviewForm(instance=user_review)

    return render(request, 'apps/submit_review.html', {
        'app': app,
        'form': form,
        'user_review': user_review,
        'is_approved': is_approved
    })


# Admin dashboard
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    pending_reviews = StagingReview.objects.all().order_by('-submitted_at')
    return render(request, 'apps/admin_dashboard.html', {'pending_reviews': pending_reviews})

# Approve review
@user_passes_test(lambda u: u.is_staff)
def approve_review(request, review_id):
    # Get the staging review
    review = get_object_or_404(StagingReview, pk=review_id)

    if review.rating is None:
        messages.error(request, f"Cannot approve review by {review.submitted_by}: rating is missing.")
        return redirect("admin_dashboard")

    # Create the approved review, keeping original submitter
    approved_review = AppReview.objects.create(
        app=review.app,
        translated_review=review.translated_review,
        rating=review.rating,
        approved_by=review.submitted_by,  # original user
        approved_at=timezone.now(),
    )

    # Update app rating and num_reviews
    app = review.app
    if app.reviews_int is None:
        app.reviews_int = 0
    app.reviews_int += 1

    current_rating = app.rating if app.rating is not None else 0
    app.rating = round((current_rating * (app.reviews_int - 1) + review.rating) / app.reviews_int, 1)
    app.save()

    # Delete the staging review
    review.delete()

    messages.success(request, f"Review by {approved_review.approved_by} approved successfully!")
    return redirect("admin_dashboard")
