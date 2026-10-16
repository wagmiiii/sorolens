"""Hand-written high-level facade over the generated Sorolens API client.

The low-level, spec-generated layer lives in :mod:`sorolens._generated` (produced
by ``scripts/generate_client.sh`` from ``docs/openapi.yaml``).  This module wraps
it into the ergonomic ``sorolens.Client`` / ``sorolens.AsyncClient`` surface that
application code is expected to use: same request shapes, typed return values,
sync and async (``httpx``) transports, and a small exception hierarchy instead of
raw status codes.
"""

from __future__ import annotations

from typing import Any

from . import exceptions
from ._generated.api.alerts import list_alerts
from ._generated.api.api_keys import (
    create_api_key,
    create_api_key_admin,
    get_api_key,
    list_api_keys,
    list_api_keys_admin,
    revoke_api_key,
    revoke_api_key_admin,
    rotate_api_key,
)
from ._generated.api.contracts import (
    get_api_v1_search,
    get_contract,
    list_contracts,
    register_contract,
)
from ._generated.api.events import list_contract_events, stream_contract_events
from ._generated.api.forecast import get_contract_forecast
from ._generated.api.health import health as health_operation
from ._generated.api.health import readyz
from ._generated.api.invocations import list_contract_invocations
from ._generated.api.reports import (
    create_report_subscription,
    delete_report_subscription,
    get_contract_report,
    get_contract_report_history,
    list_report_subscriptions,
)
from ._generated.api.snapshots import get_contract_snapshot
from ._generated.api.stats import get_contract_stats, get_global_stats
from ._generated.api.storage import list_contract_storage
from ._generated.api.watchdog import (
    get_monitored_contract,
    get_watchdog_stats,
    list_contract_alerts,
    list_contract_health_checks,
    list_monitored_contracts,
    list_watchdog_alerts,
)
from ._generated.api.watchlist import (
    add_to_watchlist,
    get_watchlist_status,
    list_watchlist,
    remove_from_watchlist,
)
# --- facade wiring for the remaining v1 surfaces (issue #556) ------------- #
from ._generated.api.alert_rules import (
    create_alert_rule,
    delete_alert_rule,
    list_alert_rules,
    list_rule_library,
    list_rule_metrics,
    preview_alert_rule,
    set_alert_rule_enabled,
    validate_alert_rule,
)
from ._generated.api.audit import list_audit_events
from ._generated.api.contracts import (
    add_contract_tag,
    batch_contracts,
    create_contract_note,
    delete_contract_note,
    get_contract_graph,
    get_contract_spec,
    get_invocation_trace,
    list_contract_notes,
    list_contract_upgrades,
    remove_contract_tag,
    update_contract_note,
    validate_contract,
)
from ._generated.api.events import list_all_events
from ._generated.api.groups import (
    add_group_contract,
    create_group,
    delete_group,
    get_group,
    get_group_stats,
    list_groups,
    remove_group_contract,
    remove_group_contract_by_path,
    update_group,
)
from ._generated.api.invocations import list_all_invocations
from ._generated.api.live import live_activity, recent_events
from ._generated.api.notifications import (
    create_alert_subscription,
    delete_alert_subscription,
    list_alert_subscriptions,
)
from ._generated.api.stats import (
    compare_contracts,
    get_contract_health_score,
    get_contract_summary,
)
from ._generated.api.verification import (
    get_contract_verification,
    verify_contract_source,
)
from ._generated.api.watchdog import get_contract_uptime
from ._generated.api.watched_accounts import (
    add_watched_account,
    delete_watched_account,
    list_watched_accounts,
)
from ._generated.models import (
    AddGroupContractBody,
    AddWatchedAccountBody,
    BatchContractsRequest,
    CompareContractsWindow,
    ContractNoteRequest,
    ContractTagRequest,
    ContractVerificationRequest,
    CreateAlertRuleBody,
    CreateAlertSubscription,
    CreateGroupBody,
    ListAllEventsNetwork,
    ListAllEventsType,
    ListAllInvocationsNetwork,
    ListAllInvocationsStatus,
    PreviewAlertRuleBody,
    RemoveGroupContractBody,
    SetAlertRuleEnabledBody,
    UpdateGroupBody,
    ValidateAlertRuleBody,
    ValidateContractBody,
)

from ._generated.client import AuthenticatedClient
from ._generated.client import Client as _GeneratedClient
from ._generated.models import (
    AddToWatchlistBody,
    Contract,
    ContractReport,
    ContractSnapshot,
    ContractStats,
    CreateApiKeyAdminBody,
    CreateApiKeyBody,
    CreateApiKeyBodyScopesItem,
    CreateReportSubscriptionBody,
    CreateReportSubscriptionBodyFrequency,
    GetApiV1SearchResponse200,
    GetContractReportHistoryResponse200,
    GetContractForecastResponse200,
    GetGlobalStatsResponse200,
    GetWatchdogStatsNetwork,
    HealthResponse200,
    InWatchlist,
    ListAlertsNetwork,
    ListAlertsResponse200,
    ListAlertsSeverity,
    ListApiKeysResponse200,
    ListContractAlertsNetwork,
    ListContractAlertsResponse200,
    ListContractAlertsSeverity,
    ListContractEventsNetwork,
    ListContractEventsResponse200,
    ListContractHealthChecksResponse200,
    ListContractInvocationsNetwork,
    ListContractInvocationsResponse200,
    ListContractInvocationsStatus,
    ListContractsNetwork,
    ListContractsResponse200,
    ListContractStorageDurability,
    ListContractStorageNetwork,
    ListContractStorageResponse200,
    ListContractStorageStatus,
    ListMonitoredContractsNetwork,
    ListMonitoredContractsResponse200,
    ListReportSubscriptionsResponse200,
    ListWatchdogAlertsNetwork,
    ListWatchdogAlertsResponse200,
    ListWatchdogAlertsSeverity,
    MonitoredContract,
    RegisterContractBody,
    RegisterContractBodyNetwork,
    ReportSubscription,
    StreamContractEventsResponse200,
    WatchdogStats,
    Watchlist,
)
from ._generated.types import UNSET, Response

DEFAULT_BASE_URL = "https://api.sorolens.xyz"

__all__ = ["Client", "AsyncClient", "DEFAULT_BASE_URL"]


