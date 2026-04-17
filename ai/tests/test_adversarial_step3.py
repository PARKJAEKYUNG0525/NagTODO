"""Adversarial tests for Step 3: Interference Pipeline"""

import pytest
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch
from ai.interference.stats import compute_stats


class TestComputeStatsEdgeCases:
    """compute_stats() edge cases"""

    def test_compute_stats_with_none_user_id(self):
        """None user_id should not crash"""
        tasks = [
            {"user_id": "u1", "completed": True, "text": "task1"},
        ]
        result = compute_stats(tasks, None)
        assert result["personal_rate"] is None

    def test_compute_stats_with_empty_string_user_id(self):
        """Empty string user_id treated as valid ID"""
        tasks = [
            {"user_id": "", "completed": True, "text": "task1"},
        ]
        result = compute_stats(tasks, "")
        assert result["personal_rate"] == pytest.approx(100.0)

    def test_compute_stats_missing_completed_defaults_false(self):
        """Missing completed field defaults to False"""
        tasks = [
            {"user_id": "u1", "text": "task1"},
        ]
        result = compute_stats(tasks, "u1")
        assert result["personal_rate"] == pytest.approx(0.0)

    def test_compute_stats_missing_text_raises_error(self):
        """Missing text field in failed task raises ValueError"""
        tasks = [
            {"user_id": "u1", "completed": False},  # Not completed - text required
        ]
        with pytest.raises(ValueError, match="text"):
            compute_stats(tasks, "u1")

    def test_compute_stats_max_failures_10(self):
        """similar_failures capped at 10"""
        tasks = [{"user_id": "u1", "completed": False, "text": f"fail{i}"} for i in range(15)]
        result = compute_stats(tasks, "u1")
        assert len(result["similar_failures"]) == 10
