from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

import joblib
import pandas as pd

DEFAULTS: Dict[str, Any] = {
    "vehicle_type": "Car",
    "fuel_type": "Petrol",
    "road_type": "City",
    "traffic_conditions": "Moderate",
    "engine_size": 1.5,
    "age_of_vehicle": 5,
    "mileage": 50000,
    "speed": 60.0,
    "acceleration": 2.0,
    "temperature": 25.0,
    "humidity": 50.0,
    "wind_speed": 10.0,
    "air_pressure": 1013.0,
    "cylinders": 4,
    "fuel_cons_comb": 8.5,
    "fuel_cons_comb_mpg": 33,
}

POLLUTANT_RATIOS: Dict[str, float] = {
    "nox": 0.002,
    "voc": 0.001,
    "so2": 0.0005,
}


@dataclass
class EmissionRequest:
    vehicle_type: Optional[str] = None
    fuel_type: Optional[str] = None
    road_type: Optional[str] = None
    traffic_conditions: Optional[str] = None
    engine_size: Optional[float] = None
    age_of_vehicle: Optional[int] = None
    mileage: Optional[int] = None
    speed: Optional[float] = None
    acceleration: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    air_pressure: Optional[float] = None
    cylinders: Optional[int] = None
    fuel_cons_comb: Optional[float] = None
    fuel_cons_comb_mpg: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmissionRequest":
        return cls(
            vehicle_type=data.get("vehicle_type") or data.get("Vehicle Type"),
            fuel_type=data.get("fuel_type") or data.get("Fuel Type"),
            road_type=data.get("road_type") or data.get("Road Type"),
            traffic_conditions=data.get("traffic_conditions") or data.get("Traffic Conditions"),
            engine_size=_to_float(data.get("engine_size")),
            age_of_vehicle=_to_int(data.get("age_of_vehicle") or data.get("Age of Vehicle")),
            mileage=_to_int(data.get("mileage") or data.get("Mileage")),
            speed=_to_float(data.get("speed") or data.get("Speed")),
            acceleration=_to_float(data.get("acceleration") or data.get("Acceleration")),
            temperature=_to_float(data.get("temperature") or data.get("Temperature")),
            humidity=_to_float(data.get("humidity") or data.get("Humidity")),
            wind_speed=_to_float(data.get("wind_speed") or data.get("Wind Speed")),
            air_pressure=_to_float(data.get("air_pressure") or data.get("Air Pressure")),
            cylinders=_to_int(data.get("cylinders")),
            fuel_cons_comb=_to_float(data.get("fuel_cons_comb")),
            fuel_cons_comb_mpg=_to_int(data.get("fuel_cons_comb_mpg")),
        )


@dataclass
class EmissionResult:
    co2_g_per_km: float
    nox_g_per_km: float
    voc_g_per_km: float
    so2_g_per_km: float
    model_used: str
    notes: str


class EmissionPredictor:
    def __init__(self, model_dir: Optional[Union[str, Path]] = None) -> None:
        self.model_dir = self._resolve_model_dir(model_dir)
        self.model_synthetic = joblib.load(self.model_dir / "model.pkl")
        self.model_canadian = joblib.load(self.model_dir / "car_model.pkl")

    def predict_from_dict(self, data: Dict[str, Any]) -> EmissionResult:
        return self.predict(EmissionRequest.from_dict(data))

    def predict(self, req: EmissionRequest) -> EmissionResult:
        has_canadian_inputs = (
            req.cylinders is not None
            and req.fuel_cons_comb is not None
            and req.fuel_cons_comb_mpg is not None
        )

        if has_canadian_inputs:
            input_df = pd.DataFrame(
                [
                    {
                        "engine_size": _value_or_default(req.engine_size, 2.0),
                        "cylinders": int(_value_or_default(req.cylinders, 4)),
                        "fuel_cons_comb": _value_or_default(req.fuel_cons_comb, 8.5),
                        "fuel_cons_comb_mpg": int(_value_or_default(req.fuel_cons_comb_mpg, 33)),
                    }
                ]
            )
            prediction = float(self.model_canadian.predict(input_df)[0])
            model_used = "canadian_fuel_efficiency_lasso"
            notes = "Used Canadian fuel-efficiency model. Input fields were complete."
        else:
            input_df = pd.DataFrame(
                [
                    {
                        "Vehicle Type": _value_or_default(req.vehicle_type, DEFAULTS["vehicle_type"]),
                        "Fuel Type": _value_or_default(req.fuel_type, DEFAULTS["fuel_type"]),
                        "Road Type": _value_or_default(req.road_type, DEFAULTS["road_type"]),
                        "Traffic Conditions": _value_or_default(
                            req.traffic_conditions, DEFAULTS["traffic_conditions"]
                        ),
                        "Engine Size": _value_or_default(req.engine_size, DEFAULTS["engine_size"]),
                        "Age of Vehicle": int(
                            _value_or_default(req.age_of_vehicle, DEFAULTS["age_of_vehicle"])
                        ),
                        "Mileage": int(_value_or_default(req.mileage, DEFAULTS["mileage"])),
                        "Speed": _value_or_default(req.speed, DEFAULTS["speed"]),
                        "Acceleration": _value_or_default(req.acceleration, DEFAULTS["acceleration"]),
                        "Temperature": _value_or_default(req.temperature, DEFAULTS["temperature"]),
                        "Humidity": _value_or_default(req.humidity, DEFAULTS["humidity"]),
                        "Wind Speed": _value_or_default(req.wind_speed, DEFAULTS["wind_speed"]),
                        "Air Pressure": _value_or_default(req.air_pressure, DEFAULTS["air_pressure"]),
                    }
                ]
            )
            prediction = float(self.model_synthetic.predict(input_df)[0])
            model_used = "synthetic_feature_model"
            notes = "Used synthetic model with fallback defaults for missing fields."

        pollutants = _derive_pollutants(prediction)

        return EmissionResult(
            co2_g_per_km=prediction,
            nox_g_per_km=pollutants["nox"],
            voc_g_per_km=pollutants["voc"],
            so2_g_per_km=pollutants["so2"],
            model_used=model_used,
            notes=notes,
        )

    def _resolve_model_dir(self, model_dir: Optional[Union[str, Path]]) -> Path:
        if model_dir is not None:
            return Path(model_dir)

        project_root = Path(__file__).resolve().parents[1]
        return project_root / "model_for_emissions" / "model_for_emissions"


def _derive_pollutants(co2_g_per_km: float) -> Dict[str, float]:
    return {
        "nox": co2_g_per_km * POLLUTANT_RATIOS["nox"],
        "voc": co2_g_per_km * POLLUTANT_RATIOS["voc"],
        "so2": co2_g_per_km * POLLUTANT_RATIOS["so2"],
    }


def _value_or_default(value: Optional[Any], default: Any) -> Any:
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return default
    return value


def _to_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None
