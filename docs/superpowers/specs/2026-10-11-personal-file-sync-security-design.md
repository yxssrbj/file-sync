# Personal File Sync Security Design

**Status:** Draft for user review
**Date:** 2026-10-11

## Goal and scope

Harden the personal file-sync application so the user's laptop can host the service and the user can access it from their phone while away from home. The laptop sync client uploads changed files. The phone can browse, download, and upload files. Phone uploads are stored beneath `phone-uploads/` in the configured storage root so they stay separate from laptop-synced files.

Remote access is private to devices the user has authorized through Tailscale. The app will not be published to the public internet, and the router will not forward a port to it. The laptop must be awake, online, and running the service for remote access to work.

## Threat model

Protect stored file contents and names from unauthenticated network users, other users on the same Wi-Fi, and accidental cross-device writes. Limit damage if a Tailscale-connected device or app credential is compromised. Preserve laptop-synced data when files are uploaded from the phone.

The initial version is for one user and their own devices. It does not provide multi-user sharing, public links, remote deletion, or protection against compromise of the laptop's Windows account. Windows disk encryption and backups remain operating-system responsibilities.

## Access model

- **Sync client:** authenticates with a dedicated random bearer token. It can use inventory comparison and upload laptop-synced files. It cannot browse or download stored files.
- **Phone browser:** authenticates with a password-protected web session. It can list files, download files, and upload files into `phone-uploads/`. It cannot delete files or upload into the laptop-synced area.
- Every application endpoint requires the appropriate credential. Tailscale membership is an additional network boundary, not a replacement for application authentication.
- Keep the browser session in a `Secure`, `HttpOnly`, `SameSite=Lax` cookie with an expiry and logout. Require a CSRF token for browser uploads.
- Store the client token, password hash, and session signing secret outside tracked source files. Never log credentials.

## Network and transport

- Keep the FastAPI service bound to loopback on the laptop.
- Use Tailscale Serve to proxy the local service to authorized devices in the tailnet over HTTPS. Do not use Tailscale Funnel or router port forwarding.
- Restrict tailnet access to the user's own laptop and phone, and allow only the service port needed for the browser interface.
- The local sync client may continue using loopback. The phone connects through the private Tailscale HTTPS name.

Tailscale Serve can proxy a local service to a tailnet and requires HTTPS to be enabled. Its documentation recommends keeping a backend on localhost when relying on Serve-provided identity headers. This design keeps application authentication even when Serve is used. See [Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve).

## Phone browsing and upload behavior

- Provide a responsive page for authenticated file listing, download, and upload.
- Resolve every requested path beneath the configured storage root and reject traversal, absolute paths, and symlink escapes.
- Return downloaded files as attachments with `X-Content-Type-Options: nosniff`; do not render uploaded HTML or SVG as trusted same-origin pages.
- Store phone uploads in a flat `phone-uploads/` directory. Accept a sanitized filename only; reject a name collision rather than replacing an existing file. Verify the received SHA-256 and write to a temporary file before the final atomic move.
- Do not add delete or rename controls in this version.

## Resource and storage protections

- Enforce a configurable upload-size limit; proposed initial default: 250 MiB per file.
- Limit inventory request size and number of entries; proposed maximum: 10,000 entries and 10 MiB of JSON.
- Apply login attempt throttling and request timeouts. Return generic authentication errors and avoid exposing server paths in responses.
- Run the service as the normal, non-administrator Windows user. Keep storage within that user's protected Desktop directory, enable Windows disk encryption where available, and maintain a separate backup.
- Keep temporary upload files beside their destination, verify the hash before replacement, and clean them after failures.

## Implementation order

1. Add separate authentication for the sync client and phone session; protect existing inventory and upload endpoints before making the service remotely reachable.
2. Add request limits, upload limits, timeouts, and login throttling.
3. Add the authenticated phone browse/download/upload page with the path and response rules above.
4. Configure the Tailscale-only HTTPS path and verify the FastAPI listener remains on loopback.
5. Review storage permissions, disk encryption, backup procedure, and secret handling.
6. Verify access control, path validation, size limits, conflict behavior, and remote connectivity with negative and positive checks.

Each implementation step will be delivered separately. After each step, the user reviews the changes and decides whether to continue. No later step begins until the user explicitly continues.

## Acceptance criteria

- Unauthenticated calls to all protected endpoints are rejected.
- A sync-client credential can sync files but cannot use phone browsing endpoints.
- The phone session can list and download stored files and upload only into `phone-uploads/`.
- A cross-site form cannot use the phone session to upload files.
- Phone uploads cannot overwrite existing files or laptop-synced files.
- Traversal and symlink escape attempts are rejected, and downloads are sent as attachments.
- Oversized uploads and inventories are rejected before unbounded storage or processing occurs.
- The service is reachable from the user's authorized phone over Tailscale HTTPS, but is not exposed through public router ports or Tailscale Funnel.
- Credentials are absent from source control and logs.
- Existing hash-based sync behavior continues to identify unchanged files correctly.
