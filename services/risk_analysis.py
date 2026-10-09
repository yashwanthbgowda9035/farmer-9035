class WeatherRiskAnalysisService:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def evaluate_risk(self, crop_type, growth_stage, temperature_c, humidity_pct, rainfall_mm, rain_forecast_prob=20):
        """
        Evaluates weather-induced agronomic risk factors based on ICAR/FAO disease-climate rules.
        Transparently labels calculations as agronomic biometeorological rule evaluations,
        never claiming simple rules to be deep neural models.
        """
        risks = []
        action_recommendations = []
        overall_severity = "Low"
        
        crop = crop_type.title()
        
        # 1. Late Blight Favorable Conditions (Phytophthora infestans)
        # Favored by 15-24°C temp and >80% relative humidity
        if crop in ["Tomato", "Potato"]:
            if 14.0 <= temperature_c <= 25.0 and humidity_pct >= 80:
                risks.append({
                    "hazard": "High Late Blight Risk (Phytophthora infestans)",
                    "severity": "High",
                    "scientific_basis": "Prolonged leaf wetness combined with temperature between 14-25°C and RH >80% provides optimal sporulation microclimate.",
                    "distinction": "This is an environmental risk index, NOT a confirmed field diagnosis."
                })
                action_recommendations.append("Inspect lower canopy leaves and undersides for water-soaked lesions.")
                action_recommendations.append("Avoid sprinkler/overhead irrigation; ensure inter-row drainage.")
                overall_severity = "High"
            elif humidity_pct >= 75:
                risks.append({
                    "hazard": "Moderate Early Blight & Leaf Mold Susceptibility",
                    "severity": "Moderate",
                    "scientific_basis": "Elevated humidity (>75%) increases fungal spore germination.",
                    "distinction": "Environmental susceptibility indicator."
                })
                action_recommendations.append("Ensure proper row spacing and prune lower senescent leaves for canopy aeration.")
                if overall_severity != "High":
                    overall_severity = "Moderate"

        # 2. Extreme Heat Stress
        if temperature_c >= 36.0:
            risks.append({
                "hazard": "Severe Heat & Blossom Drop Stress",
                "severity": "High",
                "scientific_basis": "Temperatures exceeding 36°C induce pollen sterility in solanaceous crops and increase evapotranspiration stress.",
                "distinction": "Physiological abiotic stress factor."
            })
            action_recommendations.append("Maintain soil root-zone moisture via early morning micro-irrigation.")
            action_recommendations.append("Consider light mulching to regulate soil temperature.")
            overall_severity = "High"
            
        # 3. Excessive Rainfall / Waterlogging
        if rainfall_mm >= 30.0 or rain_forecast_prob >= 75:
            risks.append({
                "hazard": "Waterlogging & Root Asphyxiation Alert",
                "severity": "Moderate",
                "scientific_basis": "Excess surface standing water depletes soil oxygen within 24-48 hours, predisposing roots to Pythium/damping-off.",
                "distinction": "Hydrological risk assessment."
            })
            action_recommendations.append("Clear drainage channels around plots immediately to prevent standing water pools.")
            action_recommendations.append("Pause scheduled fertigation until soil aerates.")
            if overall_severity != "High":
                overall_severity = "Moderate"

        if not risks:
            risks.append({
                "hazard": "Favorable Weather Window",
                "severity": "Low",
                "scientific_basis": "Current temperature and humidity parameters fall within standard vegetative growth thresholds without acute pathogen triggers.",
                "distinction": "No adverse atmospheric stress detected."
            })
            action_recommendations.append("Continue routine scouting and standard crop management calendar.")

        return {
            "status": "success",
            "crop": crop,
            "growth_stage": growth_stage,
            "inputs_evaluated": {
                "temperature_c": temperature_c,
                "humidity_pct": humidity_pct,
                "rainfall_mm": rainfall_mm,
                "rain_forecast_prob": rain_forecast_prob
            },
            "overall_severity": overall_severity,
            "risk_factors": risks,
            "action_recommendations": action_recommendations,
            "methodology": "ICAR Biometeorological Agronomic Decision Matrix (Rule-based empirical model, not deep learning)"
        }

risk_analysis_service = WeatherRiskAnalysisService.get_instance()
