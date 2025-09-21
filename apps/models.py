from django.db import models
from django.contrib.auth.models import User

class App(models.Model):
    app = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    rating = models.FloatField()
    reviews = models.CharField(max_length=100)
    reviews_int = models.BigIntegerField(default=0)
    size = models.CharField(max_length=50)
    installs = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    price = models.CharField(max_length=50)
    content_rating = models.CharField(max_length=100)
    genres = models.CharField(max_length=255)
    last_updated = models.CharField(max_length=100)
    current_ver = models.CharField(max_length=100)
    android_ver = models.CharField(max_length=100)

    class Meta:
        db_table = 'apps'  # <-- your existing table name in Postgres

class AppReview(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, db_column='app_id')
    translated_review = models.TextField()
    sentiment = models.CharField(max_length=50)
    sentiment_polarity = models.FloatField()
    sentiment_subjectivity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.CharField(max_length=100)
    rating = models.FloatField()



    class Meta:
        db_table = 'app_reviews'  # <-- existing table name

class StagingReview(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, db_column='app_id')
    translated_review = models.TextField()
    rating = models.IntegerField(null=True, blank=True)  # add this

    sentiment = models.CharField(max_length=50, null=True, blank=True)
    sentiment_polarity = models.FloatField(null=True, blank=True)
    sentiment_subjectivity = models.FloatField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    submitted_by = models.CharField(max_length=100)

    class Meta:
        db_table = 'staging_reviews'  # <-- existing table name
