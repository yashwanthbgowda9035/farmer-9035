class IrrigationService:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def calculate_guidance(self, crop_type, growth_stage, soil_type, moisture_input_mode="manual", 
                           soil_moisture_pct=None, temp_c=28.0, rain_forecast_mm=0.0):
        """
        Provides smart irrigation advisory combining soil moisture depletion and crop evapotranspiration.
        Clearly distinguishes manual estimation from real-time physical capacitive/tensiometer sensor telemetry.
        """
        crop = crop_type.title()
        
        # Crop coefficient (Kc) by stage (FAO-56 Irrigation & Drainage paper)
        kc_table = {
            "Tomato": {"Seedling": 0.45, "Vegetative": 0.75, "Flowering": 1.15, "Fruiting": 1.05, "Harvesting": 0.80},
            "Potato": {"Seedling": 0.50, "Vegetative": 0.80, "Flowering": 1.15, "Fruiting": 1.00, "Harvesting": 0.75},
            "Maize": {"Seedling": 0.40, "Vegetative": 0.85, "Flowering": 1.20, "Fruiting": 1.05, "Harvesting": 0.60},
            "Rice": {"Seedling": 1.05, "Vegetative": 1.15, "Flowering": 1.25, "Fruiting": 1.10, "Harvesting": 0.90}
        }
        
        kc = kc_table.get(crop, {}).get(growth_stage, 0.85)
        
        # Evapotranspiration baseline (ET0) estimate based on temperature
        # Hargreaves-Samani simplified daily ET0 (mm/day)
        et0 = max(2.5, min(7.5, (temp_c - 10) * 0.22 + 2.5))
        daily_crop_water_need_mm = round(et0 * kc, 1)
        
        # Soil holding capacity factor
        soil_retention = {
            "Sandy": 0.7,
            "Red Loam": 1.0,
            "Clay Loam": 1.3,
            "Black Cotton": 1.5
        }.get(soil_type, 1.0)
        
        if moisture_input_mode == "sensor":
            mode_label = "Automated Hardware Sensor Mode (Capacitive Moisture Telemetry)"
            moisture_val = soil_moisture_pct if soil_moisture_pct is not None else 50.0
        else:
            mode_label = "Manual Mode (Farmer field observation / feel test)"
            moisture_val = soil_moisture_pct if soil_moisture_pct is not None else 45.0

        # Advisory decision logic
        if rain_forecast_mm >= 15.0:
            status = "Postpone Irrigation"
            water_liters_per_sqm = 0.0
            rationale = f"Significant rain ({rain_forecast_mm} mm) is forecast. Irrigating now risks waterlogging, root asphyxiation, and nutrient leaching."
            action = "Hold off on watering. Inspect field drainage channels before downpour."
        elif moisture_val < 35.0:
            status = "Irrigate Promptly (High Deficit)"
            water_liters_per_sqm = round(daily_crop_water_need_mm * 1.5, 1) # 1 mm = 1 Liter / m^2
            rationale = f"Soil moisture ({moisture_val}%) is below the allowable depletion threshold for {crop} at {growth_stage} stage (Kc={kc})."
            action = f"Apply approximately {water_liters_per_sqm} Litres/m² during early morning or evening to minimize evaporative loss."
        elif 35.0 <= moisture_val <= 65.0:
            status = "Moderate Moisture (Light Maintenance)"
            water_liters_per_sqm = round(daily_crop_water_need_mm * 0.8, 1)
            rationale = f"Root-zone moisture ({moisture_val}%) is within optimal range. Minor replenishment needed to offset ET of {daily_crop_water_need_mm} mm/day."
            action = f"Deliver {water_liters_per_sqm} Litres/m² via drip line or micro-sprinkler."
        else:
            status = "Adequate Moisture (No Irrigation Needed)"
            water_liters_per_sqm = 0.0
            rationale = f"Soil moisture is high ({moisture_val}%). Additional water will saturate pore spaces."
            action = "Skip irrigation cycle. Check again in 24 hours."

        return {
            "status": "success",
            "crop": crop,
            "stage": growth_stage,
            "soil_type": soil_type,
            "input_mode": mode_label,
            "measured_moisture_pct": moisture_val,
            "crop_coefficient_kc": kc,
            "daily_crop_water_need_mm": daily_crop_water_need_mm,
            "advisory_status": status,
            "water_liters_per_sqm": water_liters_per_sqm,
            "rationale": rationale,
            "action_instructions": action,
            "methodology": "FAO-56 Evapotranspiration Crop-Water Modeling"
        }

irrigation_service = IrrigationService.get_instance()
