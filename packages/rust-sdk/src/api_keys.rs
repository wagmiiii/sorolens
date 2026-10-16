//! API key lifecycle: listing, creation, lookup, revocation, rotation.
//!
//! Covers the `API Keys` tag of `docs/openapi.yaml` under `/api/v1/api-keys`.
//! Responses are returned as raw [`serde_json::Value`] payloads because the
//! create/rotate calls additionally embed the one-time plaintext key; callers
//! can read `key` straight off the object.

use serde_json::Value;

use crate::client::ClientConfig;
use crate::error::Error;
use crate::macros::endpoints;
use crate::request::{encode_path_segment, RequestSpec};
use crate::types::CreateApiKeyRequest;

/// Filters for [`crate::Client::list_api_keys`].
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ListApiKeysParams {
    /// Opaque cursor from a previous page.
    pub cursor: Option<String>,
    /// Page size (`1..=200`, default 50).
    pub limit: Option<u32>,
}

impl ListApiKeysParams {
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

pub(crate) fn list_request(
    _config: &ClientConfig,
    params: &ListApiKeysParams,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get("/api/v1/api-keys")
        .query_opt("cursor", params.cursor.as_deref())
        .query_opt("limit", params.limit))
}

pub(crate) fn create_request(
    _config: &ClientConfig,
    request: &CreateApiKeyRequest,
) -> Result<RequestSpec, Error> {
    RequestSpec::post("/api/v1/api-keys", request)
}

pub(crate) fn get_request(_config: &ClientConfig, id: &str) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get(format!(
        "/api/v1/api-keys/{}",
        encode_path_segment(id.trim())
    )))
}

pub(crate) fn revoke_request(_config: &ClientConfig, id: &str) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::delete(format!(
        "/api/v1/api-keys/{}",
        encode_path_segment(id.trim())
    )))
}

pub(crate) fn rotate_request(_config: &ClientConfig, id: &str) -> Result<RequestSpec, Error> {
    RequestSpec::post(
        format!(
            "/api/v1/api-keys/{}/rotate",
            encode_path_segment(id.trim())
        ),
        &Vec::<String>::new(),
    )
}

endpoints! {
    /// Lists the API keys visible to the caller.
    ///
    /// `GET /api/v1/api-keys`.
    fn list_api_keys(params: &ListApiKeysParams) -> Value = list_request;

    /// Creates an API key. The plaintext token is returned once, in the
    /// `key` field of the response.
    ///
    /// `POST /api/v1/api-keys`.
    fn create_api_key(request: &CreateApiKeyRequest) -> Value = create_request;

    /// Fetches API key metadata by id.
    ///
    /// `GET /api/v1/api-keys/{id}`.
    fn get_api_key(id: &str) -> Value = get_request;

    /// Revokes an API key. Returns `()` on success (HTTP 204).
    ///
    /// `DELETE /api/v1/api-keys/{id}`.
    fn revoke_api_key(id: &str) -> () = revoke_request;

    /// Rotates an API key; the new plaintext token is returned once in the
    /// `key` field of the response.
    ///
    /// `POST /api/v1/api-keys/{id}/rotate`.
    fn rotate_api_key(id: &str) -> Value = rotate_request;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn list_request_encodes_filters() {
        let config = ClientConfig::default();
        let params = ListApiKeysParams::default().limit(10).cursor("abc");
        let spec = list_request(&config, &params).unwrap();
        assert_eq!(spec.path, "/api/v1/api-keys");
        assert_eq!(
            spec.query,
            vec![
                ("cursor".to_string(), "abc".to_string()),
                ("limit".to_string(), "10".to_string()),
            ]
        );
    }

    #[test]
    fn get_and_reuse_encode_the_id() {
        let config = ClientConfig::default();
        let spec = get_request(&config, "key 1").unwrap();
        assert_eq!(spec.path, "/api/v1/api-keys/key%201");
        let spec = revoke_request(&config, "k1").unwrap();
        assert_eq!(spec.method, crate::request::HttpMethod::Delete);
    }

    #[test]
    fn create_request_serializes_name_and_scopes() {
        let config = ClientConfig::default();
        let request = CreateApiKeyRequest::new("ci", vec!["read:contracts"]);
        let spec = create_request(&config, &request).unwrap();
        assert_eq!(spec.path, "/api/v1/api-keys");
        let body = spec.body.unwrap();
        assert_eq!(body["name"], "ci");
        assert_eq!(body["scopes"][0], "read:contracts");
    }

    #[test]
    fn rotate_request_posts_to_the_rotate_path() {
        let config = ClientConfig::default();
        let spec = rotate_request(&config, "k1").unwrap();
        assert_eq!(spec.path, "/api/v1/api-keys/k1/rotate");
    }
}
