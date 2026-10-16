//! Contract notes: free-form annotations attached to a contract.
//!
//! Covers the contract-notes endpoints of the `Contracts` tag
//! (`/api/v1/contracts/{id}/notes/...`). Note bodies are raw
//! [`serde_json::Value`] payloads.

use serde_json::Value;

use crate::client::ClientConfig;
use crate::error::Error;
use crate::macros::endpoints;
use crate::request::{contract_id, encode_path_segment, RequestSpec};

fn note_path(id: &str, note_id: &str) -> Result<String, Error> {
    let note_id = note_id.trim();
    if note_id.is_empty() {
        return Err(Error::InvalidRequest("note id must not be empty".into()));
    }
    Ok(format!(
        "/api/v1/contracts/{}/notes/{}",
        contract_id(id)?,
        encode_path_segment(note_id)
    ))
}

pub(crate) fn list_notes_request(_config: &ClientConfig, id: &str) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::get(format!(
        "/api/v1/contracts/{}/notes",
        contract_id(id)?
    )))
}

pub(crate) fn create_note_request(
    _config: &ClientConfig,
    id: &str,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::post(
        format!("/api/v1/contracts/{}/notes", contract_id(id)?),
        request,
    )
}

pub(crate) fn update_note_request(
    _config: &ClientConfig,
    id: &str,
    note_id: &str,
    request: &Value,
) -> Result<RequestSpec, Error> {
    RequestSpec::patch(note_path(id, note_id)?, request)
}

pub(crate) fn delete_note_request(
    _config: &ClientConfig,
    id: &str,
    note_id: &str,
) -> Result<RequestSpec, Error> {
    Ok(RequestSpec::delete(note_path(id, note_id)?))
}

endpoints! {
    /// Lists the notes attached to a contract.
    ///
    /// `GET /api/v1/contracts/{id}/notes`.
    fn list_contract_notes(id: &str) -> Value = list_notes_request;

    /// Creates a note on a contract.
    ///
    /// `POST /api/v1/contracts/{id}/notes`.
    fn create_contract_note(id: &str, request: &Value) -> Value = create_note_request;

    /// Updates an existing note.
    ///
    /// `PATCH /api/v1/contracts/{id}/notes/{noteID}`.
    fn update_contract_note(id: &str, note_id: &str, request: &Value) -> Value =
        update_note_request;

    /// Deletes a note. Returns `()` on success (HTTP 204).
    ///
    /// `DELETE /api/v1/contracts/{id}/notes/{noteID}`.
    fn delete_contract_note(id: &str, note_id: &str) -> () = delete_note_request;
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn note_requests_under_the_contract_path() {
        let config = ClientConfig::default();
        assert_eq!(
            list_notes_request(&config, "CABC").unwrap().path,
            "/api/v1/contracts/CABC/notes"
        );
        let spec = create_note_request(&config, "CABC", &json!({"text": "hi"})).unwrap();
        assert_eq!(spec.path, "/api/v1/contracts/CABC/notes");
        assert_eq!(spec.body.unwrap()["text"], "hi");

        let spec = update_note_request(&config, "CABC", "n1", &json!({"text": "x"})).unwrap();
        assert_eq!(spec.path, "/api/v1/contracts/CABC/notes/n1");
        assert_eq!(
            delete_note_request(&config, "CABC", "n1").unwrap().path,
            "/api/v1/contracts/CABC/notes/n1"
        );
        assert!(matches!(
            delete_note_request(&config, "CABC", ""),
            Err(Error::InvalidRequest(_))
        ));
    }
}
