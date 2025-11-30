import unittest
from src.utils.analytics import AnalyticsEngine

class TestAnalytics(unittest.TestCase):
    def test_weak_areas(self):
        # Mock history: 2 wrong from Doc A, 1 right from Doc A, 1 wrong from Doc B
        history = [
            {"source": "Doc A", "is_correct": False},
            {"source": "Doc A", "is_correct": False},
            {"source": "Doc A", "is_correct": True},
            {"source": "Doc B", "is_correct": False},
            {"source": "Doc C", "is_correct": True},
        ]
        
        weak_areas = AnalyticsEngine.analyze_weak_areas(history)
        
        # Doc A: 2/3 wrong = 0.67
        # Doc B: 1/1 wrong = 1.0
        # Doc C: 0/1 wrong = 0.0 (Should not be in list)
        
        self.assertIn("Doc A", weak_areas)
        self.assertIn("Doc B", weak_areas)
        self.assertNotIn("Doc C", weak_areas)
        self.assertEqual(weak_areas["Doc B"], 1.0)
        self.assertEqual(weak_areas["Doc A"], 0.67)

    def test_learning_metrics_fast(self):
        # Slope 0.3 (Fast)
        metrics = AnalyticsEngine.calculate_learning_metrics(0.3, 3.0)
        self.assertEqual(metrics["learning_speed"], "Fast ⚡")
        # Remaining 2.0 / 0.3 = 6.6 -> 6 attempts
        self.assertEqual(metrics["time_to_mastery"], "~6 more attempts")

    def test_learning_metrics_struggling(self):
        # Slope -0.1 (Struggling)
        metrics = AnalyticsEngine.calculate_learning_metrics(-0.1, 3.0)
        self.assertEqual(metrics["learning_speed"], "Struggling ⚠️")
        self.assertEqual(metrics["time_to_mastery"], "Indefinite (Slope too low)")

if __name__ == '__main__':
    unittest.main()
