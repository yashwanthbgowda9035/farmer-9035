class SoilService:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def interpret_measurements(self, ph, nitrogen, phosphorus, potassium, organic_carbon=0.55, ec=0.45, target_crop="Tomato"):
        """
        Interprets laboratory soil-test measurements against official ICAR Soil Health Card benchmarks.
        Explicitly clarifies that soil chemistry cannot be inferred from leaf/ground photos.
        """
        deficiencies = []
        strengths = []
        advisories = []
        
        # pH interpretation
        if ph < 5.5:
            ph_status = "Strongly Acidic (Al/Fe toxicity risk, P fixation)"
            deficiencies.append("Soil acidity limiting phosphorus availability")
            advisories.append("Apply agricultural lime (calcium carbonate) or dolomite as per soil buffer capacity before next crop cycle.")
        elif 5.5 <= ph < 6.5:
            ph_status = "Slightly Acidic (Acceptable for solanaceous crops & potatoes)"
            strengths.append("Favorable pH for potato and tomato micronutrient intake")
        elif 6.5 <= ph <= 7.5:
            ph_status = "Optimal Neutral (Ideal microbial activity & nutrient availability)"
            strengths.append("Optimum pH for comprehensive nutrient uptake")
        elif 7.5 < ph <= 8.5:
            ph_status = "Moderately Alkaline (Calcareous / Micronutrient lock-in risk)"
            deficiencies.append("Zinc and iron availability may be restricted by high pH")
            advisories.append("Incorporate organic matter / farmyard manure (FYM) and consider gypsum if sodium is elevated.")
        else:
            ph_status = "Strongly Alkaline / Saline-Sodic"
            deficiencies.append("Severe alkalinity restricting root growth")
            advisories.append("Consult KVK soil scientist for gypsum requirement test.")

        # Nitrogen (N) benchmark (kg/ha)
        if nitrogen < 280:
            n_status = "Low (< 280 kg/ha)"
            deficiencies.append("Nitrogen deficiency (Risk of stunted growth & chlorosis)")
            advisories.append("Split-apply nitrogen via well-decomposed FYM and balanced neem-coated urea or compost tea.")
        elif 280 <= nitrogen <= 560:
            n_status = "Medium (280 - 560 kg/ha, Sufficient)"
            strengths.append("Adequate available soil nitrogen")
        else:
            n_status = "High (> 560 kg/ha)"
            strengths.append("High nitrogen content; curtail excess N to prevent vegetative overgrowth & pest flare-ups.")

        # Phosphorus (P) benchmark (kg/ha)
        if phosphorus < 10:
            p_status = "Low (< 10 kg/ha)"
            deficiencies.append("Phosphorus deficiency (Risk of purpling leaves & weak root system)")
            advisories.append("Incorporate single super phosphate (SSP) or rock phosphate with PSB (Phosphorus Solubilizing Bacteria).")
        elif 10 <= phosphorus <= 25:
            p_status = "Medium (10 - 25 kg/ha, Sufficient)"
            strengths.append("Balanced soil phosphorus")
        else:
            p_status = "High (> 25 kg/ha)"
            strengths.append("Abundant soil phosphorus reserves")

        # Potassium (K) benchmark (kg/ha)
        if potassium < 110:
            k_status = "Low (< 110 kg/ha)"
            deficiencies.append("Potassium deficiency (Risk of marginal leaf scorch & poor fruit firmness)")
            advisories.append("Apply muriate of potash (MOP) or sulfate of potash (SOP) according to crop stage.")
        elif 110 <= potassium <= 280:
            k_status = "Medium (110 - 280 kg/ha, Sufficient)"
            strengths.append("Adequate potassium for fruit development")
        else:
            k_status = "High (> 280 kg/ha)"
            strengths.append("High soil potassium status")

        # Electrical Conductivity (dS/m)
        if ec < 1.0:
            ec_status = "Normal (< 1.0 dS/m, Safe from salinity stress)"
        elif 1.0 <= ec <= 2.0:
            ec_status = "Critical (1.0 - 2.0 dS/m, Sensitive crops may show yield decline)"
            deficiencies.append("Moderate salinity tension")
        else:
            ec_status = "Hazardous (> 2.0 dS/m, High soluble salts)"
            deficiencies.append("Severe salinity hazard requiring leaching")

        # Expert follow-up prompts
        expert_questions = [
            f"Given our pH of {ph} and target crop {target_crop}, what is the recommended basal compost application rate?",
            f"Are foliar micronutrient sprays (Boron, Zinc, Iron) needed to prevent flower drop under this nutrient profile?",
            "What green manuring crop (e.g. Sunn hemp, Dhaincha) is best suited for our upcoming season to improve soil organic carbon?"
        ]

        return {
            "status": "success",
            "target_crop": target_crop,
            "measurements": {
                "ph": {"value": ph, "status": ph_status},
                "nitrogen": {"value": nitrogen, "unit": "kg/ha", "status": n_status},
                "phosphorus": {"value": phosphorus, "unit": "kg/ha", "status": p_status},
                "potassium": {"value": potassium, "unit": "kg/ha", "status": k_status},
                "organic_carbon": {"value": organic_carbon, "unit": "%", "status": "Medium" if organic_carbon >= 0.5 else "Low"},
                "electrical_conductivity": {"value": ec, "unit": "dS/m", "status": ec_status}
            },
            "strengths": strengths,
            "deficiencies": deficiencies,
            "actionable_advisories": advisories,
            "expert_follow_up_questions": expert_questions,
            "scientific_reference": "ICAR Central Soil Salinity Research Institute & Ministry of Agriculture Soil Health Card Reference Tables."
        }

soil_service = SoilService.get_instance()
