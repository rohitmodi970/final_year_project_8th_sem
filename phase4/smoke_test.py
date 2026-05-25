import json
import requests


def main() -> None:
    base_url = "http://127.0.0.1:5001"

    health = requests.get(f"{base_url}/health", timeout=30)
    print("/health", health.status_code, health.json())

    route_payload = {
        "origin": 290731701,
        "destination": 13851397444,
    }
    route = requests.post(f"{base_url}/route/compare", json=route_payload, timeout=60)
    print("/route/compare", route.status_code)
    print(json.dumps(route.json(), indent=2))

    emission_payload = {
        "vehicle_type": "Car",
        "fuel_type": "Petrol",
        "road_type": "City",
        "traffic_conditions": "Moderate",
        "engine_size": 1.5,
        "age_of_vehicle": 5,
        "mileage": 50000,
    }
    emission = requests.post(
        f"{base_url}/emissions/predict",
        json=emission_payload,
        timeout=30,
    )
    print("/emissions/predict", emission.status_code, emission.json())


if __name__ == "__main__":
    main()
