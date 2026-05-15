import requests
from django.core.management.base import BaseCommand
from core.models import Country

# Source: https://gist.github.com/subbe/428e74e2d77ccb33e58a458a7d591207
# Has: name, iso (alpha3), iso2 (alpha2), latitude, longitude, flag URL
COUNTRIES_URL = (
    "https://gist.githubusercontent.com/subbe/"
    "428e74e2d77ccb33e58a458a7d591207/raw/"
    "countries.json"
)

# DiplomaticPulse uses UN-style full names — map them to standard names
FULL_NAME_MAP = {
    "India": "Republic of India",
    "China": "People's Republic of China",
    "Russia": "Russian Federation",
    "Iran": "Islamic Republic of Iran",
    "Syria": "Syrian Arab Republic",
    "South Korea": "Republic of Korea",
    "North Korea": "Democratic People's Republic of Korea",
    "Bolivia": "Plurinational State of Bolivia",
    "Venezuela": "Bolivarian Republic of Venezuela",
    "Tanzania": "United Republic of Tanzania",
    "Moldova": "Republic of Moldova",
    "Vietnam": "Socialist Republic of Viet Nam",
    "Laos": "Lao People's Democratic Republic",
    "Brunei": "Brunei Darussalam",
    "Cape Verde": "Republic of Cabo Verde",
    "Ivory Coast": "Republic of Côte d'Ivoire",
    "Czech Republic": "Czech Republic",
    "United States": "United States of America",
    "United Kingdom": "United Kingdom of Great Britain and Northern Ireland",
    "Palestine": "State of Palestine",
    "Micronesia": "Federated States of Micronesia",
    "Trinidad": "Republic of Trinidad and Tobago",
    "Turkey": "Republic of Türkiye",
    "Germany": "Federal Republic of Germany",
    "France": "French Republic",
    "Brazil": "Federative Republic of Brazil",
    "Pakistan": "Islamic Republic of Pakistan",
    "Bangladesh": "People's Republic of Bangladesh",
    "Saudi Arabia": "Kingdom of Saudi Arabia",
    "Japan": "Japan",
    "Australia": "Commonwealth of Australia",
    "Canada": "Canada",
    "Mexico": "United Mexican States",
    "Argentina": "Argentine Republic",
}


class Command(BaseCommand):
    help = "Populate Country model with ISO codes, lat/lng, and flag URLs"

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching country data...")

        try:
            response = requests.get(COUNTRIES_URL, timeout=15)
            response.raise_for_status()
            countries_data = response.json()
        except Exception as e:
            self.stderr.write(f"Failed to fetch data: {e}")
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for c in countries_data:
            name = c.get("name", "").strip()
            isoa3 = c.get("iso", "").strip()
            isoa2 = c.get("iso2", "").strip()
            lat = c.get("latitude")
            lng = c.get("longitude")

            if not all([name, isoa3, isoa2, lat, lng]):
                skipped_count += 1
                continue

            # Build the full_name using the map, or default to name
            full_name = FULL_NAME_MAP.get(name, name)

            try:
                obj, created = Country.objects.update_or_create(
                    isoa3_code=isoa3,
                    defaults={
                        "name": name,
                        "full_name": full_name,
                        "isoa2_code": isoa2,
                        "lat": float(lat),
                        "lng": float(lng),
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                self.stderr.write(f"Error saving {name}: {e}")
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                (
                    f"Done! Created: {created_count} | "
                    f"Updated: {updated_count} | "
                    f"Skipped: {skipped_count}"
                )
            )
        )