def _build_client(
    *,
    api_key: str | None,
    base_url: str,
    timeout: Any = None,
    headers: dict[str, str] | None = None,
    **httpx_args: Any,
) -> _GeneratedClient:
    """Return a generated client, authenticated when an API key is supplied."""
    common: dict[str, Any] = {"base_url": base_url, **httpx_args}
    if timeout is not None:
        common["timeout"] = timeout
    if headers:
        common["headers"] = headers
    if api_key:
        return AuthenticatedClient(token=api_key, **common)
    return _GeneratedClient(**common)


def _unwrap(response: Response[Any]) -> Any:
    """Raise the mapped error (if any) and return the parsed payload."""
    exceptions.raise_for_response(response.status_code, response.parsed, response.content)
    return response.parsed


def _value(value: Any) -> Any:
    return UNSET if value is None else value


def _enum(enum_type: Any, value: Any) -> Any:
    return UNSET if value is None else enum_type(value)


class _SyncResource:
    def __init__(self, client: Client) -> None:
        self._client = client._client


class _AsyncResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client._client


# --------------------------------------------------------------------------- #
# Synchronous resources
# --------------------------------------------------------------------------- #
class _Health(_SyncResource):
    def health(self) -> HealthResponse200:
        """Liveness probe. Returns the parsed body (``status: ok``)."""
        return _unwrap(health_operation.sync_detailed(client=self._client))

    def readyz(self) -> Any:
        """Readiness probe. Returns the parsed body for both 200 and 503."""
        return readyz.sync_detailed(client=self._client).parsed


class _Stats(_SyncResource):
    def global_stats(self) -> GetGlobalStatsResponse200:
        """Counts across every tracked contract."""
        return _unwrap(get_global_stats.sync_detailed(client=self._client))

    def contract(self, contract_id: str, *, window: str | None = None) -> ContractStats:
        """Per-contract counters; ``window`` accepts ``"24h"``, ``"7d"`` or ``"30d"``."""
        return _unwrap(
            get_contract_stats.sync_detailed(
                contract_id, client=self._client, window=_value(window)
            )
        )

    def compare(self, ids: list[str], *, window: str | None = None) -> Any:
        """Side-by-side counters for several contracts (issue #556 facade wiring)."""
        return _unwrap(
            compare_contracts.sync_detailed(
                client=self._client,
                ids=",".join(ids),
                window=_enum(CompareContractsWindow, window),
            )
        )

    def health_score(self, contract_id: str) -> Any:
        """Composite health score for one contract."""
        return _unwrap(get_contract_health_score.sync_detailed(contract_id, client=self._client))

    def summary(self, contract_id: str) -> Any:
        """One-call rollup of stats, health and recent activity for a contract."""
        return _unwrap(get_contract_summary.sync_detailed(contract_id, client=self._client))

    def activity(self, *, minutes: int | None = None) -> Any:
        """Live activity window (default: last 30 minutes)."""
        return _unwrap(live_activity.sync_detailed(client=self._client, minutes=_value(minutes)))


class _Contracts(_SyncResource):
    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        network: str | None = None,
        status: str | None = None,
    ) -> ListContractsResponse200:
        return _unwrap(
            list_contracts.sync_detailed(
                client=self._client,
                cursor=_value(cursor),
                limit=_value(limit),
                network=_enum(ListContractsNetwork, network),
                status=_value(status),
            )
        )

    def get(self, contract_id: str) -> Contract:
        return _unwrap(get_contract.sync_detailed(contract_id, client=self._client))

    def register(self, contract_id: str, network: str, *, label: str | None = None) -> Contract:
        body = RegisterContractBody(
            id=contract_id,
            network=RegisterContractBodyNetwork(network),
            label=_value(label),
        )
        return _unwrap(register_contract.sync_detailed(client=self._client, body=body))

    # --- issue #556 facade wiring: tags, batch, graph, spec, verification --- #
    def add_tag(self, contract_id: str, body: ContractTagRequest) -> Any:
        return _unwrap(
            add_contract_tag.sync_detailed(contract_id, client=self._client, body=body)
        )

    def remove_tag(self, contract_id: str, tag: str) -> Any:
        return _unwrap(remove_contract_tag.sync_detailed(contract_id, tag, client=self._client))

    def batch(self, body: BatchContractsRequest) -> Any:
        return _unwrap(batch_contracts.sync_detailed(client=self._client, body=body))

    def graph(self, contract_id: str) -> Any:
        return _unwrap(get_contract_graph.sync_detailed(contract_id, client=self._client))

    def spec(self, contract_id: str) -> Any:
        return _unwrap(get_contract_spec.sync_detailed(contract_id, client=self._client))

    def upgrades(self, contract_id: str, *, limit: int | None = None) -> Any:
        return _unwrap(
            list_contract_upgrades.sync_detailed(
                contract_id, client=self._client, limit=_value(limit)
            )
        )

    def validate(self, body: ValidateContractBody) -> Any:
        return _unwrap(validate_contract.sync_detailed(client=self._client, body=body))

    def verification(self, contract_id: str) -> Any:
        return _unwrap(get_contract_verification.sync_detailed(contract_id, client=self._client))

    def verify_source(self, contract_id: str, body: ContractVerificationRequest) -> Any:
        return _unwrap(
            verify_contract_source.sync_detailed(contract_id, client=self._client, body=body)
        )


class _Events(_SyncResource):
    def list(
        self,
        contract_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        network: str | None = None,
        type: str | None = None,
        from_ledger: int | None = None,
        to_ledger: int | None = None,
    ) -> ListContractEventsResponse200:
        return _unwrap(
            list_contract_events.sync_detailed(
                contract_id,
                client=self._client,
                cursor=_value(cursor),
                limit=_value(limit),
                network=_enum(ListContractEventsNetwork, network),
                type_=_value(type),
                from_=_value(from_ledger),
                to=_value(to_ledger),
            )
        )

    def stream(self, contract_id: str) -> StreamContractEventsResponse200:
        """Short-poll the 20 most recent events for a contract."""
        return _unwrap(stream_contract_events.sync_detailed(contract_id, client=self._client))

    # --- issue #556 facade wiring: global event feeds ---------------------- #
    def recent(self, *, limit: int | None = None) -> Any:
        """Most recent events across every tracked contract (``GET /api/v1/events/recent``)."""
        return _unwrap(recent_events.sync_detailed(client=self._client, limit=_value(limit)))

    def list_all(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        contract_id: str | None = None,
        type: str | None = None,
        network: str | None = None,
    ) -> Any:
        """Cross-contract event listing (``GET /api/v1/events``)."""
        return _unwrap(
            list_all_events.sync_detailed(
                client=self._client,
                cursor=_value(cursor),
                limit=_value(limit),
                contract_id=_value(contract_id),
                type_=_enum(ListAllEventsType, type),
                network=_enum(ListAllEventsNetwork, network),
            )
        )


