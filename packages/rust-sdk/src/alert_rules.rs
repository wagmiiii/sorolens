//! Alert-rule management and alert subscriptions.
//!
//! Covers the `Alert Rules` tag of `docs/openapi.yaml` (`/api/v1/rules/...`)
//! and the watchdog alert subscriptions (`/api/v1/watchdog/subscriptions`).
//! Rule payloads are schema-dynamic (the shape depends on the rule type from
//! [`crate::Client::list_rule_library`]), so create/validate/preview calls
//! accept raw [`serde_json::Value`] bodies and return raw payloads.

use serde_json::{json, Value};

use crate::client::ClientConfig;
use crate::error::Error;
use crate::macros::endpoints;
use crate::request::{encode_path_segment, RequestSpec};

fn rule_id(id: &str) -> Result<String, Error> {
    let id = id.trim();
    if id.is_empty() {
        return Err(Error::InvalidRequest("rule id must not be empty".into()));
    }
    Ok(encode_path_segment(id))
}

pub(crate) fn list_rules_request(_config: &ClientConfig) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get("/api/v1/rules"))
}

pub(crate) fn create_rule_request(
    _config: &ClientConfig,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::post("/api/v1/rules", request)
}

pub(crate) fn validate_rule_request(
    _config: &ClientConfig,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::post("/api/v1/rules/validate", request)
}

pub(crate) fn preview_rule_request(
    _config: &ClientConfig,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::post("/api/v1/rules/preview", request)
}

pub(crate) fn rule_metrics_request(_config: &ClientConfig) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get("/api/v1/rules/metrics"))
}

pub(crate) fn rule_library_request(_config: &ClientConfig) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get("/api/v1/rules/library"))
}

pub(crate) fn set_rule_enabled_request(
    _config: &ClientConfig,
    id: &str,
    enabled: bool,
) -> Result<RequestSpec, Error> {
    RequestSpec::patch(format!("/api/v1/rules/{}", rule_id(id)?), &json!({ "enabled": enabled }))
}

pub(crate) fn delete_rule_request(_config: &ClientConfig, id: &str) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::delete(format!(
        "/api/v1/rules/{}",
        rule_id(id)?
    )))
}

pub(crate) fn list_subscriptions_request(_config: &ClientConfig) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get("/api/v1/watchdog/subscriptions"))
}

pub(crate) fn create_subscription_request(
    _config: &ClientConfig,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::post("/api/v1/watchdog/subscriptions", request)
}

pub(crate) fn delete_subscription_request(
    _config: &ClientConfig,
    id: &str,
) -> Result<RequestSpec, Error> {
    let id = id.trim();
    if id.is_empty() {
        return Err(Error::InvalidRequest(
            "subscription id must not be empty".into(),
        ));
    }
    Ok(RequestSpec::delete(format!(
        "/api/v1/watchdog/subscriptions/{}",
        encode_path_segment(id)
    )))
}

endpoints! {
    /// Lists the alert rules owned by the caller.
    ///
    /// `GET /api/v1/rules`.
    fn list_alert_rules() -> Value = list_rules_request;

    /// Creates an alert rule from its JSON definition.
    ///
    /// `POST /api/v1/rules`.
    fn create_alert_rule(request: &Value) -> Value = create_rule_request;

    /// Validates a rule definition without persisting it.
    ///
    /// `POST /api/v1/rules/validate`.
    fn validate_alert_rule(request: &Value) -> Value = validate_rule_request;

    /// Runs a rule against recent data as a dry run.
    ///
    /// `POST /api/v1/rules/preview`.
    fn preview_alert_rule(request: &Value) -> Value = preview_rule_request;

    /// Metrics (hit counts, fired alerts) for the caller's rules.
    ///
    /// `GET /api/v1/rules/metrics`.
    fn list_rule_metrics() -> Value = rule_metrics_request;

    /// The library of available rule types and their parameter schemas.
    ///
    /// `GET /api/v1/rules/library`.
    fn list_rule_library() -> Value = rule_library_request;

    /// Enables or disables an alert rule.
    ///
    /// `PATCH /api/v1/rules/{id}`.
    fn set_alert_rule_enabled(id: &str, enabled: bool) -> Value = set_rule_enabled_request;

    /// Deletes an alert rule. Returns `()` on success (HTTP 204).
    ///
    /// `DELETE /api/v1/rules/{id}`.
    fn delete_alert_rule(id: &str) -> () = delete_rule_request;

    /// Lists the caller's alert subscriptions (webhook/email targets).
    ///
    /// `GET /api/v1/watchdog/subscriptions`.
    fn list_alert_subscriptions() -> Value = list_subscriptions_request;

    /// Creates an alert subscription from its JSON definition.
    ///
    /// `POST /api/v1/watchdog/subscriptions`.
    fn create_alert_subscription(request: &Value) -> Value = create_subscription_request;

    /// Deletes an alert subscription. Returns `()` on success (HTTP 204).
    ///
    /// `DELETE /api/v1/watchdog/subscriptions/{id}`.
    fn delete_alert_subscription(id: &str) -> () = delete_subscription_request;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rule_requests_target_the_rules_api() {
        let config = ClientConfig::default();
        let spec = create_rule_request(&config, &json!({"type": "contract_paused"})).unwrap();
        assert_eq!(spec.path, "/api/v1/rules");
        assert_eq!(spec.body.unwrap()["type"], "contract_paused");

        let spec = validate_rule_request(&config, &json!({})).unwrap();
        assert_eq!(spec.path, "/api/v1/rules/validate");

        let spec = preview_rule_request(&config, &json!({})).unwrap();
        assert_eq!(spec.path, "/api/v1/rules/preview");

        assert_eq!(
            rule_metrics_request(&config).unwrap().path,
            "/api/v1/rules/metrics"
        );
        assert_eq!(
            rule_library_request(&config).unwrap().path,
            "/api/v1/rules/library"
        );
    }

    #[test]
    fn set_enabled_patches_the_rule() {
        let config = ClientConfig::default();
        let spec = set_rule_enabled_request(&config, "rule-1", true).unwrap();
        assert_eq!(spec.method, crate::request::HttpMethod::Patch);
        assert_eq!(spec.path, "/api/v1/rules/rule-1");
        assert_eq!(spec.body.unwrap()["enabled"], true);

        assert!(matches!(
            set_rule_enabled_request(&config, "  ", true),
            Err(Error::InvalidRequest(_))
        ));
    }

    #[test]
    fn subscription_requests() {
        let config = ClientConfig::default();
        let spec = create_subscription_request(&config, &json!({"url": "https://example.com"}))
            .unwrap();
        assert_eq!(spec.path, "/api/v1/watchdog/subscriptions");

        assert_eq!(
            list_subscriptions_request(&config).unwrap().path,
            "/api/v1/watchdog/subscriptions"
        );

        let spec = delete_subscription_request(&config, "sub/1").unwrap();
        assert_eq!(spec.path, "/api/v1/watchdog/subscriptions/sub%2F1");
        assert!(matches!(
            delete_subscription_request(&config, ""),
            Err(Error::InvalidRequest(_))
        ));
    }
}
