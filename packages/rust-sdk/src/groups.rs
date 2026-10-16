//! Contract groups: collections of contracts with shared stats.
//!
//! Covers the `Groups` tag of `docs/openapi.yaml` (`/api/v1/groups/...`).
//! Group payloads are returned as raw [`serde_json::Value`]; mutation bodies
//! are accepted as raw JSON so the SDK never drifts from the server schema.

use serde_json::Value;

use crate::client::ClientConfig;
use crate::error::Error;
use crate::macros::endpoints;
use crate::request::{contract_id, encode_path_segment, RequestSpec};

fn group_id(id: &str) -> Result<String, Error> {
    let id = id.trim();
    if id.is_empty() {
        return Err(Error::InvalidRequest("group id must not be empty".into()));
    }
    Ok(encode_path_segment(id))
}

pub(crate) fn list_groups_request(_config: &ClientConfig) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get("/api/v1/groups"))
}

pub(crate) fn create_group_request(
    _config: &ClientConfig,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::post("/api/v1/groups", request)
}

pub(crate) fn get_group_request(_config: &ClientConfig, id: &str) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get(format!("/api/v1/groups/{}", group_id(id)?)))
}

pub(crate) fn update_group_request(
    _config: &ClientConfig,
    id: &str,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::patch(format!("/api/v1/groups/{}", group_id(id)?), request)
}

pub(crate) fn delete_group_request(_config: &ClientConfig, id: &str) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::delete(format!(
        "/api/v1/groups/{}",
        group_id(id)?
    )))
}

pub(crate) fn add_group_contract_request(
    _config: &ClientConfig,
    id: &str,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::post(format!("/api/v1/groups/{}/contracts", group_id(id)?), request)
}

pub(crate) fn remove_group_contract_request(
    _config: &ClientConfig,
    id: &str,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::delete_with_body(
        format!("/api/v1/groups/{}/contracts", group_id(id)?),
        request,
    )
}

pub(crate) fn remove_group_contract_by_path_request(
    _config: &ClientConfig,
    id: &str,
    contract: &str,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::delete(format!(
        "/api/v1/groups/{}/contracts/{}",
        group_id(id)?,
        contract_id(contract)?
    )))
}

pub(crate) fn group_stats_request(_config: &ClientConfig, id: &str) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get(format!(
        "/api/v1/groups/{}/stats",
        group_id(id)?
    )))
}

endpoints! {
    /// Lists the caller's contract groups.
    ///
    /// `GET /api/v1/groups`.
    fn list_groups() -> Value = list_groups_request;

    /// Creates a contract group from its JSON definition.
    ///
    /// `POST /api/v1/groups`.
    fn create_group(request: &Value) -> Value = create_group_request;

    /// Fetches a group by id.
    ///
    /// `GET /api/v1/groups/{id}`.
    fn get_group(id: &str) -> Value = get_group_request;

    /// Updates a group's metadata.
    ///
    /// `PATCH /api/v1/groups/{id}`.
    fn update_group(id: &str, request: &Value) -> Value = update_group_request;

    /// Deletes a group. Returns `()` on success (HTTP 204).
    ///
    /// `DELETE /api/v1/groups/{id}`.
    fn delete_group(id: &str) -> () = delete_group_request;

    /// Adds contracts to a group.
    ///
    /// `POST /api/v1/groups/{id}/contracts`.
    fn add_group_contract(id: &str, request: &Value) -> Value = add_group_contract_request;

    /// Removes contracts from a group via a JSON body.
    ///
    /// `DELETE /api/v1/groups/{id}/contracts`.
    fn remove_group_contract(id: &str, request: &Value) -> Value = remove_group_contract_request;

    /// Removes one contract from a group by path id. Returns `()` (HTTP 204).
    ///
    /// `DELETE /api/v1/groups/{id}/contracts/{contractId}`.
    fn remove_group_contract_by_path(id: &str, contract_id: &str) -> () =
        remove_group_contract_by_path_request;

    /// Aggregated stats for a group.
    ///
    /// `GET /api/v1/groups/{id}/stats`.
    fn get_group_stats(id: &str) -> Value = group_stats_request;
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::request::HttpMethod;
    use serde_json::json;

    #[test]
    fn group_requests_target_the_groups_api() {
        let config = ClientConfig::default();
        let spec = create_group_request(&config, &json!({"name": "treasury"})).unwrap();
        assert_eq!(spec.path, "/api/v1/groups");

        assert_eq!(
            get_group_request(&config, "g1").unwrap().path,
            "/api/v1/groups/g1"
        );

        let spec = update_group_request(&config, "g1", &json!({"name": "x"})).unwrap();
        assert_eq!(spec.method, HttpMethod::Patch);
        assert_eq!(spec.path, "/api/v1/groups/g1");

        let spec = remove_group_contract_request(&config, "g1", &json!({"contract_ids": ["C1"]}))
            .unwrap();
        assert_eq!(spec.method, HttpMethod::Delete);
        assert_eq!(spec.path, "/api/v1/groups/g1/contracts");
        assert!(spec.body.is_some());

        assert_eq!(
            remove_group_contract_by_path_request(&config, "g1", "C1")
                .unwrap()
                .path,
            "/api/v1/groups/g1/contracts/C1"
        );
        assert_eq!(
            group_stats_request(&config, "g1").unwrap().path,
            "/api/v1/groups/g1/stats"
        );

        assert!(matches!(
            get_group_request(&config, " "),
            Err(Error::InvalidRequest(_))
        ));
    }
}
