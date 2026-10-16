//! SLA reports and email digest subscriptions.
//!
//! Covers the `Reports` tag of `docs/openapi.yaml`
//! (`/api/v1/reports/...`). The `badge.svg` and one-click `unsubscribe`
//! endpoints answer non-JSON payloads and are intentionally not exposed on
//! the SDK transport (see `scripts/sdk-coverage-allowlist.json`).

use serde_json::Value;

use crate::client::ClientConfig;
use crate::error::Error;
use crate::macros::endpoints;
use crate::request::{contract_id, encode_path_segment, RequestSpec};
use crate::types::CreateReportSubscriptionRequest;

/// Parameters for [`crate::Client::get_contract_report`].
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct GetContractReportParams {
    /// Report month as `YYYY-MM` (defaults to the current month).
    pub month: Option<String>,
}

impl GetContractReportParams {
    /// Selects the report month (`YYYY-MM`).
    pub fn month(mut self, month: impl Into<String>) -> Self {
        self.month = Some(month.into());
        self
    }
}

/// Parameters for [`crate::Client::get_contract_report_history`].
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct GetContractReportHistoryParams {
    /// Maximum months to return (`1..=24`, default 6).
    pub limit: Option<u32>,
}

impl GetContractReportHistoryParams {
    /// Sets the maximum number of months.
    pub fn limit(mut self, limit: u32) -> Self {
        self.limit = Some(limit);
        self
    }
}

pub(crate) fn report_request(
    _config: &ClientConfig,
    id: &str,
    params: &GetContractReportParams,
) -> Result<RequestSpec, Error> {
    Ok(
        RequestSpec::get(format!("/api/v1/reports/{}", contract_id(id)?))
            .query_opt("month", params.month.as_deref()),
    )
}

pub(crate) fn history_request(
    _config: &ClientConfig,
    id: &str,
    params: &GetContractReportHistoryParams,
) -> Result<RequestSpec, Error> {
    Ok(
        RequestSpec::get(format!(
            "/api/v1/reports/{}/history",
            contract_id(id)?
        ))
        .query_opt("limit", params.limit),
    )
}

pub(crate) fn create_subscription_request(
    _config: &ClientConfig,
    request: &CreateReportSubscriptionRequest,
) -> Result<RequestSpec, Error> {
    RequestSpec::post("/api/v1/reports/subscriptions", request)
}

pub(crate) fn list_subscriptions_request(
    _config: &ClientConfig,
    email: &str,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get("/api/v1/reports/subscriptions")
        .query_opt("email", Some(email.trim())))
}

pub(crate) fn delete_subscription_request(
    _config: &ClientConfig,
    id: &str,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::delete(format!(
        "/api/v1/reports/subscriptions/{}",
        encode_path_segment(id.trim())
    )))
}

endpoints! {
    /// Monthly SLA/uptime report for a contract (JSON format).
    ///
    /// `GET /api/v1/reports/{contract_id}`.
    fn get_contract_report(id: &str, params: &GetContractReportParams) -> Value =
        report_request;

    /// Recent monthly report history for a contract.
    ///
    /// `GET /api/v1/reports/{contract_id}/history`.
    fn get_contract_report_history(
        id: &str,
        params: &GetContractReportHistoryParams,
    ) -> Value = history_request;

    /// Subscribes an email address to the daily/weekly digest.
    ///
    /// `POST /api/v1/reports/subscriptions`.
    fn create_report_subscription(
        request: &CreateReportSubscriptionRequest
    ) -> Value = create_subscription_request;

    /// Lists a subscriber's digest subscriptions.
    ///
    /// `GET /api/v1/reports/subscriptions?email=...`.
    fn list_report_subscriptions(email: &str) -> Value = list_subscriptions_request;

    /// Deletes a digest subscription. Returns `()` on success (HTTP 204).
    ///
    /// `DELETE /api/v1/reports/subscriptions/{id}`.
    fn delete_report_subscription(id: &str) -> () = delete_subscription_request;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn report_request_passes_the_month_through() {
        let config = ClientConfig::default();
        let params = GetContractReportParams::default().month("2026-01");
        let spec = report_request(&config, "CABC", &params).unwrap();
        assert_eq!(spec.path, "/api/v1/reports/CABC");
        assert_eq!(
            spec.query,
            vec![("month".to_string(), "2026-01".to_string())]
        );
    }

    #[test]
    fn history_request_under_the_reports_path() {
        let config = ClientConfig::default();
        let spec = history_request(
            &config,
            "CABC",
            &GetContractReportHistoryParams::default().limit(12),
        )
        .unwrap();
        assert_eq!(spec.path, "/api/v1/reports/CABC/history");
        assert_eq!(spec.query, vec![("limit".to_string(), "12".to_string())]);
    }

    #[test]
    fn subscription_requests() {
        let config = ClientConfig::default();
        let request =
            CreateReportSubscriptionRequest::new("ops@example.com", "weekly").day_of_week(3);
        let spec = create_subscription_request(&config, &request).unwrap();
        assert_eq!(spec.path, "/api/v1/reports/subscriptions");
        let body = spec.body.unwrap();
        assert_eq!(body["email"], "ops@example.com");
        assert_eq!(body["day_of_week"], 3);

        let spec = list_subscriptions_request(&config, "ops@example.com").unwrap();
        assert_eq!(
            spec.query,
            vec![("email".to_string(), "ops@example.com".to_string())]
        );

        let spec = delete_subscription_request(&config, "sub1").unwrap();
        assert_eq!(spec.path, "/api/v1/reports/subscriptions/sub1");
        assert_eq!(spec.method, crate::request::HttpMethod::Delete);
    }
}
