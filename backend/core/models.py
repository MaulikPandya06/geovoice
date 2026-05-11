from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    isoa3_code = models.CharField(max_length=5, unique=True)
    isoa2_code = models.CharField(max_length=5, null=True, blank=True)
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class Statement(models.Model):
    STANCE_CHOICES = [
        ('support', 'Support'),
        ('neutral', 'Neutral'),
        ('oppose', 'Oppose'),
    ]

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    text = models.TextField()
    stance = models.CharField(max_length=10, choices=STANCE_CHOICES)
    source_url = models.URLField(null=True, blank=True)
    publish_date = models.DateField()

    def __str__(self):
        return f"{self.country.name} - {self.event.title}"
