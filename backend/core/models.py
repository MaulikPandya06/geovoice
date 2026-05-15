from django.db import models
from pgvector.django import VectorField, HnswIndex


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    isoa3_code = models.CharField(max_length=5, unique=True)
    isoa2_code = models.CharField(max_length=5, unique=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class RawPost(models.Model):
    PLATFORM_CHOICES = [
        ("twitter", "Twitter/X"),
        ("web", "Web Scrape"),
        ("pdf", "PDF Document"),
        ("javascript", "JS Page"),
    ]

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)

    # Twitter fields
    account_handle = models.CharField(max_length=255, blank=True)
    post_id = models.CharField(max_length=255, unique=True)
    post_text = models.TextField(blank=True)
    image_text = models.TextField(blank=True)
    combined_text = models.TextField(blank=True)
    media_urls = models.JSONField(default=list)
    image_urls = models.JSONField(default=list)
    ocr_processed = models.BooleanField(default=False)

    # Web scrape fields
    title = models.TextField(blank=True)
    source_url = models.URLField(max_length=500, null=True, blank=True)
    language = models.CharField(max_length=50, blank=True)
    content_type = models.CharField(max_length=50, blank=True)

    posted_at = models.DateTimeField()
    post_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # AI processing flags
    classify_ai_processed = models.BooleanField(default=False)


class Statement(models.Model):
    STANCE_CHOICES = [
        ('support', 'Support'),
        ('neutral', 'Neutral'),
        ('oppose', 'Oppose'),
    ]

    raw_post = models.OneToOneField(
        RawPost, on_delete=models.CASCADE, null=True, blank=True
    )
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    text = models.TextField()
    stance = models.CharField(max_length=10, choices=STANCE_CHOICES)
    confidence_score = models.FloatField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    topics = models.JSONField(default=list)
    source_url = models.URLField(null=True, blank=True)
    publish_date = models.DateField()

    def __str__(self):
        return f"{self.country.name} - {self.event.title}"


class StatementChunk(models.Model):
    statement = models.ForeignKey(
        Statement, on_delete=models.CASCADE, related_name='chunks'
    )
    chunk_index = models.IntegerField()       # position: 0, 1, 2...
    chunk_text = models.TextField()          # the actual chunk content
    embedding = VectorField(dimensions=1024, null=True, blank=True)
    # NVIDIA NIM models output 1024-dimensional vectors

    class Meta:
        ordering = ['chunk_index']
        indexes = [
            HnswIndex(
                name='chunk_embedding_hnsw_idx',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops']
            )
        ]

    def __str__(self):
        return f"Statement {self.statement_id} | Chunk {self.chunk_index}"


class CountryEventSummary(models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )

    summary = models.TextField(null=True, blank=True)

    statement_count = models.IntegerField(default=0)

    mwhen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('country', 'event')

    def __str__(self):
        return f"{self.country.name} - {self.event.title}"
