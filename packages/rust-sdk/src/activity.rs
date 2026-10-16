//! Cross-contract activity feeds: global event/invocation listings, recent
//! events, live activity, invocation traces and the admin audit trail.
//!
//! Covers the global `Events`, `Invocations`, `Stats` and audit endpoints of
//! `docs/openapi.yaml` (`/api/v1/events`, `/api/v1/invocations`,
//! `/api/v1/stats/activity`, `/api/v1/admin/audit`). Per-contract variants
//! live in [`crate::events`] and [`crate::invocations`].

use serde_json::Value;

use crate::client::ClientConfig;
use crate::error::Error;
use crate::macros::endpoints;
use crate::request::{encode_path_segment, RequestSpec};

/// Filters for [`crate::Client::list_all_events`].
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ListAllEventsParams {
    /// Opaque cursor from a previous page.
    pub cursor: Option<String>,
    /// Maximum results per page.
    pub limit: Option<u32>,
    /// Filter by contract ID.
    pub contract_id: Option<String>,
    /// Event type filter (e.g. `transfer`).
    pub event_type: Option<String>,
    /// Only events at or after this ISO-8601 timestamp.
    pub since: Option<String>,
    /// Only events at or before this ISO-8601 timestamp.
    pub until: Option<String>,
}

impl ListAllEventsParams {
    /// Sets the pagination cursor.
    pub fn cursor(mut self, cursor: impl Into<String>) -> Self {
        self.cursor = Some(cursor.into());
        self
    }

    /// Sets the page size.
    pub fn limit(mut self, limit: u32) -> Self {
        self.limit = Some(limit);
        self
    }

    /// Filters by contract ID.
    pub fn contract_id(mut self, contract_id: impl Into<String>) -> Self {
        self.contract_id = Some(contract_id.into());
        self
    }

    /// Filters by event type.
    pub fn event_type(mut self, event_type: impl Into<String>) -> Self {
        self.event_type = Some(event_type.into());
        self
    }

    /// Restricts to events at or after this ISO-8601 timestamp.
    pub fn since(mut self, since: impl Into<String>) -> Self {
        self.since = Some(since.into());
        self
    }

    /// Restricts to events at or before this ISO-8601 timestamp.
    pub fn until(mut self, until: impl Into<String>) -> Self {
        self.until = Some(until.into());
        self
    }
}

/// Filters for [`crate::Client::list_all_invocations`].
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ListAllInvocationsParams {
    /// Opaque cursor from a previous page.
    pub cursor: Option<String>,
    /// Maximum results per page.
    pub limit: Option<u32>,
    /// Filter by contract ID.
    pub contract_id: Option<String>,
    /// Filter by invoked function name.
    pub function: Option<String>,
    /// Filter by invocation status (`success` / `error`).
    pub status: Option<String>,
    /// Only invocations at or after this ISO-8601 timestamp.
    pub since: Option<String>,
    /// Only invocations at or before this ISO-8601 timestamp.
    pub until: Option<String>,
}

impl ListAllInvocationsParams {
    /// Sets the pagination cursor.
    pub fn cursor(mut self, cursor: impl Into<String>) -> Self {
        self.cursor = Some(cursor.into());
        self
    }

    /// Sets the page size.
    pub fn limit(mut self, limit: u32) -> Self {
        self.limit = Some(limit);
        self
    }

    /// Filters by contract ID.
    pub fn contract_id(mut self, contract_id: impl Into<String>) -> Self {
        self.contract_id = Some(contract_id.into());
        self
    }

    /// Filters by invoked function name.
    pub fn function(mut self, function: impl Into<String>) -> Self {
        self.function = Some(function.into());
        self
    }

    /// Filters by invocation status.
    pub fn status(mut self, status: impl Into<String>) -> Self {
        self.status = Some(status.into());
        self
    }

    /// Restricts to invocations at or after this ISO-8601 timestamp.
    pub fn since(mut self, since: impl Into<String>) -> Self {
        self.since = Some(since.into());
        self
    }

    /// Restricts to invocations at or before this ISO-8601 timestamp.
    pub fn until(mut self, until: impl Into<String>) -> Self {
        self.until = Some(until.into());
        self
    }
}

/// Filters for [`crate::Client::list_audit_events`].
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ListAuditEventsParams {
    /// Only entries at or after this ISO-8601 timestamp.
    pub since: Option<String>,
    /// Opaque cursor from a previous page.
    pub cursor: Option<String>,
    /// Maximum results per page.
    pub limit: Option<u32>,
}

impl ListAuditEventsParams {
    /// Restricts to entries at or after this ISO-8601 timestamp.
    pub fn since(mut self, since: impl Into<String>) -> Self {
        self.since = Some(since.into());
        self
    }

    /// Sets the pagination cursor.
    pub fn cursor(mut self, cursor: impl Into<String>) -> Self {
        self.cursor = Some(cursor.into());
        self
    }

    /// Sets the page size.
    pub fn limit(mut self, limit: u32) -> Self {
        self.limit = Some(limit);
        self
    }
}

pub(crate) fn list_all_events_request(
    _config: &ClientConfig,
    params: &ListAllEventsParams,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get("/api/v1/events")
        .query_opt("cursor", params.cursor.as_deref())
        .query_opt("limit", params.limit)
        .query_opt("contract_id", params.contract_id.as_deref())
        .query_opt("type", params.event_type.as_deref())
        .query_opt("since", params.since.as_deref())
        .query_opt("until", params.until.as_deref()))
}

pub(crate) fn recent_events_request(
    _config: &ClientConfig,
    limit: Option<u32>,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get("/api/v1/events/recent").query_opt("limit", limit))
}

