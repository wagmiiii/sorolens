//! Contract detail surfaces: batch lookup, comparison, enrichment, tags and
//! source verification.
//!
//! Covers the remaining `Contracts` tag endpoints of `docs/openapi.yaml`
//! (`/api/v1/contracts/batch`, `/api/v1/contracts/{id}/...`, `/api/v1/compare`).
//! These payloads are analytic or schema-dynamic and are returned as raw
//! [`serde_json::Value`].

use serde_json::Value;

use crate::client::ClientConfig;
use crate::error::Error;
use crate::macros::endpoints;
use crate::request::{contract_id, encode_path_segment, RequestSpec};

pub(crate) fn batch_contracts_request(
    _config: &ClientConfig,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::post("/api/v1/contracts/batch", request)
}

pub(crate) fn validate_contract_request(
    _config: &ClientConfig,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::post("/api/v1/contracts/validate", request)
}

pub(crate) fn compare_contracts_request(
    _config: &ClientConfig,
    ids: &str,
    window: Option<&str>,
) -> Result<RequestSpec, Error> {
    if ids.trim().is_empty() {
        return Err(Error::InvalidRequest(
            "compare requires at least one contract id".into(),
        ));
    }
    Ok(RequestSpec::get("/api/v1/compare")
        .query_opt("ids", Some(ids.trim()))
        .query_opt("window", window.map(str::trim).filter(|w| !w.is_empty())))
}

pub(crate) fn add_contract_tag_request(
    _config: &ClientConfig,
    id: &str,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::post(format!("/api/v1/contracts/{}/tags", contract_id(id)?), request)
}

pub(crate) fn remove_contract_tag_request(
    _config: &ClientConfig,
    id: &str,
    tag: &str,
) -> Result<RequestSpec, Error> {
    let tag = tag.trim();
    if tag.is_empty() {
        return Err(Error::InvalidRequest("tag must not be empty".into()));
    }
    Ok(RequestSpec::delete(format!(
        "/api/v1/contracts/{}/tags/{}",
        contract_id(id)?,
        encode_path_segment(tag)
    )))
}

pub(crate) fn contract_detail_request(
    _config: &ClientConfig,
    id: &str,
    suffix: &str,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get(format!(
        "/api/v1/contracts/{}/{}",
        contract_id(id)?,
        suffix
    )))
}

pub(crate) fn spec_request(config: &ClientConfig, id: &str) -> Result<RequestSpec, Error> {
    contract_detail_request(config, id, "spec")
}

pub(crate) fn summary_request(config: &ClientConfig, id: &str) -> Result<RequestSpec, Error> {
    contract_detail_request(config, id, "summary")
}

pub(crate) fn graph_request(config: &ClientConfig, id: &str) -> Result<RequestSpec, Error> {
    contract_detail_request(config, id, "graph")
}

pub(crate) fn health_score_request(config: &ClientConfig, id: &str) -> Result<RequestSpec, Error> {
    contract_detail_request(config, id, "health-score")
}

pub(crate) fn verification_request(config: &ClientConfig, id: &str) -> Result<RequestSpec, Error> {
    contract_detail_request(config, id, "verification")
}

pub(crate) fn list_contract_upgrades_request(
    _config: &ClientConfig,
    id: &str,
    limit: Option<u32>,
) -> Result<RequestSpec, Error> {
    Ok(
        RequestSpec::get(format!("/api/v1/contracts/{}/upgrades", contract_id(id)?))
            .query_opt("limit", limit),
    )
}

pub(crate) fn verify_contract_source_request(
    _config: &ClientConfig,
    id: &str,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::post(
        format!("/api/v1/contracts/{}/verify", contract_id(id)?),
        request,
    )
}

endpoints! {
    /// Fetches several contracts in one call.
    ///
    /// `POST /api/v1/contracts/batch`.
    fn batch_contracts(request: &Value) -> Value = batch_contracts_request;

    /// Validates a contract id/network without registering it.
    ///
    /// `POST /api/v1/contracts/validate`.
    fn validate_contract(request: &Value) -> Value = validate_contract_request;

    /// Compares analytics across contracts (`ids` is comma-separated).
    ///
    /// `GET /api/v1/compare`.
    fn compare_contracts(ids: &str, window: Option<&str>) -> Value = compare_contracts_request;

    /// Attaches a tag to a contract.
    ///
    /// `POST /api/v1/contracts/{id}/tags`.
    fn add_contract_tag(id: &str, request: &Value) -> Value = add_contract_tag_request;

    /// Removes a tag from a contract. Returns `()` on success (HTTP 204).
    ///
    /// `DELETE /api/v1/contracts/{id}/tags/{tag}`.
    fn remove_contract_tag(id: &str, tag: &str) -> () = remove_contract_tag_request;

    /// Full contract spec (methods, types, interfaces).
    ///
    /// `GET /api/v1/contracts/{id}/spec`.
    fn get_contract_spec(id: &str) -> Value = spec_request;

    /// Human-readable contract summary.
    ///
    /// `GET /api/v1/contracts/{id}/summary`.
    fn get_contract_summary(id: &str) -> Value = summary_request;

    /// Contract interaction graph (upstream/downstream calls).
    ///
    /// `GET /api/v1/contracts/{id}/graph`.
    fn get_contract_graph(id: &str) -> Value = graph_request;

    /// Composite health score for a contract.
    ///
    /// `GET /api/v1/contracts/{id}/health-score`.
    fn get_contract_health_score(id: &str) -> Value = health_score_request;

    /// Source-verification status for a contract.
    ///
    /// `GET /api/v1/contracts/{id}/verification`.
    fn get_contract_verification(id: &str) -> Value = verification_request;

    /// Deployed WASM upgrade history for a contract.
    ///
    /// `GET /api/v1/contracts/{id}/upgrades`.
    fn list_contract_upgrades(id: &str, limit: Option<u32>) -> Value =
        list_contract_upgrades_request;

    /// Requests source verification for a contract.
    ///
    /// `POST /api/v1/contracts/{id}/verify`.
    fn verify_contract_source(id: &str, request: &Value) -> Value =
        verify_contract_source_request;
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn detail_requests_encode_paths() {
        let config = ClientConfig::default();
        assert_eq!(
            batch_contracts_request(&config, &json!({"ids": ["C1"]})).unwrap().path,
            "/api/v1/contracts/batch"
        );
        assert_eq!(
            validate_contract_request(&config, &json!({})).unwrap().path,
            "/api/v1/contracts/validate"
        );

        let spec = compare_contracts_request(&config, "C1,C2", Some("7d")).unwrap();
        assert_eq!(spec.path, "/api/v1/compare");
        assert_eq!(
            spec.query,
            vec![
                ("ids".to_string(), "C1,C2".to_string()),
                ("window".to_string(), "7d".to_string()),
            ]
        );
        assert!(matches!(
            compare_contracts_request(&config, " ", None),
            Err(Error::InvalidRequest(_))
        ));

        let spec = remove_contract_tag_request(&config, "C1", "deFi").unwrap();
        assert_eq!(spec.path, "/api/v1/contracts/C1/tags/deFi");

        assert_eq!(
            list_contract_upgrades_request(&config, "C1", Some(5))
                .unwrap()
                .path,
            "/api/v1/contracts/C1/upgrades"
        );
        assert_eq!(
            verify_contract_source_request(&config, "C1", &json!({"repo": "x"}))
                .unwrap()
                .path,
            "/api/v1/contracts/C1/verify"
        );
    }
}
