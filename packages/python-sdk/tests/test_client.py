"""Synchronous client tests against recorded API fixtures."""

from __future__ import annotations

import httpx
import pytest

from conftest import API_KEY, BASE_URL, CONTRACT_ID, make_sync_client
from sorolens import exceptions


@pytest.fixture
def client():
    http_client = make_sync_client()
    yield http_client
    http_client.close()


def test_global_stats(client):
    stats = client.stats.global_stats()
    assert stats.tracked_contracts == 42
    assert stats.total_events == 1048576


def test_list_contracts(client):
    page = client.contracts.list(limit=2)
    assert page.next_cursor == "eyJvZmZzZXQiOjJ9"
    assert [contract.label for contract in page.contracts] == ["counter", "watchdog"]
    assert page.contracts[1].backfill_complete_at is None
    # Tags ride along on the list response; an untagged contract reports [].
    assert page.contracts[0].tags == ["prod"]
    assert page.contracts[1].tags == []


def test_get_contract(client):
    contract = client.contracts.get(CONTRACT_ID)
    assert contract.id == CONTRACT_ID
    assert contract.status.value == "active"
    assert contract.tags == ["prod"]


def test_get_missing_contract_raises_not_found(client):
    with pytest.raises(exceptions.NotFoundError) as exc_info:
        client.contracts.get("missing")
    assert "contract not found" in str(exc_info.value)
    assert exc_info.value.status_code == 404


def test_list_events(client):
    page = client.events.list(CONTRACT_ID, limit=1)
    assert page.events[0].tx_hash.startswith("a1b2c3")


def test_watchdog_stats_filters(client):
    stats = client.watchdog.stats(network="mainnet")
    assert stats.total_monitored == 12
    assert stats.critical_alerts == 3


def test_create_api_key(client):
    created = client.api_keys.create("ci-reader", ["read:contracts"])
    assert created.key == "sk_read_0123456789abcdef0123456789abcdef"
    assert created.name == "ci-reader"


def test_api_key_sent_as_bearer_token():
    seen: list[httpx.Request] = []

    def transport(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"status": "ok"})

    with make_sync_client(httpx.MockTransport(transport)) as client:
        client.health.health()

    assert seen[0].headers["Authorization"] == f"Bearer {API_KEY}"
    assert str(seen[0].url) == f"{BASE_URL}/health"


# ---- facade surfaces added for issue #556 (search / reports / alerts) ------


def test_search(client):
    res = client.search("counter", limit=5)
    assert [contract.label for contract in res.items] == ["counter"]


def test_list_alerts(client):
    page = client.alerts.list(severity="Warning", limit=50)
    group = page.groups[0]
    assert group.rule == "error_rate"
    assert group.severity.value == "Warning"


def test_get_contract_report(client):
    report = client.reports.get(CONTRACT_ID, month="2026-05")
    assert report.uptime_pct == 99.5
    assert report.incidents == 2


def test_report_history(client):
    history = client.reports.history(CONTRACT_ID, months=3)
    assert history.months[0].month == "2026-04"


def test_report_subscription_lifecycle(client):
    created = client.reports.subscribe("ops@example.com", "weekly", day_of_week=1)
    assert created.id == "rs_1"
    listed = client.reports.subscriptions("ops@example.com")
    assert [sub.frequency.value for sub in listed.subscriptions] == ["weekly"]
    client.reports.unsubscribe("rs_1")


def test_api_key_get_and_rotate(client):
    meta = client.api_keys.get("key-1")
    assert meta.name == "ci"
    assert meta.key_prefix == "sk_ci"
    rotated = client.api_keys.rotate("key-1")
    assert rotated.key.startswith("sk_")


# ---- facade wiring for the remaining v1 surfaces (issue #556) -------------


def test_alert_rules_list(client):
    assert client.rules.list().rules == []


def test_groups_list(client):
    assert client.groups.list("user-1").groups == []


def test_watched_accounts_list(client):
    assert client.watched_accounts.list().watched_accounts == []


def test_recent_events(client):
    assert client.events.recent(limit=5).events == []
