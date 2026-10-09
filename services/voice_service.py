class VoiceService:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def get_supported_languages(self):
        return [
            {
                "code": "en",
                "name": "English",
                "speech_recognition_tag": "en-IN",
                "speech_synthesis_voice": "en-IN",
                "flag": "🇮🇳"
            },
            {
                "code": "kn",
                "name": "ಕನ್ನಡ (Kannada)",
                "speech_recognition_tag": "kn-IN",
                "speech_synthesis_voice": "kn-IN",
                "flag": "🌾"
            }
        ]

    def process_voice_transcript(self, raw_transcript, language="en"):
        """
        Cleans and normalizes voice transcripts from browser Web Speech API.
        """
        cleaned = raw_transcript.strip()
        return {
            "status": "success",
            "language": language,
            "original_transcript": raw_transcript,
            "processed_query": cleaned,
            "length": len(cleaned)
        }

voice_service = VoiceService.get_instance()
