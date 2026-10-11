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

Build and verify one step at a time. After each step, show the changed files and verification results, then stop for the user's review. Do not begin the next step until the user says to continue.

### Step 1: Make server startup predictable

- Remove `sync.py`'s import-time scan of `demo/source`; importing the comparison helper must not scan a folder or depend on the current working directory.
- Put server configuration in one clear place while keeping the service bound to loopback.
- **Checkpoint:** start the API from the repository root and the `src` directory; both should use the same Desktop storage path and should not scan the client source.

### Step 2: Protect the existing sync API

- Add a dedicated random bearer token for the laptop sync client.
- Require it on both `/api/inventory` and `/api/uploadfile`; update the client to send the token from its environment.
- Keep the token out of source control and logs.
- **Checkpoint:** requests with no token or a wrong token fail; a valid token completes the existing sync and the next inventory check reports files unchanged.

### Step 3: Bound existing sync requests

- Limit inventory entry count and JSON body size.
- Limit upload size and request duration, and reject oversized uploads without replacing a stored file.
- **Checkpoint:** normal sync still works; oversized inventory and upload requests are rejected; interrupted or rejected uploads leave no partial destination file.

### Step 4: Add phone login and session protection

- Add password-based login with a stored password hash, logout, session expiry, and login throttling.
- Use `Secure`, `HttpOnly`, and `SameSite=Lax` session cookies. Require CSRF protection for state-changing browser actions.
- **Checkpoint:** correct login succeeds; wrong credentials and expired sessions fail; cookie attributes and CSRF token validation are verified; credentials do not appear in logs or tracked files.

### Step 5: Add an authenticated file listing

- Add a phone-friendly page that lists relative paths and useful metadata without exposing absolute server paths.
- Require a phone session. Do not add upload or delete controls in this step.
- **Checkpoint:** an authenticated phone session sees stored files; unauthenticated requests are rejected; traversal-like input cannot reveal files outside storage.

### Step 6: Add safe downloads

- Add a download route that resolves paths beneath storage and rejects traversal and symlink escapes.
- Send files as attachments with `X-Content-Type-Options: nosniff`; do not render HTML or SVG from storage as trusted pages.
- **Checkpoint:** valid files download; invalid paths fail; an HTML test file downloads as an attachment instead of executing in the app origin.

### Step 7: Add phone uploads in isolation

- Let an authenticated phone session upload into the flat `phone-uploads/` directory only.
- Sanitize filenames, reject collisions, enforce the configured size limit, verify SHA-256, and use temporary files plus atomic replacement after validation.
- **Checkpoint:** a small file appears in `phone-uploads/`; collision, traversal, oversized, invalid-hash, invalid-CSRF, and unauthenticated requests fail without changing existing files.

### Step 8: Enable private remote access

- Keep FastAPI bound to loopback and proxy it through Tailscale Serve over HTTPS.
- Restrict the tailnet to the user's devices and the service port. Do not enable Funnel or router port forwarding.
- **Checkpoint:** the authenticated phone can use the app from a different network; the service is not reachable from the public internet or directly from the LAN listener.

### Step 9: Review laptop storage protection

- Verify the storage directory is accessible only to the user's Windows account, check disk encryption status, and establish a separate backup procedure.
- **Checkpoint:** record the permissions, encryption status, and backup location; do not claim the files are protected at rest until encryption is confirmed.

### Step 10: Run the end-to-end security checklist

- Re-run the sync unchanged/update cases and all authentication, path, size, collision, download-header, and remote-access checks.
- **Checkpoint:** every acceptance criterion below passes; report any remaining limitation before considering the security work complete.

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
- Storage permissions, disk encryption status, and backup location are recorded accurately.
