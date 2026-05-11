# core/serializers.py

from rest_framework import serializers
from .models import Country, Event, Statement


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    total_statements = serializers.IntegerField(read_only=True)
    countries_involved = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_countries_involved(self, obj):
        return obj.statement_set.values('country').distinct().count()


class StatementSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(
        source='country.name',
        read_only=True
    )

    full_name = serializers.CharField(
        source='country.full_name',
        read_only=True
    )

    country_isoa2 = serializers.CharField(
        source='country.isoa2_code',
        read_only=True
    )

    country_isoa3 = serializers.CharField(
        source='country.isoa3_code',
        read_only=True
    )

    country_flag = serializers.CharField(
        source='country.flag_url',
        read_only=True
    )

    class Meta:
        model = Statement
        fields = '__all__'