pub(crate) fn list_all_invocations_request(
    _config: &ClientConfig,
    params: &ListAllInvocationsParams,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get("/api/v1/invocations")
        .query_opt("cursor", params.cursor.as_deref())
        .query_opt("limit", params.limit)
        .query_opt("contract_id", params.contract_id.as_deref())
        .query_opt("fn", params.function.as_deref())
        .query_opt("status", params.status.as_deref())
        .query_opt("since", params.since.as_deref())
        .query_opt("until", params.until.as_deref()))
}

pub(crate) fn invocation_trace_request(
    _config: &ClientConfig,
    tx_hash: &str,
) -> Result<RequestSpec, Error> {
    let tx_hash = tx_hash.trim();
    if tx_hash.is_empty() {
        return Err(Error::InvalidRequest(
            "transaction hash must not be empty".into(),
        ));
    }
    Ok(RequestSpec::get(format!(
        "/api/v1/invocations/{}/trace",
        encode_path_segment(tx_hash)
    )))
}

pub(crate) fn live_activity_request(
    _config: &ClientConfig,
    minutes: Option<u32>,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get("/api/v1/stats/activity").query_opt("minutes", minutes))
}

pub(crate) fn list_audit_events_request(
    _config: &ClientConfig,
    params: &ListAuditEventsParams,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get("/api/v1/admin/audit")
        .query_opt("since", params.since.as_deref())
        .query_opt("cursor", params.cursor.as_deref())
        .query_opt("limit", params.limit))
}

pub(crate) fn contract_uptime_request(
    _config: &ClientConfig,
    id: &str,
    window: Option<&str>,
) -> Result<RequestSpec, Error> {
    let id = id.trim();
    if id.is_empty() {
        return Err(Error::InvalidRequest(
            "watchdog contract id must not be empty".into(),
        ));
    }
    Ok(
        RequestSpec::get(format!(
            "/api/v1/watchdog/contracts/{}/uptime",
            encode_path_segment(id)
        ))
        .query_opt("window", window.map(str::trim).filter(|w| !w.is_empty())),
    )
}

endpoints! {
    /// Lists events across all indexed contracts.
    ///
    /// `GET /api/v1/events`.
    fn list_all_events(params: &ListAllEventsParams) -> Value = list_all_events_request;

    /// The most recent events across all contracts.
    ///
    /// `GET /api/v1/events/recent`.
    fn recent_events(limit: Option<u32>) -> Value = recent_events_request;

    /// Lists invocations across all indexed contracts.
    ///
    /// `GET /api/v1/invocations`.
    fn list_all_invocations(params: &ListAllInvocationsParams) -> Value =
        list_all_invocations_request;

    /// Execution trace for one transaction hash.
    ///
    /// `GET /api/v1/invocations/{tx_hash}/trace`.
    fn get_invocation_trace(tx_hash: &str) -> Value = invocation_trace_request;

    /// Network-wide live activity for the activity dashboard.
    ///
    /// `GET /api/v1/stats/activity`.
    fn live_activity(minutes: Option<u32>) -> Value = live_activity_request;

    /// Uptime series for a watchdog-monitored contract.
    ///
    /// `GET /api/v1/watchdog/contracts/{id}/uptime`.
    fn get_contract_uptime(id: &str, window: Option<&str>) -> Value = contract_uptime_request;

    /// The admin audit trail for the caller's account.
    ///
    /// `GET /api/v1/admin/audit`.
    fn list_audit_events(params: &ListAuditEventsParams) -> Value = list_audit_events_request;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn list_all_events_encodes_filters() {
        let config = ClientConfig::default();
        let params = ListAllEventsParams::default()
            .contract_id("CABC")
            .event_type("transfer")
            .limit(25);
        let spec = list_all_events_request(&config, &params).unwrap();
        assert_eq!(spec.path, "/api/v1/events");
        assert_eq!(
            spec.query,
            vec![
                ("limit".to_string(), "25".to_string()),
                ("contract_id".to_string(), "CABC".to_string()),
                ("type".to_string(), "transfer".to_string()),
            ]
        );
    }

    #[test]
    fn invocation_and_trace_requests() {
        let config = ClientConfig::default();
        let params = ListAllInvocationsParams::default().function("transfer").status("success");
        let spec = list_all_invocations_request(&config, &params).unwrap();
        assert_eq!(spec.path, "/api/v1/invocations");
        assert_eq!(
            spec.query,
            vec![
                ("fn".to_string(), "transfer".to_string()),
                ("status".to_string(), "success".to_string()),
            ]
        );

        assert_eq!(
            invocation_trace_request(&config, "abc123").unwrap().path,
            "/api/v1/invocations/abc123/trace"
        );
        assert!(matches!(
            invocation_trace_request(&config, " "),
            Err(Error::InvalidRequest(_))
        ));
    }

    #[test]
    fn activity_audit_and_uptime_requests() {
        let config = ClientConfig::default();
        let spec = live_activity_request(&config, Some(30)).unwrap();
        assert_eq!(spec.path, "/api/v1/stats/activity");
        assert_eq!(spec.query, vec![("minutes".to_string(), "30".to_string())]);

        let spec = list_audit_events_request(
            &config,
            &ListAuditEventsParams::default().since("2026-01-01T00:00:00Z"),
        )
        .unwrap();
        assert_eq!(spec.path, "/api/v1/admin/audit");

        let spec = contract_uptime_request(&config, "C1", Some("7d")).unwrap();
        assert_eq!(spec.path, "/api/v1/watchdog/contracts/C1/uptime");
        assert_eq!(spec.query, vec![("window".to_string(), "7d".to_string())]);
    }
}