class _Invocations(_SyncResource):
    def list(
        self,
        contract_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        network: str | None = None,
        status: str | None = None,
        fn: str | None = None,
        from_ledger: int | None = None,
        to_ledger: int | None = None,
    ) -> ListContractInvocationsResponse200:
        return _unwrap(
            list_contract_invocations.sync_detailed(
                contract_id,
                client=self._client,
                cursor=_value(cursor),
                limit=_value(limit),
                network=_enum(ListContractInvocationsNetwork, network),
                status=_enum(ListContractInvocationsStatus, status),
                fn=_value(fn),
                from_=_value(from_ledger),
                to=_value(to_ledger),
            )
        )

    # --- issue #556 facade wiring: global invocation feed + trace ---------- #
    def list_all(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        contract_id: str | None = None,
        fn: str | None = None,
        status: str | None = None,
        network: str | None = None,
    ) -> Any:
        """Cross-contract invocation listing (``GET /api/v1/invocations``)."""
        return _unwrap(
            list_all_invocations.sync_detailed(
                client=self._client,
                cursor=_value(cursor),
                limit=_value(limit),
                contract_id=_value(contract_id),
                fn=_value(fn),
                status=_enum(ListAllInvocationsStatus, status),
                network=_enum(ListAllInvocationsNetwork, network),
            )
        )

    def trace(self, tx_hash: str) -> Any:
        """Full call trace for one invocation (``GET /api/v1/invocations/{tx_hash}/trace``)."""
        return _unwrap(get_invocation_trace.sync_detailed(tx_hash, client=self._client))


class _Storage(_SyncResource):
    def list(
        self,
        contract_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        network: str | None = None,
        durability: str | None = None,
        status: str | None = None,
    ) -> ListContractStorageResponse200:
        return _unwrap(
            list_contract_storage.sync_detailed(
                contract_id,
                client=self._client,
                cursor=_value(cursor),
                limit=_value(limit),
                network=_enum(ListContractStorageNetwork, network),
                durability=_enum(ListContractStorageDurability, durability),
                status=_enum(ListContractStorageStatus, status),
            )
        )


class _Forecast(_SyncResource):
    def get(
        self, contract_id: str, *, horizon: int | None = None
    ) -> GetContractForecastResponse200:
        """Forecast fees, invocations and events for the next ``horizon`` days."""
        return _unwrap(
            get_contract_forecast.sync_detailed(
                contract_id, client=self._client, horizon=_value(horizon)
            )
        )


class _Snapshots(_SyncResource):
    def get(self, contract_id: str, *, ledger: int) -> ContractSnapshot:
        return _unwrap(
            get_contract_snapshot.sync_detailed(contract_id, client=self._client, ledger=ledger)
        )


class _ApiKeys(_SyncResource):
    def list(
        self, *, cursor: str | None = None, limit: int | None = None
    ) -> ListApiKeysResponse200:
        return _unwrap(
            list_api_keys.sync_detailed(
                client=self._client, cursor=_value(cursor), limit=_value(limit)
            )
        )

    def create(self, name: str, scopes: list[str]) -> Any:
        body = CreateApiKeyBody(
            name=name, scopes=[CreateApiKeyBodyScopesItem(scope) for scope in scopes]
        )
        return _unwrap(create_api_key.sync_detailed(client=self._client, body=body))

    def revoke(self, key_id: str) -> None:
        _unwrap(revoke_api_key.sync_detailed(key_id, client=self._client))

    def get(self, key_id: str) -> Any:
        return _unwrap(get_api_key.sync_detailed(key_id, client=self._client))

    def rotate(self, key_id: str) -> Any:
        """Rotates a key; the new plaintext token is returned once."""
        return _unwrap(rotate_api_key.sync_detailed(key_id, client=self._client))

    def list_admin(
        self, *, cursor: str | None = None, limit: int | None = None
    ) -> ListApiKeysResponse200:
        return _unwrap(
            list_api_keys_admin.sync_detailed(
                client=self._client, cursor=_value(cursor), limit=_value(limit)
            )
        )

    def create_admin(self, name: str, scopes: list[str]) -> Any:
        body = CreateApiKeyAdminBody(name=name, scopes=list(scopes))
        return _unwrap(create_api_key_admin.sync_detailed(client=self._client, body=body))

    def revoke_admin(self, key_id: str) -> None:
        _unwrap(revoke_api_key_admin.sync_detailed(key_id, client=self._client))


class _Watchlist(_SyncResource):
    def list(self, user_id: str) -> Watchlist:
        return _unwrap(list_watchlist.sync_detailed(client=self._client, x_user_id=user_id))

    def add(self, user_id: str, contract_id: str) -> InWatchlist:
        body = AddToWatchlistBody(contract_id=contract_id)
        return _unwrap(
            add_to_watchlist.sync_detailed(client=self._client, body=body, x_user_id=user_id)
        )

    def remove(self, user_id: str, contract_id: str) -> InWatchlist:
        return _unwrap(
            remove_from_watchlist.sync_detailed(contract_id, client=self._client, x_user_id=user_id)
        )

    def status(self, user_id: str, contract_id: str) -> InWatchlist:
        return _unwrap(
            get_watchlist_status.sync_detailed(contract_id, client=self._client, x_user_id=user_id)
        )


