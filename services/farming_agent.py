import os
import json
from datetime import datetime
from config import Config
from models.database import db
from models.crop import CropPlot, CropObservation
from models.analysis import CropAnalysis, SoilRecord
from services.weather_service import weather_service
from services.risk_analysis import risk_analysis_service
from services.soil_service import soil_service
from services.rag_service import rag_service
from services.market_service import market_service
from services.crop_recommender import crop_recommender_service

class FarmingAgentService:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        self.tools = {
            "analyse_crop_image": {
                "name": "analyse_crop_image",
                "description": "Examines uploaded leaf photograph using computer vision screening for disease lesions.",
                "required_args": ["analysis_id"]
            },
            "get_crop_history": {
                "name": "get_crop_history",
                "description": "Retrieves registered plots and dated observation records for the farmer.",
                "required_args": ["user_id"]
            },
            "get_weather_information": {
                "name": "get_weather_information",
                "description": "Retrieves current meteorological telemetry and precipitation forecasts.",
                "required_args": ["location"]
            },
            "interpret_soil_measurements": {
                "name": "interpret_soil_measurements",
                "description": "Evaluates soil chemistry test (pH, N, P, K) against ICAR standards.",
                "required_args": ["ph", "nitrogen", "phosphorus", "potassium"]
            },
            "search_agricultural_knowledge": {
                "name": "search_agricultural_knowledge",
                "description": "Executes semantic RAG query across verified agricultural extension handbooks.",
                "required_args": ["query"]
            },
            "get_market_price_history": {
                "name": "get_market_price_history",
                "description": "Retrieves wholesale mandi prices and 10-day market trends from KSAMB.",
                "required_args": ["commodity"]
            },
            "create_crop_monitoring_checklist": {
                "name": "create_crop_monitoring_checklist",
                "description": "Generates actionable crop scouting checklist for current growth stage.",
                "required_args": ["crop_type", "growth_stage"]
            },
            "create_draft_farming_plan": {
                "name": "create_draft_farming_plan",
                "description": "Drafts structured seasonal farming calendar with nutrient & irrigation milestones.",
                "required_args": ["crop_type", "acreage"]
            },
            "summarise_farmer_records": {
                "name": "summarise_farmer_records",
                "description": "Summarizes total plots, past analyses, and active reminders for the farmer.",
                "required_args": ["user_id"]
            }
        }

    # 1. Tool implementations
    def tool_analyse_crop_image(self, user_id, args):
        analysis_id = args.get("analysis_id")
        rec = CropAnalysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        if not rec:
            return {"status": "error", "message": f"Crop analysis record #{analysis_id} not found or not owned by user."}
        return {
            "status": "success",
            "crop": rec.crop_type,
            "predicted_condition": rec.predicted_class,
            "confidence_pct": rec.confidence,
            "recommendations": rec.recommendations,
            "citations": rec.scientific_citations,
            "is_preliminary": rec.is_preliminary
        }

    def tool_get_crop_history(self, user_id, args):
        plots = CropPlot.query.filter_by(user_id=user_id).all()
        result = []
        for p in plots:
            obs_count = len(p.observations)
            result.append({
                "plot_id": p.id,
                "name": p.plot_name,
                "crop": p.crop_type,
                "acreage": p.acreage,
                "soil": p.soil_type,
                "irrigation": p.irrigation_system,
                "observations_logged": obs_count
            })
        return {"status": "success", "plots": result, "total_plots": len(result)}

    def tool_get_weather_information(self, user_id, args):
        w = weather_service.get_weather()
        return w

    def tool_interpret_soil_measurements(self, user_id, args):
        try:
            ph = float(args.get("ph", 6.5))
            n = float(args.get("nitrogen", 240))
            p = float(args.get("phosphorus", 18))
            k = float(args.get("potassium", 160))
            return soil_service.interpret_measurements(ph, n, p, k)
        except Exception as e:
            return {"status": "error", "message": f"Invalid soil input values: {str(e)}"}

    def tool_search_agricultural_knowledge(self, user_id, args):
        q = args.get("query", "")
        lang = args.get("language", "en")
        return rag_service.query(q, language=lang)

    def tool_get_market_price_history(self, user_id, args):
        commodity = args.get("commodity", "Tomato")
        return market_service.get_market_trends(commodity)

    def tool_create_crop_monitoring_checklist(self, user_id, args):
        crop = args.get("crop_type", "Tomato").title()
        stage = args.get("growth_stage", "Vegetative").title()
        checklists = {
            "Tomato": {
                "Vegetative": [
                    "Inspect under lower leaves for early blight target-spots.",
                    "Check drip emitters for uniform water discharge.",
                    "Scout for whiteflies or leaf miners on tender upper growth.",
                    "Ensure bamboo/string staking is erect to keep foliage off bare ground."
                ],
                "Flowering": [
                    "Monitor for blossom end rot symptoms (check calcium & moisture consistency).",
                    "Scout flower clusters for thrips and fruit borer egg deposits.",
                    "Avoid water stress to prevent flower abortion."
                ],
                "Fruiting": [
                    "Check fruit skin for sunburn or caterpillar bore holes.",
                    "Maintain steady potassium fertigation for fruit firmness.",
                    "Remove fallen or decaying fruits immediately to prevent fungal spore buildup."
                ]
            }
        }
        items = checklists.get(crop, {}).get(stage, [
            f"Check crop vigor and soil moisture around root zone.",
            f"Inspect lower leaf canopies for discoloration or insect activity.",
            f"Record observation photograph in KrishiMitra plot tracker."
        ])
        return {
            "status": "success",
            "crop": crop,
            "stage": stage,
            "checklist_items": items,
            "recommended_frequency": "Every 3 to 4 days during active vegetative/fruiting growth."
        }

    def tool_create_draft_farming_plan(self, user_id, args):
        crop = args.get("crop_type", "Tomato").title()
        acreage = float(args.get("acreage", 1.0))
        plan = {
            "crop": crop,
            "acreage": acreage,
            "stage_1_land_prep": "Deep plowing + 10-15 tonnes FYM per hectare + broad beds with drip lines.",
            "stage_2_transplanting": "25-30 day old sturdy seedlings, 60cm x 45cm spacing, evening planting.",
            "stage_3_nutrient_management": "Basal DAP + MOP; weekly split fertigation with 19-19-19 and calcium nitrate.",
            "stage_4_pest_disease_surveillance": "Yellow sticky traps (10/acre) + weekly scouting + biopesticide Trichoderma drenching.",
            "estimated_cycle_duration_days": 110,
            "confirmation_required": True,
            "note": "Draft plan generated for planning. Confirmation required before creating plot calendar records."
        }
        return {"status": "success", "plan": plan}

    def tool_summarise_farmer_records(self, user_id, args):
        plots = CropPlot.query.filter_by(user_id=user_id).count()
        analyses = CropAnalysis.query.filter_by(user_id=user_id).count()
        soil_tests = SoilRecord.query.filter_by(user_id=user_id).count()
        return {
            "status": "success",
            "registered_plots": plots,
            "leaf_analyses_conducted": analyses,
            "soil_tests_recorded": soil_tests
        }

    def dispatch_tool(self, tool_name, user_id, args):
        if tool_name not in self.tools:
            return {"status": "error", "message": f"Unauthorized or unrecognized tool: {tool_name}"}
            
        tool_def = self.tools[tool_name]
        # Validate arguments
        for req in tool_def["required_args"]:
            if req not in args and req != "user_id":
                return {
                    "status": "error",
                    "message": f"Missing required parameter '{req}' for tool '{tool_name}'."
                }
                
        # Call safe dispatch
        method = getattr(self, f"tool_{tool_name}", None)
        if not method:
            return {"status": "error", "message": f"Tool handler not implemented: {tool_name}"}
            
        try:
            return method(user_id, args)
        except Exception as e:
            return {"status": "error", "message": f"Execution error in tool '{tool_name}': {str(e)}"}

    def run_agent(self, user_query, user_id, language="en"):
        """
        Multi-stage Agent execution pipeline:
        Stage 1: Intent Understanding
        Stage 2: Tool Selection & Permission Validation
        Stage 3: Information Retrieval / Tool Execution
        Stage 4: Evidence Synthesis & Honest Grounding
        """
        stages = [
            {"stage": "Understanding Question", "status": "completed", "detail": f"Parsed query: '{user_query}' (Language: {language})"},
            {"stage": "Selecting Tools", "status": "in_progress", "detail": "Evaluating approved agronomic tools"},
            {"stage": "Retrieving Information", "status": "pending", "detail": "Awaiting tool execution"},
            {"stage": "Preparing Response", "status": "pending", "detail": "Synthesizing evidence-backed advice"}
        ]
        
        tools_called = []
        evidence_items = []
        q_lower = user_query.lower()
        
        # Deterministic Tool Routing based on agricultural domain intent
        if any(w in q_lower for w in ["weather", "rain", "temperature", "cloud", "forecast", "ಹವಾಮಾನ"]):
            tool_name = "get_weather_information"
            args = {"location": "Bengaluru"}
            tools_called.append({"tool": tool_name, "args": args})
            out = self.dispatch_tool(tool_name, user_id, args)
            evidence_items.append({"source": "Meteorological Telemetry", "output": out})

        if any(w in q_lower for w in ["price", "market", "mandi", "rate", "ಮಾರಾಟ", "ಬೆಲೆ"]):
            commodity = "Tomato"
            if "potato" in q_lower: commodity = "Potato"
            elif "onion" in q_lower: commodity = "Onion"
            elif "rice" in q_lower: commodity = "Rice"
            elif "maize" in q_lower: commodity = "Maize"
            
            tool_name = "get_market_price_history"
            args = {"commodity": commodity}
            tools_called.append({"tool": tool_name, "args": args})
            out = self.dispatch_tool(tool_name, user_id, args)
            evidence_items.append({"source": f"KSAMB APMC Market Bulletin ({commodity})", "output": out})

        if any(w in q_lower for w in ["plot", "history", "records", "my crops", "farm"]):
            tool_name = "get_crop_history"
            args = {"user_id": user_id}
            tools_called.append({"tool": tool_name, "args": args})
            out = self.dispatch_tool(tool_name, user_id, args)
            evidence_items.append({"source": "Farmer Farm Records", "output": out})

        if any(w in q_lower for w in ["checklist", "scout", "inspect", "routine", "ವೀಕ್ಷಣೆ"]):
            tool_name = "create_crop_monitoring_checklist"
            args = {"crop_type": "Tomato", "growth_stage": "Vegetative"}
            tools_called.append({"tool": tool_name, "args": args})
            out = self.dispatch_tool(tool_name, user_id, args)
            evidence_items.append({"source": "Agronomic Scouting Protocol", "output": out})

        # Knowledge RAG default / fallback
        if not tools_called or any(w in q_lower for w in ["how", "what", "blight", "disease", "spray", "fertilizer", "ರೋಗ", "ಗೊಬ್ಬರ"]):
            tool_name = "search_agricultural_knowledge"
            args = {"query": user_query, "language": language}
            tools_called.append({"tool": tool_name, "args": args})
            out = self.dispatch_tool(tool_name, user_id, args)
            evidence_items.append({"source": "RAG Extension Knowledge Base", "output": out})

        # Update stages
        stages[1]["status"] = "completed"
        stages[1]["detail"] = f"Invoked tools: {', '.join([t['tool'] for t in tools_called])}"
        stages[2]["status"] = "completed"
        stages[2]["detail"] = f"Gathered {len(evidence_items)} verified data artifact(s)"
        stages[3]["status"] = "completed"
        stages[3]["detail"] = "Grounded advice prepared with transparent source provenance"

        # Synthesize clear answer
        synthesis_parts = []
        for ev in evidence_items:
            src = ev["source"]
            data = ev["output"]
            if data.get("status") == "success":
                if "answer" in data:
                    synthesis_parts.append(data["answer"])
                elif "temperature_c" in data:
                    synthesis_parts.append(
                        f"🌤️ **Weather Intelligence ({data['provider']})**:\n"
                        f"Location: {data['location']}\n"
                        f"Temperature: {data['temperature_c']}°C | Relative Humidity: {data['humidity_pct']}%\n"
                        f"Rainfall: {data['rainfall_mm']} mm | Conditions: {data['description']}"
                    )
                elif "latest_observation" in data:
                    obs = data["latest_observation"]
                    synthesis_parts.append(
                        f"📊 **Mandi Price Intelligence ({data['data_source']})**:\n"
                        f"Commodity: {data['commodity']} at {data['market_mandi']}\n"
                        f"Modal Wholesale Price: ₹{obs['modal_price']} / Quintal\n"
                        f"Daily Price Range: ₹{obs['min_price']} - ₹{obs['max_price']} / Quintal\n"
                        f"Recorded Date: {obs['date']}"
                    )
                elif "checklist_items" in data:
                    items_str = "\n".join([f"  • {item}" for item in data["checklist_items"]])
                    synthesis_parts.append(
                        f"📋 **Field Scouting Checklist ({data['crop']} - {data['stage']} Stage)**:\n"
                        f"{items_str}\n\n*Scouting Frequency: {data['recommended_frequency']}*"
                    )
                elif "plots" in data:
                    plot_list = [f"  • {p['name']} ({p['crop']}, {p['acreage']} acres, {p['irrigation']} irrigation)" for p in data["plots"]]
                    synthesis_parts.append(
                        f"🌱 **Your Farm Profile**:\n"
                        f"Total Plots Registered: {data['total_plots']}\n"
                        + ("\n".join(plot_list) if plot_list else "  No plots registered yet.")
                    )
            elif data.get("status") in ["empty_knowledge_base", "insufficient_evidence"]:
                synthesis_parts.append(f"ℹ️ {data.get('answer')}")
            else:
                synthesis_parts.append(f"⚠️ Tool notice ({src}): {data.get('message', 'No details available.')}")

        final_response = "\n\n---\n\n".join(synthesis_parts)
        if not final_response.strip():
            final_response = "I have reviewed your query and available farm records. Please clarify your specific crop question or upload a leaf photograph for targeted guidance."

        return {
            "status": "success",
            "query": user_query,
            "stages": stages,
            "tools_called": tools_called,
            "response": final_response,
            "safety_note": "KrishiMitra AI Agent adheres strictly to approved agronomic tool interfaces and verified documentation."
        }

farming_agent_service = FarmingAgentService.get_instance()
