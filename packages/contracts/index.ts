/**
 * PulakDrive shared TypeScript contracts.
 *
 * These hand-maintained definitions mirror the serialized Python domain models.
 * Protocol compatibility is determined by `api_protocol_major` and
 * `api_protocol_minor`; changing field names or enum values requires an explicit
 * protocol-version decision. This package does not generate API clients.
 */

export * from "./vault.js";
export * from "./service.js";