class _Watchdog(_SyncResource):
    def stats(self, *, network: str | None = None) -> WatchdogStats:
        return _unwrap(
            get_watchdog_stats.sync_detailed(
                client=self._client, network=_enum(GetWatchdogStatsNetwork, network)
            )
        )

    def alerts(
        self,
        *,
        severity: str | None = None,
        network: str | None = None,
        limit: int | None = None,
    ) -> ListWatchdogAlertsResponse200:
        return _unwrap(
            list_watchdog_alerts.sync_detailed(
                client=self._client,
                severity=_enum(ListWatchdogAlertsSeverity, severity),
                network=_enum(ListWatchdogAlertsNetwork, network),
                limit=_value(limit),
            )
        )

    def contracts(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        network: str | None = None,
    ) -> ListMonitoredContractsResponse200:
        return _unwrap(
            list_monitored_contracts.sync_detailed(
                client=self._client,
                cursor=_value(cursor),
                limit=_value(limit),
                network=_enum(ListMonitoredContractsNetwork, network),
            )
        )

    def contract(self, contract_id: str) -> MonitoredContract:
        return _unwrap(get_monitored_contract.sync_detailed(contract_id, client=self._client))

    def health(
        self, contract_id: str, *, limit: int | None = None
    ) -> ListContractHealthChecksResponse200:
        return _unwrap(
            list_contract_health_checks.sync_detailed(
                contract_id, client=self._client, limit=_value(limit)
            )
        )

    def alerts_for(
        self,
        contract_id: str,
        *,
        severity: str | None = None,
        network: str | None = None,
        limit: int | None = None,
    ) -> ListContractAlertsResponse200:
        return _unwrap(
            list_contract_alerts.sync_detailed(
                contract_id,
                client=self._client,
                severity=_enum(ListContractAlertsSeverity, severity),
                network=_enum(ListContractAlertsNetwork, network),
                limit=_value(limit),
            )
        )

    # --- issue #556 facade wiring: uptime + notification subscriptions ----- #
    def uptime(self, contract_id: str) -> Any:
        return _unwrap(get_contract_uptime.sync_detailed(contract_id, client=self._client))

    def create_subscription(self, body: CreateAlertSubscription) -> Any:
        return _unwrap(
            create_alert_subscription.sync_detailed(client=self._client, body=body)
        )

    def list_subscriptions(self) -> Any:
        return _unwrap(list_alert_subscriptions.sync_detailed(client=self._client))

    def delete_subscription(self, subscription_id: str) -> None:
        _unwrap(delete_alert_subscription.sync_detailed(subscription_id, client=self._client))


class _Rules(_SyncResource):
    """Declarative alert-rule management (``/api/v1/rules*``, issue #556)."""

    def create(self, body: CreateAlertRuleBody) -> Any:
        return _unwrap(create_alert_rule.sync_detailed(client=self._client, body=body))

    def list(self) -> Any:
        return _unwrap(list_alert_rules.sync_detailed(client=self._client))

    def delete(self, rule_id: int) -> None:
        _unwrap(delete_alert_rule.sync_detailed(rule_id, client=self._client))

    def set_enabled(self, rule_id: int, body: SetAlertRuleEnabledBody) -> Any:
        return _unwrap(
            set_alert_rule_enabled.sync_detailed(rule_id, client=self._client, body=body)
        )

    def preview(self, body: PreviewAlertRuleBody) -> Any:
        return _unwrap(preview_alert_rule.sync_detailed(client=self._client, body=body))

    def validate(self, body: ValidateAlertRuleBody) -> Any:
        return _unwrap(validate_alert_rule.sync_detailed(client=self._client, body=body))

    def library(self) -> Any:
        return _unwrap(list_rule_library.sync_detailed(client=self._client))

    def metrics(self) -> Any:
        return _unwrap(list_rule_metrics.sync_detailed(client=self._client))


class _Groups(_SyncResource):
    """Contract groups (``/api/v1/groups*``); each call passes the owner user id."""

    def create(self, user_id: str, body: CreateGroupBody) -> Any:
        return _unwrap(
            create_group.sync_detailed(client=self._client, body=body, x_user_id=user_id)
        )

    def list(self, user_id: str) -> Any:
        return _unwrap(list_groups.sync_detailed(client=self._client, x_user_id=user_id))

    def get(self, group_id: str, user_id: str) -> Any:
        return _unwrap(
            get_group.sync_detailed(group_id, client=self._client, x_user_id=user_id)
        )

    def update(self, group_id: str, user_id: str, body: UpdateGroupBody) -> Any:
        return _unwrap(
            update_group.sync_detailed(
                group_id, client=self._client, body=body, x_user_id=user_id
            )
        )

    def delete(self, group_id: str, user_id: str) -> None:
        _unwrap(delete_group.sync_detailed(group_id, client=self._client, x_user_id=user_id))

    def stats(self, group_id: str, user_id: str) -> Any:
        return _unwrap(
            get_group_stats.sync_detailed(group_id, client=self._client, x_user_id=user_id)
        )

    def add_contract(self, group_id: str, user_id: str, body: AddGroupContractBody) -> Any:
        return _unwrap(
            add_group_contract.sync_detailed(
                group_id, client=self._client, body=body, x_user_id=user_id
            )
        )

    def remove_contract(self, group_id: str, user_id: str, body: RemoveGroupContractBody) -> Any:
        return _unwrap(
            remove_group_contract.sync_detailed(
                group_id, client=self._client, body=body, x_user_id=user_id
            )
        )

    def remove_contract_by_path(self, group_id: str, contract_id: str, user_id: str) -> Any:
        return _unwrap(
            remove_group_contract_by_path.sync_detailed(
                group_id, contract_id, client=self._client, x_user_id=user_id
            )
        )


class _Notes(_SyncResource):
    """Per-contract analyst notes (``/api/v1/contracts/{id}/notes``)."""

    def list(self, contract_id: str) -> Any:
        return _unwrap(list_contract_notes.sync_detailed(contract_id, client=self._client))

    def create(self, contract_id: str, body: ContractNoteRequest) -> Any:
        return _unwrap(
            create_contract_note.sync_detailed(contract_id, client=self._client, body=body)
        )

    def update(self, contract_id: str, note_id: str, body: ContractNoteRequest) -> Any:
        return _unwrap(
            update_contract_note.sync_detailed(
                contract_id, note_id, client=self._client, body=body
            )
        )

    def delete(self, contract_id: str, note_id: str) -> None:
        _unwrap(delete_contract_note.sync_detailed(contract_id, note_id, client=self._client))


class _WatchedAccounts(_SyncResource):
    """Liquidity-pool watched accounts (``/api/v1/watched-accounts``)."""

    def list(self) -> Any:
        return _unwrap(list_watched_accounts.sync_detailed(client=self._client))

    def add(self, body: AddWatchedAccountBody) -> Any:
        return _unwrap(add_watched_account.sync_detailed(client=self._client, body=body))

    def delete(self, account_id: str) -> None:
        _unwrap(delete_watched_account.sync_detailed(account_id, client=self._client))


class _Audit(_SyncResource):
    """Admin audit trail feed (``GET /api/v1/admin/audit``)."""

    def list_events(
        self, *, since: Any = None, limit: int | None = None, cursor: str | None = None
    ) -> Any:
        return _unwrap(
            list_audit_events.sync_detailed(
                client=self._client,
                since=_value(since),
                limit=_value(limit),
                cursor=_value(cursor),
            )
        )


