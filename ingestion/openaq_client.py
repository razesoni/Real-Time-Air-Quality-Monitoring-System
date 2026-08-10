import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

class OpenAQClient:

    def __init__(self):
        self.api_key = os.getenv("OPENAQ_API_KEY")
        self.base_url = "https://api.openaq.org/v3"
        self.headers = {"X-API-Key": self.api_key} if self.api_key else {}

    def _get(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from OpenAQ API: {e}")
            return {}

    def get_location_details(self, location_id: int) -> dict:
        data = self._get(f"locations/{location_id}")
        results = data.get("results", {})
        if isinstance(results, list):
            return results[0] if results else {}
        elif isinstance(results, dict):
            return results
        return {}

    def get_latest_measurements(self, location_id: int) -> list:
        location_data = self.get_location_details(location_id)
        if not isinstance(location_data, dict) or not location_data:
            return []

        sensors = location_data.get("sensors", [])
        sensor_map = {s.get("id"): s.get("parameter", {}) for s in sensors if isinstance(s, dict)}
        city = location_data.get("locality") or location_data.get("name") or "Unknown"

        latest_data = self._get(f"locations/{location_id}/latest")
        latest_results = latest_data.get("results", [])

        measurements = []
        if isinstance(latest_results, list) and latest_results:
            for item in latest_results:
                sensor_id = item.get("sensorsId")
                param = sensor_map.get(sensor_id, {})
                datetime_info = item.get("datetime", {})
                last_updated = datetime_info.get("utc") if isinstance(datetime_info, dict) else None
                measurements.append({
                    "location_id": location_id,
                    "city": city,
                    "parameter": param.get("name"),
                    "unit": param.get("units"),
                    "value": item.get("value"),
                    "last_updated": last_updated,
                })
        else:
            for sensor in sensors:
                if not isinstance(sensor, dict):
                    continue
                param = sensor.get("parameter", {})
                datetime_last = sensor.get("datetimeLast")
                last_updated = datetime_last.get("utc") if isinstance(datetime_last, dict) else None
                measurements.append({
                    "location_id": location_id,
                    "city": city,
                    "parameter": param.get("name"),
                    "unit": param.get("units"),
                    "value": sensor.get("value"),
                    "last_updated": last_updated,
                })

        return measurements

    def search_locations(self, city: str = None, country: str = "IN") -> list:
        params = {"country": country}
        if city:
            params["city"] = city
                
        data = self._get("locations", params=params)
        results = data.get("results", [])
        return results if isinstance(results, list) else []

if __name__ == "__main__":
    client = OpenAQClient()
    sample_location_id = 8118  
    print(f"Fetching details for location {sample_location_id}...")
    latest = client.get_latest_measurements(sample_location_id)
    print("Latest Measurements:", latest)