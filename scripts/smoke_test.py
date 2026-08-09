"""
CloudPulse-AI Automated End-to-End API Smoke Test Suite.
Validates that every core API endpoint is operational and returns 200/201.
"""

from __future__ import annotations

import asyncio
import sys
import time
from typing import Any

import httpx


async def run_smoke_tests() -> int:
    base_url = "http://127.0.0.1:8000"
    print("=" * 70)
    print(" CloudPulse-AI Platform API Smoke Test Suite")
    print(f" Target: {base_url}")
    print("=" * 70)

    passed = 0
    failed = 0
    total_tests = 0

    async with httpx.AsyncClient(base_url=base_url, timeout=15.0) as client:
        # 1. Health Checks
        total_tests += 1
        try:
            res = await client.get("/health")
            if res.status_code == 200:
                print(f"[PASS] GET  /health -> 200 OK ({res.json().get('status')})")
                passed += 1
            else:
                print(f"[FAIL] GET  /health -> {res.status_code} {res.text}")
                failed += 1
        except Exception as exc:
            print(f"[FAIL] GET  /health -> Connection Error: {exc}")
            failed += 1

        total_tests += 1
        try:
            res = await client.get("/ready")
            if res.status_code == 200:
                print(f"[PASS] GET  /ready -> 200 OK")
                passed += 1
            else:
                print(f"[FAIL] GET  /ready -> {res.status_code}")
                failed += 1
        except Exception as exc:
            print(f"[FAIL] GET  /ready -> Connection Error: {exc}")
            failed += 1

        # 2. Authentication Login
        total_tests += 1
        token = ""
        try:
            res = await client.post(
                "/api/v1/auth/login",
                json={"email": "admin@cloudpulse.io", "password": "Password123!"},
            )
            if res.status_code == 200:
                token = res.json().get("access_token")
                print(f"[PASS] POST /api/v1/auth/login -> 200 OK (JWT token received)")
                passed += 1
            else:
                print(f"[FAIL] POST /api/v1/auth/login -> {res.status_code} {res.text}")
                failed += 1
        except Exception as exc:
            print(f"[FAIL] POST /api/v1/auth/login -> Error: {exc}")
            failed += 1

        headers = {"Authorization": f"Bearer {token}"} if token else {}

        # 3. Telemetry Pipeline
        total_tests += 1
        try:
            res = await client.get("/api/v1/telemetry/health", headers=headers)
            if res.status_code == 200:
                print(f"[PASS] GET  /api/v1/telemetry/health -> 200 OK ({res.json().get('status')})")
                passed += 1
            else:
                print(f"[FAIL] GET  /api/v1/telemetry/health -> {res.status_code}")
                failed += 1
        except Exception as exc:
            print(f"[FAIL] GET  /api/v1/telemetry/health -> Error: {exc}")
            failed += 1

        # 4. Cost Optimizer
        endpoints_to_test = [
            ("GET", "/api/v1/cost/overview", None),
            ("GET", "/api/v1/cost/services", None),
            ("GET", "/api/v1/cost/recommendations", None),
            ("GET", "/api/v1/cost/resources", None),
            ("GET", "/api/v1/incidents/active", None),
            ("GET", "/api/v1/incidents/stats", None),
            ("GET", "/api/v1/incidents/analytics", None),
            ("GET", "/api/v1/incidents", None),
            ("POST", "/api/v1/chat/query", {"question": "What is the CPU usage on api-gateway?"}),
            ("POST", "/api/v1/ai/chat", {"message": "How do I optimize my cloud infrastructure?"}),
            ("GET", "/api/v1/cloud/accounts", None),
            ("GET", "/api/v1/cloud/resources", None),
            ("GET", "/api/v1/kubernetes/clusters", None),
            ("GET", "/api/v1/kubernetes/nodes", None),
            ("GET", "/api/v1/kubernetes/pods", None),
            ("GET", "/api/v1/workflows", None),
            ("GET", "/api/v1/workflows/templates", None),
            ("GET", "/api/v1/traces", None),
            ("GET", "/api/v1/services/map", None),
            ("GET", "/api/v1/aiops/status", None),
            ("GET", "/api/v1/aiops/recommendations", None),
            ("GET", "/api/v1/security/findings", None),
            ("GET", "/api/v1/security/compliance", None),
            ("GET", "/api/v1/runbooks", None),
            ("GET", "/api/v1/predictions", None),
            ("GET", "/api/v1/predictions/stats", None),
            ("GET", "/api/v1/servers", None),
            ("GET", "/api/v1/alerts", None),
            ("GET", "/api/v1/notifications", None),
            ("GET", "/api/v1/twin", None),
        ]

        for method, path, body in endpoints_to_test:
            total_tests += 1
            try:
                t0 = time.perf_counter()
                if method == "GET":
                    res = await client.get(path, headers=headers)
                else:
                    res = await client.post(path, json=body, headers=headers)
                elapsed = int((time.perf_counter() - t0) * 1000)

                if res.status_code in [200, 201]:
                    print(f"[PASS] {method:4} {path:<34} -> {res.status_code} ({elapsed}ms)")
                    passed += 1
                else:
                    print(f"[FAIL] {method:4} {path:<34} -> {res.status_code} {res.text[:120]}")
                    failed += 1
            except Exception as exc:
                print(f"[FAIL] {method:4} {path:<34} -> Error: {exc}")
                failed += 1

    print("=" * 70)
    print(f" Summary: {passed}/{total_tests} Tests Passed (Failed: {failed})")
    print("=" * 70)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    code = asyncio.run(run_smoke_tests())
    sys.exit(code)
