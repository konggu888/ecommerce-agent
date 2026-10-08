    def test_normalizes_duplicate_confidence(self):
        result = normalize_footage_analysis({"clips": [{"source": "a.mp4", "duplicate_confidence": 8}]})
        self.assertEqual(result["clips"][0]["duplicate_confidence"], 1.0)
