//! Per-user watchlists and watched accounts.
//!
//! Covers the `Watchlist` tag (`/api/v1/watchlist/...`) and the watched-
//! accounts endpoints (`/api/v1/watched-accounts`) of `docs/openapi.yaml`.
//! Watched accounts are Soroban addresses monitored outside the contract
//! registry; payloads are raw [`serde_json::Value`].

use serde_json::Value;

use crate::client::ClientConfig;
use crate::error::Error;
use crate::macros::endpoints;
use crate::request::{contract_id, encode_path_segment, RequestSpec};

/// Filters for [`crate::Client::list_watchlist`].
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ListWatchlistParams {
    /// Opaque cursor from a previous page.
    pub cursor: Option<String>,
    /// Page size (`1..=200`, default 50).
    pub limit: Option<u32>,
}

impl ListWatchlistParams {
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

pub(crate) fn list_watchlist_request(
    _config: &ClientConfig,
    params: &ListWatchlistParams,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get("/api/v1/watchlist")
        .query_opt("cursor", params.cursor.as_deref())
        .query_opt("limit", params.limit))
}

pub(crate) fn add_watchlist_request(
    _config: &ClientConfig,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::post("/api/v1/watchlist", request)
}

pub(crate) fn remove_watchlist_request(
    _config: &ClientConfig,
    id: &str,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::delete(format!(
        "/api/v1/watchlist/{}",
        contract_id(id)?
    )))
}

pub(crate) fn watchlist_status_request(
    _config: &ClientConfig,
    id: &str,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get(format!(
        "/api/v1/watchlist/{}/status",
        contract_id(id)?
    )))
}

pub(crate) fn list_watched_accounts_request(
    _config: &ClientConfig,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get("/api/v1/watched-accounts"))
}

pub(crate) fn add_watched_account_request(
    _config: &ClientConfig,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::post("/api/v1/watched-accounts", request)
}

pub(crate) fn delete_watched_account_request(
    _config: &ClientConfig,
    id: &str,
) -> Result<RequestSpec, Error> {
    let id = id.trim();
    if id.is_empty() {
        return Err(Error::InvalidRequest(
            "watched account id must not be empty".into(),
        ));
    }
    Ok(RequestSpec::delete(format!(
        "/api/v1/watched-accounts/{}",
        encode_path_segment(id)
    )))
}

endpoints! {
    /// Lists the authenticated caller's watchlist.
    ///
    /// `GET /api/v1/watchlist`.
    fn list_watchlist(params: &ListWatchlistParams) -> Value = list_watchlist_request;

    /// Adds a contract to the caller's watchlist.
    ///
    /// `POST /api/v1/watchlist`.
    fn add_to_watchlist(request: &Value) -> Value = add_watchlist_request;

    /// Removes a contract from the caller's watchlist. Returns `()` (HTTP 204).
    ///
    /// `DELETE /api/v1/watchlist/{contractId}`.
    fn remove_from_watchlist(contract_id: &str) -> () = remove_watchlist_request;

    /// Whether the caller watches a contract, with notification settings.
    ///
    /// `GET /api/v1/watchlist/{contractId}/status`.
    fn get_watchlist_status(contract_id: &str) -> Value = watchlist_status_request;

    /// Lists the caller's watched accounts.
    ///
    /// `GET /api/v1/watched-accounts`.
    fn list_watched_accounts() -> Value = list_watched_accounts_request;

    /// Starts watching an account.
    ///
    /// `POST /api/v1/watched-accounts`.
    fn add_watched_account(request: &Value) -> Value = add_watched_account_request;

    /// Stops watching an account. Returns `()` on success (HTTP 204).
    ///
    /// `DELETE /api/v1/watched-accounts/{id}`.
    fn delete_watched_account(id: &str) -> () = delete_watched_account_request;
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn watchlist_requests() {
        let config = ClientConfig::default();
        let spec = list_watchlist_request(&config, &ListWatchlistParams::default().limit(10))
            .unwrap();
        assert_eq!(spec.path, "/api/v1/watchlist");
        assert_eq!(spec.query, vec![("limit".to_string(), "10".to_string())]);

        assert_eq!(
            add_watchlist_request(&config, &json!({"contract_id": "CABC"}))
                .unwrap()
                .path,
            "/api/v1/watchlist"
        );
        assert_eq!(
            remove_watchlist_request(&config, "CABC")
                .unwrap()
                .path,
            "/api/v1/watchlist/CABC"
        );
        assert_eq!(
            watchlist_status_request(&config, "CABC")
                .unwrap()
                .path,
            "/api/v1/watchlist/CABC/status"
        );
    }

    #[test]
    fn watched_account_requests() {
        let config = ClientConfig::default();
        assert_eq!(
            list_watched_accounts_request(&config).unwrap().path,
            "/api/v1/watched-accounts"
        );
        assert_eq!(
            add_watched_account_request(&config, &json!({"account": "GABC"}))
                .unwrap()
                .path,
            "/api/v1/watched-accounts"
        );
        assert_eq!(
            delete_watched_account_request(&config, "wa1")
                .unwrap()
                .path,
            "/api/v1/watched-accounts/wa1"
        );
        assert!(matches!(
            delete_watched_account_request(&config, ""),
            Err(Error::InvalidRequest(_))
        ));
    }
}