class _Alerts(_SyncResource):
    """Cross-contract alert feed (``/api/v1/alerts``, issue #556)."""

    def list(
        self,
        *,
        flat: bool | None = None,
        contract_id: str | None = None,
        severity: str | None = None,
        network: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> ListAlertsResponse200:
        return _unwrap(
            list_alerts.sync_detailed(
                client=self._client,
                flat=_value(flat),
                contract_id=_value(contract_id),
                severity=_enum(ListAlertsSeverity, severity),
                network=_enum(ListAlertsNetwork, network),
                cursor=_value(cursor),
                limit=_value(limit),
            )
        )


class _Reports(_SyncResource):
    """SLA reports and email digest subscriptions (issue #556)."""

    def get(
        self, contract_id: str, *, month: str | None = None
    ) -> ContractReport:
        return _unwrap(
            get_contract_report.sync_detailed(
                contract_id, client=self._client, month=_value(month)
            )
        )

    def history(
        self, contract_id: str, *, months: int | None = None
    ) -> GetContractReportHistoryResponse200:
        return _unwrap(
            get_contract_report_history.sync_detailed(
                contract_id, client=self._client, months=_value(months)
            )
        )

    def subscribe(
        self, email: str, frequency: str, *, day_of_week: int | None = None
    ) -> ReportSubscription:
        body = CreateReportSubscriptionBody(
            email=email,
            frequency=CreateReportSubscriptionBodyFrequency(frequency),
            day_of_week=_value(day_of_week),
        )
        return _unwrap(
            create_report_subscription.sync_detailed(client=self._client, body=body)
        )

    def subscriptions(self, email: str) -> ListReportSubscriptionsResponse200:
        return _unwrap(
            list_report_subscriptions.sync_detailed(client=self._client, email=email)
        )

    def unsubscribe(self, subscription_id: str) -> None:
        _unwrap(delete_report_subscription.sync_detailed(subscription_id, client=self._client))


class Client:
    """Synchronous client for the Sorolens API.

    Usage::

        from sorolens import Client

        with Client(api_key="sk_...") as client:
            stats = client.stats.global_stats()
            page = client.contracts.list(limit=10)
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: Any = None,
        headers: dict[str, str] | None = None,
        **httpx_args: Any,
    ) -> None:
        self._client = _build_client(
            api_key=api_key, base_url=base_url, timeout=timeout, headers=headers, **httpx_args
        )
        self.health = _Health(self)
        self.stats = _Stats(self)
        self.contracts = _Contracts(self)
        self.events = _Events(self)
        self.invocations = _Invocations(self)
        self.storage = _Storage(self)
        self.forecast = _Forecast(self)
        self.snapshots = _Snapshots(self)
        self.api_keys = _ApiKeys(self)
        self.watchlist = _Watchlist(self)
        self.watchdog = _Watchdog(self)
        self.alerts = _Alerts(self)
        self.reports = _Reports(self)
        self.rules = _Rules(self)
        self.groups = _Groups(self)
        self.notes = _Notes(self)
        self.watched_accounts = _WatchedAccounts(self)
        self.audit = _Audit(self)

    def search(
        self, q: str, *, limit: int | None = None
    ) -> GetApiV1SearchResponse200:
        """Full-text contract search on ``GET /api/v1/search`` (issue #556)."""
        return _unwrap(
            get_api_v1_search.sync_detailed(client=self._client, q=q, limit=_value(limit))
        )

    def close(self) -> None:
        self._client.get_httpx_client().close()

    def __enter__(self) -> Client:
        self._client.get_httpx_client().__enter__()
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self._client.get_httpx_client().__exit__(*exc_info)


# --------------------------------------------------------------------------- #
# Asynchronous resources
# --------------------------------------------------------------------------- #
class _AsyncHealth(_AsyncResource):
    async def health(self) -> HealthResponse200:
        return _unwrap(await health_operation.asyncio_detailed(client=self._client))

    async def readyz(self) -> Any:
        return (await readyz.asyncio_detailed(client=self._client)).parsed


class _AsyncStats(_AsyncResource):
    async def global_stats(self) -> GetGlobalStatsResponse200:
        return _unwrap(await get_global_stats.asyncio_detailed(client=self._client))

    async def contract(self, contract_id: str, *, window: str | None = None) -> ContractStats:
        return _unwrap(
            await get_contract_stats.asyncio_detailed(
                contract_id, client=self._client, window=_value(window)
            )
        )

    async def compare(self, ids: list[str], *, window: str | None = None) -> Any:
        """Side-by-side counters for several contracts (issue #556 facade wiring)."""
        return _unwrap(
            await compare_contracts.asyncio_detailed(
                client=self._client,
                ids=",".join(ids),
                window=_enum(CompareContractsWindow, window),
            )
        )

    async def health_score(self, contract_id: str) -> Any:
        return _unwrap(await get_contract_health_score.asyncio_detailed(contract_id, client=self._client))

    async def summary(self, contract_id: str) -> Any:
        return _unwrap(await get_contract_summary.asyncio_detailed(contract_id, client=self._client))

    async def activity(self, *, minutes: int | None = None) -> Any:
        return _unwrap(await live_activity.asyncio_detailed(client=self._client, minutes=_value(minutes)))


class _AsyncContracts(_AsyncResource):
    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        network: str | None = None,
        status: str | None = None,
    ) -> ListContractsResponse200:
        return _unwrap(
            await list_contracts.asyncio_detailed(
                client=self._client,
                cursor=_value(cursor),
                limit=_value(limit),
                network=_enum(ListContractsNetwork, network),
                status=_value(status),
            )
        )

    async def get(self, contract_id: str) -> Contract:
        return _unwrap(await get_contract.asyncio_detailed(contract_id, client=self._client))

    async def register(
        self, contract_id: str, network: str, *, label: str | None = None
    ) -> Contract:
        body = RegisterContractBody(
            id=contract_id,
            network=RegisterContractBodyNetwork(network),
            label=_value(label),
        )
        return _unwrap(await register_contract.asyncio_detailed(client=self._client, body=body))

    # --- issue #556 facade wiring: tags, batch, graph, spec, verification --- #
    async def add_tag(self, contract_id: str, body: ContractTagRequest) -> Any:
        return _unwrap(
            await add_contract_tag.asyncio_detailed(contract_id, client=self._client, body=body)
        )

    async def remove_tag(self, contract_id: str, tag: str) -> Any:
        return _unwrap(
            await remove_contract_tag.asyncio_detailed(contract_id, tag, client=self._client)
        )

    async def batch(self, body: BatchContractsRequest) -> Any:
        return _unwrap(await batch_contracts.asyncio_detailed(client=self._client, body=body))

    async def graph(self, contract_id: str) -> Any:
        return _unwrap(await get_contract_graph.asyncio_detailed(contract_id, client=self._client))

    async def spec(self, contract_id: str) -> Any:
        return _unwrap(await get_contract_spec.asyncio_detailed(contract_id, client=self._client))

    async def upgrades(self, contract_id: str, *, limit: int | None = None) -> Any:
        return _unwrap(
            await list_contract_upgrades.asyncio_detailed(
                contract_id, client=self._client, limit=_value(limit)
            )
        )

    async def validate(self, body: ValidateContractBody) -> Any:
        return _unwrap(await validate_contract.asyncio_detailed(client=self._client, body=body))

    async def verification(self, contract_id: str) -> Any:
        return _unwrap(
            await get_contract_verification.asyncio_detailed(contract_id, client=self._client)
        )

    async def verify_source(self, contract_id: str, body: ContractVerificationRequest) -> Any:
        return _unwrap(
            await verify_contract_source.asyncio_detailed(
                contract_id, client=self._client, body=body
            )
        )


class _AsyncEvents(_AsyncResource):
    async def list(
        self,
        contract_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        network: str | None = None,
        type: str | None = None,
        from_ledger: int | None = None,
        to_ledger: int | None = None,
    ) -> ListContractEventsResponse200:
        return _unwrap(
            await list_contract_events.asyncio_detailed(
                contract_id,
                client=self._client,
                cursor=_value(cursor),
                limit=_value(limit),
                network=_enum(ListContractEventsNetwork, network),
                type_=_value(type),
                from_=_value(from_ledger),
                to=_value(to_ledger),
            )
        )

    async def stream(self, contract_id: str) -> StreamContractEventsResponse200:
        return _unwrap(
            await stream_contract_events.asyncio_detailed(contract_id, client=self._client)
        )

    # --- issue #556 facade wiring: global event feeds ---------------------- #
    async def recent(self, *, limit: int | None = None) -> Any:
        return _unwrap(await recent_events.asyncio_detailed(client=self._client, limit=_value(limit)))

    async def list_all(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        contract_id: str | None = None,
        type: str | None = None,
        network: str | None = None,
    ) -> Any:
        return _unwrap(
            await list_all_events.asyncio_detailed(
                client=self._client,
                cursor=_value(cursor),
                limit=_value(limit),
                contract_id=_value(contract_id),
                type_=_enum(ListAllEventsType, type),
                network=_enum(ListAllEventsNetwork, network),
            )
        )


class _AsyncInvocations(_AsyncResource):
    async def list(
        self,
        contract_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        network: str | None = None,
        status: str | None = None,
        fn: str | None = None,
        from_ledger: int | None = None,
        to_ledger: int | None = None,
    ) -> ListContractInvocationsResponse200:
        return _unwrap(
            await list_contract_invocations.asyncio_detailed(
                contract_id,
                client=self._client,
                cursor=_value(cursor),
                limit=_value(limit),
                network=_enum(ListContractInvocationsNetwork, network),
                status=_enum(ListContractInvocationsStatus, status),
                fn=_value(fn),
                from_=_value(from_ledger),
                to=_value(to_ledger),
            )
        )

    # --- issue #556 facade wiring: global invocation feed + trace ---------- #
    async def list_all(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        contract_id: str | None = None,
        fn: str | None = None,
        status: str | None = None,
        network: str | None = None,
    ) -> Any:
        return _unwrap(
            await list_all_invocations.asyncio_detailed(
                client=self._client,
                cursor=_value(cursor),
                limit=_value(limit),
                contract_id=_value(contract_id),
                fn=_value(fn),
                status=_enum(ListAllInvocationsStatus, status),
                network=_enum(ListAllInvocationsNetwork, network),
            )
        )

    async def trace(self, tx_hash: str) -> Any:
        return _unwrap(await get_invocation_trace.asyncio_detailed(tx_hash, client=self._client))


class _AsyncStorage(_AsyncResource):
    async def list(
        self,
        contract_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        network: str | None = None,
        durability: str | None = None,
        status: str | None = None,
    ) -> ListContractStorageResponse200:
        return _unwrap(
            await list_contract_storage.asyncio_detailed(
                contract_id,
                client=self._client,
                cursor=_value(cursor),
                limit=_value(limit),
                network=_enum(ListContractStorageNetwork, network),
                durability=_enum(ListContractStorageDurability, durability),
                status=_enum(ListContractStorageStatus, status),
            )
        )


class _AsyncForecast(_AsyncResource):
    async def get(
        self, contract_id: str, *, horizon: int | None = None
    ) -> GetContractForecastResponse200:
        return _unwrap(
            await get_contract_forecast.asyncio_detailed(
                contract_id, client=self._client, horizon=_value(horizon)
            )
        )


class _AsyncSnapshots(_AsyncResource):
    async def get(self, contract_id: str, *, ledger: int) -> ContractSnapshot:
        return _unwrap(
            await get_contract_snapshot.asyncio_detailed(
                contract_id, client=self._client, ledger=ledger
            )
        )


class _AsyncApiKeys(_AsyncResource):
    async def list(
        self, *, cursor: str | None = None, limit: int | None = None
    ) -> ListApiKeysResponse200:
        return _unwrap(
            await list_api_keys.asyncio_detailed(
                client=self._client, cursor=_value(cursor), limit=_value(limit)
            )
        )

    async def create(self, name: str, scopes: list[str]) -> Any:
        body = CreateApiKeyBody(
            name=name, scopes=[CreateApiKeyBodyScopesItem(scope) for scope in scopes]
        )
        return _unwrap(await create_api_key.asyncio_detailed(client=self._client, body=body))

    async def revoke(self, key_id: str) -> None:
        _unwrap(await revoke_api_key.asyncio_detailed(key_id, client=self._client))

    async def get(self, key_id: str) -> Any:
        return _unwrap(await get_api_key.asyncio_detailed(key_id, client=self._client))

    async def rotate(self, key_id: str) -> Any:
        """Rotates a key; the new plaintext token is returned once."""
        return _unwrap(await rotate_api_key.asyncio_detailed(key_id, client=self._client))

    async def list_admin(
        self, *, cursor: str | None = None, limit: int | None = None
    ) -> ListApiKeysResponse200:
        return _unwrap(
            await list_api_keys_admin.asyncio_detailed(
                client=self._client, cursor=_value(cursor), limit=_value(limit)
            )
        )

    async def create_admin(self, name: str, scopes: list[str]) -> Any:
        body = CreateApiKeyAdminBody(name=name, scopes=list(scopes))
        return _unwrap(await create_api_key_admin.asyncio_detailed(client=self._client, body=body))

    async def revoke_admin(self, key_id: str) -> None:
        _unwrap(await revoke_api_key_admin.asyncio_detailed(key_id, client=self._client))


class _AsyncWatchlist(_AsyncResource):
    async def list(self, user_id: str) -> Watchlist:
        return _unwrap(
            await list_watchlist.asyncio_detailed(client=self._client, x_user_id=user_id)
        )

    async def add(self, user_id: str, contract_id: str) -> InWatchlist:
        body = AddToWatchlistBody(contract_id=contract_id)
        return _unwrap(
            await add_to_watchlist.asyncio_detailed(
                client=self._client, body=body, x_user_id=user_id
            )
        )

    async def remove(self, user_id: str, contract_id: str) -> InWatchlist:
        return _unwrap(
            await remove_from_watchlist.asyncio_detailed(
                contract_id, client=self._client, x_user_id=user_id
            )
        )

    async def status(self, user_id: str, contract_id: str) -> InWatchlist:
        return _unwrap(
            await get_watchlist_status.asyncio_detailed(
                contract_id, client=self._client, x_user_id=user_id
            )
        )


class _AsyncWatchdog(_AsyncResource):
    async def stats(self, *, network: str | None = None) -> WatchdogStats:
        return _unwrap(
            await get_watchdog_stats.asyncio_detailed(
                client=self._client, network=_enum(GetWatchdogStatsNetwork, network)
            )
        )

    async def alerts(
        self,
        *,
        severity: str | None = None,
        network: str | None = None,
        limit: int | None = None,
    ) -> ListWatchdogAlertsResponse200:
        return _unwrap(
            await list_watchdog_alerts.asyncio_detailed(
                client=self._client,
                severity=_enum(ListWatchdogAlertsSeverity, severity),
                network=_enum(ListWatchdogAlertsNetwork, network),
                limit=_value(limit),
            )
        )

    async def contracts(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        network: str | None = None,
    ) -> ListMonitoredContractsResponse200:
        return _unwrap(
            await list_monitored_contracts.asyncio_detailed(
                client=self._client,
                cursor=_value(cursor),
                limit=_value(limit),
                network=_enum(ListMonitoredContractsNetwork, network),
            )
        )

    async def contract(self, contract_id: str) -> MonitoredContract:
        return _unwrap(
            await get_monitored_contract.asyncio_detailed(contract_id, client=self._client)
        )

    async def health(
        self, contract_id: str, *, limit: int | None = None
    ) -> ListContractHealthChecksResponse200:
        return _unwrap(
            await list_contract_health_checks.asyncio_detailed(
                contract_id, client=self._client, limit=_value(limit)
            )
        )

    async def alerts_for(
        self,
        contract_id: str,
        *,
        severity: str | None = None,
        network: str | None = None,
        limit: int | None = None,
    ) -> ListContractAlertsResponse200:
        return _unwrap(
            await list_contract_alerts.asyncio_detailed(
                contract_id,
                client=self._client,
                severity=_enum(ListContractAlertsSeverity, severity),
                network=_enum(ListContractAlertsNetwork, network),
                limit=_value(limit),
            )
        )

    # --- issue #556 facade wiring: uptime + notification subscriptions ----- #
    async def uptime(self, contract_id: str) -> Any:
        return _unwrap(await get_contract_uptime.asyncio_detailed(contract_id, client=self._client))

    async def create_subscription(self, body: CreateAlertSubscription) -> Any:
        return _unwrap(
            await create_alert_subscription.asyncio_detailed(client=self._client, body=body)
        )

    async def list_subscriptions(self) -> Any:
        return _unwrap(await list_alert_subscriptions.asyncio_detailed(client=self._client))

    async def delete_subscription(self, subscription_id: str) -> None:
        _unwrap(await delete_alert_subscription.asyncio_detailed(subscription_id, client=self._client))


class _AsyncAlerts(_AsyncResource):
    """Cross-contract alert feed (``/api/v1/alerts``, issue #556)."""

    async def list(
        self,
        *,
        flat: bool | None = None,
        contract_id: str | None = None,
        severity: str | None = None,
        network: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> ListAlertsResponse200:
        return _unwrap(
            await list_alerts.asyncio_detailed(
                client=self._client,
                flat=_value(flat),
                contract_id=_value(contract_id),
                severity=_enum(ListAlertsSeverity, severity),
                network=_enum(ListAlertsNetwork, network),
                cursor=_value(cursor),
                limit=_value(limit),
            )
        )


class _AsyncReports(_AsyncResource):
    """SLA reports and email digest subscriptions (issue #556)."""

    async def get(
        self, contract_id: str, *, month: str | None = None
    ) -> ContractReport:
        return _unwrap(
            await get_contract_report.asyncio_detailed(
                contract_id, client=self._client, month=_value(month)
            )
        )

    async def history(
        self, contract_id: str, *, months: int | None = None
    ) -> GetContractReportHistoryResponse200:
        return _unwrap(
            await get_contract_report_history.asyncio_detailed(
                contract_id, client=self._client, months=_value(months)
            )
        )

    async def subscribe(
        self, email: str, frequency: str, *, day_of_week: int | None = None
    ) -> ReportSubscription:
        body = CreateReportSubscriptionBody(
            email=email,
            frequency=CreateReportSubscriptionBodyFrequency(frequency),
            day_of_week=_value(day_of_week),
        )
        return _unwrap(
            await create_report_subscription.asyncio_detailed(client=self._client, body=body)
        )

    async def subscriptions(self, email: str) -> ListReportSubscriptionsResponse200:
        return _unwrap(
            await list_report_subscriptions.asyncio_detailed(client=self._client, email=email)
        )

    async def unsubscribe(self, subscription_id: str) -> None:
        _unwrap(await delete_report_subscription.asyncio_detailed(subscription_id, client=self._client))


class _AsyncRules(_AsyncResource):
    """Declarative alert-rule management (``/api/v1/rules*``, issue #556)."""

    async def create(self, body: CreateAlertRuleBody) -> Any:
        return _unwrap(await create_alert_rule.asyncio_detailed(client=self._client, body=body))

    async def list(self) -> Any:
        return _unwrap(await list_alert_rules.asyncio_detailed(client=self._client))

    async def delete(self, rule_id: int) -> None:
        _unwrap(await delete_alert_rule.asyncio_detailed(rule_id, client=self._client))

    async def set_enabled(self, rule_id: int, body: SetAlertRuleEnabledBody) -> Any:
        return _unwrap(
            await set_alert_rule_enabled.asyncio_detailed(rule_id, client=self._client, body=body)
        )

    async def preview(self, body: PreviewAlertRuleBody) -> Any:
        return _unwrap(await preview_alert_rule.asyncio_detailed(client=self._client, body=body))

    async def validate(self, body: ValidateAlertRuleBody) -> Any:
        return _unwrap(await validate_alert_rule.asyncio_detailed(client=self._client, body=body))

    async def library(self) -> Any:
        return _unwrap(await list_rule_library.asyncio_detailed(client=self._client))

    async def metrics(self) -> Any:
        return _unwrap(await list_rule_metrics.asyncio_detailed(client=self._client))


class _AsyncGroups(_AsyncResource):
    """Contract groups (``/api/v1/groups*``); each call passes the owner user id."""

    async def create(self, user_id: str, body: CreateGroupBody) -> Any:
        return _unwrap(
            await create_group.asyncio_detailed(
                client=self._client, body=body, x_user_id=user_id
            )
        )

    async def list(self, user_id: str) -> Any:
        return _unwrap(await list_groups.asyncio_detailed(client=self._client, x_user_id=user_id))

    async def get(self, group_id: str, user_id: str) -> Any:
        return _unwrap(
            await get_group.asyncio_detailed(group_id, client=self._client, x_user_id=user_id)
        )

    async def update(self, group_id: str, user_id: str, body: UpdateGroupBody) -> Any:
        return _unwrap(
            await update_group.asyncio_detailed(
                group_id, client=self._client, body=body, x_user_id=user_id
            )
        )

    async def delete(self, group_id: str, user_id: str) -> None:
        _unwrap(
            await delete_group.asyncio_detailed(group_id, client=self._client, x_user_id=user_id)
        )

    async def stats(self, group_id: str, user_id: str) -> Any:
        return _unwrap(
            await get_group_stats.asyncio_detailed(group_id, client=self._client, x_user_id=user_id)
        )

    async def add_contract(self, group_id: str, user_id: str, body: AddGroupContractBody) -> Any:
        return _unwrap(
            await add_group_contract.asyncio_detailed(
                group_id, client=self._client, body=body, x_user_id=user_id
            )
        )

    async def remove_contract(
        self, group_id: str, user_id: str, body: RemoveGroupContractBody
    ) -> Any:
        return _unwrap(
            await remove_group_contract.asyncio_detailed(
                group_id, client=self._client, body=body, x_user_id=user_id
            )
        )

    async def remove_contract_by_path(self, group_id: str, contract_id: str, user_id: str) -> Any:
        return _unwrap(
            await remove_group_contract_by_path.asyncio_detailed(
                group_id, contract_id, client=self._client, x_user_id=user_id
            )
        )


class _AsyncNotes(_AsyncResource):
    """Per-contract analyst notes (``/api/v1/contracts/{id}/notes``)."""

    async def list(self, contract_id: str) -> Any:
        return _unwrap(await list_contract_notes.asyncio_detailed(contract_id, client=self._client))

    async def create(self, contract_id: str, body: ContractNoteRequest) -> Any:
        return _unwrap(
            await create_contract_note.asyncio_detailed(
                contract_id, client=self._client, body=body
            )
        )

    async def update(self, contract_id: str, note_id: str, body: ContractNoteRequest) -> Any:
        return _unwrap(
            await update_contract_note.asyncio_detailed(
                contract_id, note_id, client=self._client, body=body
            )
        )

    async def delete(self, contract_id: str, note_id: str) -> None:
        _unwrap(
            await delete_contract_note.asyncio_detailed(
                contract_id, note_id, client=self._client
            )
        )


class _AsyncWatchedAccounts(_AsyncResource):
    """Liquidity-pool watched accounts (``/api/v1/watched-accounts``)."""

    async def list(self) -> Any:
        return _unwrap(await list_watched_accounts.asyncio_detailed(client=self._client))

    async def add(self, body: AddWatchedAccountBody) -> Any:
        return _unwrap(await add_watched_account.asyncio_detailed(client=self._client, body=body))

    async def delete(self, account_id: str) -> None:
        _unwrap(await delete_watched_account.asyncio_detailed(account_id, client=self._client))


class _AsyncAudit(_AsyncResource):
    """Admin audit trail feed (``GET /api/v1/admin/audit``)."""

    async def list_events(
        self, *, since: Any = None, limit: int | None = None, cursor: str | None = None
    ) -> Any:
        return _unwrap(
            await list_audit_events.asyncio_detailed(
                client=self._client,
                since=_value(since),
                limit=_value(limit),
                cursor=_value(cursor),
            )
        )


class AsyncClient:
    """Asynchronous (``httpx.AsyncClient``) client for the Sorolens API.

    Usage::

        from sorolens import AsyncClient

        async with AsyncClient(api_key="sk_...") as client:
            page = await client.contracts.list(limit=10)
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: Any = None,
        headers: dict[str, str] | None = None,
        **httpx_args: Any,
    ) -> None:
        self._client = _build_client(
            api_key=api_key, base_url=base_url, timeout=timeout, headers=headers, **httpx_args
        )
        self.health = _AsyncHealth(self)
        self.stats = _AsyncStats(self)
        self.contracts = _AsyncContracts(self)
        self.events = _AsyncEvents(self)
        self.invocations = _AsyncInvocations(self)
        self.storage = _AsyncStorage(self)
        self.forecast = _AsyncForecast(self)
        self.snapshots = _AsyncSnapshots(self)
        self.api_keys = _AsyncApiKeys(self)
        self.watchlist = _AsyncWatchlist(self)
        self.watchdog = _AsyncWatchdog(self)
        self.alerts = _AsyncAlerts(self)
        self.reports = _AsyncReports(self)
        self.rules = _AsyncRules(self)
        self.groups = _AsyncGroups(self)
        self.notes = _AsyncNotes(self)
        self.watched_accounts = _AsyncWatchedAccounts(self)
        self.audit = _AsyncAudit(self)

    async def search(
        self, q: str, *, limit: int | None = None
    ) -> GetApiV1SearchResponse200:
        """Full-text contract search on ``GET /api/v1/search`` (issue #556)."""
        return _unwrap(
            await get_api_v1_search.asyncio_detailed(
                client=self._client, q=q, limit=_value(limit)
            )
        )

    async def close(self) -> None:
        await self._client.get_async_httpx_client().aclose()

    async def __aenter__(self) -> AsyncClient:
        await self._client.get_async_httpx_client().__aenter__()
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        await self._client.get_async_httpx_client().__aexit__(*exc_info)
