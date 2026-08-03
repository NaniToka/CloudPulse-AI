"""
Unit tests for the Cost Analysis Engine.
"""

from app.services.cost_engine import (
    calculate_efficiency_score,
    group_costs_by_region,
    group_costs_by_service,
)


def test_calculate_efficiency_score():
    assert calculate_efficiency_score(100.0, 0.0) == 100
    assert calculate_efficiency_score(100.0, 50.0) == 50
    assert calculate_efficiency_score(100.0, 100.0) == 0
    assert calculate_efficiency_score(0.0, 10.0) == 100


def test_group_costs_by_service():
    sample_costs = [
        {"service": "GKE", "cost": 100.0},
        {"service": "GKE", "cost": 200.0},
        {"service": "Cloud SQL", "cost": 100.0},
    ]

    grouped = group_costs_by_service(sample_costs)
    assert len(grouped) == 2
    assert grouped[0]["service"] == "GKE"
    assert grouped[0]["cost"] == 300.0
    assert grouped[0]["percentage"] == 75.0
    assert grouped[0]["resource_count"] == 2

    assert grouped[1]["service"] == "Cloud SQL"
    assert grouped[1]["cost"] == 100.0
    assert grouped[1]["percentage"] == 25.0


def test_group_costs_by_region():
    sample_costs = [
        {"region": "us-central1", "cost": 500.0},
        {"region": "europe-west1", "cost": 500.0},
    ]

    grouped = group_costs_by_region(sample_costs)
    assert len(grouped) == 2
    assert grouped[0]["percentage"] == 50.0
    assert grouped[1]["percentage"] == 50.0
