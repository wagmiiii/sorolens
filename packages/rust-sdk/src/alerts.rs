//! Alert feed: the deduplicated alert-group view over fired alerts.
//!
//! Covers the `Alerts` tag of `docs/openapi.yaml` (`/api/v1/alerts`). Per
//! contract alert history lives in [`crate::watchdog`].

use serde_json::Value;

use crate::client::ClientConfig;
use crate::error::Error;
use crate::macros::endpoints;
use crate::request::RequestSpec;
use crate::types::{Network, Severity};

/// Filters for [`crate::Client::list_alerts`].
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ListAlertsParams {
    /// Return the raw per-event alert feed instead of grouped alerts.
    pub flat: Option<bool>,
    /// Filter by contract ID.
    pub contract_id: Option<String>,
    /// Severity filter.
    pub severity: Option<Severity>,
    /// Restrict to one network.
    pub network: Option<Network>,
    /// Opaque cursor from a previous page.
    pub cursor: Option<String>,
    /// Maximum results (`1..=500`, default 100).
    pub limit: Option<u32>,
}

impl ListAlertsParams {
    /// Requests the raw (ungrouped) alert feed.
    pub fn flat(mut self, flat: bool) -> Self {
        self.flat = Some(flat);
        self
    }

    /// Filters by contract ID.
    pub fn contract_id(mut self, contract_id: impl Into<String>) -> Self {
        self.contract_id = Some(contract_id.into());
        self
    }

    /// Filters by severity.
    pub fn severity(mut self, severity: Severity) -> Self {
        self.severity = Some(severity);
        self
    }

    /// Restricts the page to one network.
    pub fn network(mut self, network: Network) -> Self {
        self.network = Some(network);
        self
    }

    /// Sets the pagination cursor.
    pub fn cursor(mut self, cursor: impl Into<String>) -> Self {
        self.cursor = Some(cursor.into());
        self
    }

    /// Sets the maximum number of alerts.
    pub fn limit(mut self, limit: u32) -> Self {
        self.limit = Some(limit);
        self
    }
}

pub(crate) fn alerts_request(
    _config: &ClientConfig,
    params: &ListAlertsParams,
) -> Result<RequestSpec, Error> {
    if let Some(limit) = params.limit {
        if !(1..=500).contains(&limit) {
            return Err(Error::InvalidRequest(format!(
                "alert limit must be between 1 and 500, got {limit}"
            )));
        }
    }
    Ok(RequestSpec::get("/api/v1/alerts")
        .query_opt("flat", params.flat)
        .query_opt("contract_id", params.contract_id.as_deref())
        .query_opt("severity", params.severity.map(Severity::as_str))
        .query_opt("network", params.network.map(Network::as_str))
        .query_opt("cursor", params.cursor.as_deref())
        .query_opt("limit", params.limit))
}

endpoints! {
    /// Lists fired alerts (grouped by default; raw feed with
    /// [`ListAlertsParams::flat`]).
    ///
    /// `GET /api/v1/alerts`.
    fn list_alerts(params: &ListAlertsParams) -> Value = alerts_request;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn alerts_request_encodes_filters() {
        let config = ClientConfig::default();
        let params = ListAlertsParams::default()
            .flat(true)
            .contract_id("CABC")
            .severity(Severity::Critical)
            .network(Network::Testnet)
            .limit(20);
        let spec = alerts_request(&config, &params).unwrap();
        assert_eq!(spec.path, "/api/v1/alerts");
        assert_eq!(
            spec.query,
            vec![
                ("flat".to_string(), "true".to_string()),
                ("contract_id".to_string(), "CABC".to_string()),
                ("severity".to_string(), "Critical".to_string()),
                ("network".to_string(), "testnet".to_string()),
                ("limit".to_string(), "20".to_string()),
            ]
        );
    }

    #[test]
    fn alerts_request_rejects_out_of_range_limits() {
        let config = ClientConfig::default();
        for limit in [0, 501] {
            assert!(matches!(
                alerts_request(&config, &ListAlertsParams::default().limit(limit)),
                Err(Error::InvalidRequest(_))
            ));
        }
    }
}
