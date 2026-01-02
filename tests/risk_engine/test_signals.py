import pytest
from src.risk_engine.signals import SignalDetector


class TestSignalDetector:
    def test_detect_no_signals(self):
        detector = SignalDetector()
        scores = {"security": 20, "political": 20, "composite": 20}
        signals = detector.detect_signals(scores, [20.0])
        assert len(signals) == 0

    def test_detect_flashpoint(self):
        detector = SignalDetector()
        scores = {"security": 75, "political": 50, "composite": 60}
        signals = detector.detect_signals(scores, [])
        assert len(signals) >= 1
        assert signals[0]["type"] == "flashpoint_risk"
        assert signals[0]["severity"] == "high"

    def test_detect_destabilization(self):
        detector = SignalDetector()
        scores = {"security": 30, "political": 65, "composite": 50}
        signals = detector.detect_signals(scores, [])
        found = False
        for s in signals:
            if s["type"] == "destabilization":
                found = True
                break
        assert found

    def test_detect_critical(self):
        detector = SignalDetector()
        scores = {"security": 20, "political": 20, "composite": 85}
        signals = detector.detect_signals(scores, [])
        found = False
        for s in signals:
            if s["type"] == "critical_status":
                found = True
                break
        assert found
