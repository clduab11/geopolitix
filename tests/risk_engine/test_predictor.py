import pytest
from src.risk_engine.predictor import RiskPredictor


class TestRiskPredictor:
    def test_init_default(self):
        predictor = RiskPredictor()
        assert predictor.alpha == 0.3

    def test_init_custom_alpha(self):
        predictor = RiskPredictor(alpha=0.5)
        assert predictor.alpha == 0.5

    def test_predict_next_score_empty(self):
        predictor = RiskPredictor()
        assert predictor.predict_next_score([]) == 50.0

    def test_predict_next_score_single(self):
        predictor = RiskPredictor()
        assert predictor.predict_next_score([60.0]) == 60.0

    def test_predict_next_score_constant(self):
        predictor = RiskPredictor()
        history = [60.0, 60.0, 60.0]
        assert predictor.predict_next_score(history) == 60.0

    def test_predict_next_score_increasing(self):
        # S_0 = 50
        # S_1 = 0.5 * 60 + 0.5 * 50 = 55
        # S_2 = 0.5 * 70 + 0.5 * 55 = 35 + 27.5 = 62.5
        predictor = RiskPredictor(alpha=0.5)
        history = [50.0, 60.0, 70.0]
        prediction = predictor.predict_next_score(history)
        assert prediction == 62.5

    def test_generate_feature_vector(self):
        predictor = RiskPredictor()
        vector = predictor.generate_feature_vector(
            political=80.0,
            economic=50.0,
            security=20.0,
            trade=100.0,
            news_sentiment=0.0,
        )
        assert vector == [0.8, 0.5, 0.2, 1.0, 0.5]
