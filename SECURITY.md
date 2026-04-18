# Security Policy

## Supported Versions

Security fixes are applied to the latest version on the `main` branch.

## Reporting a Vulnerability

Please do **not** open public issues for suspected vulnerabilities.

Instead, report privately with:

- Vulnerability type and impact
- Affected endpoints/files
- Reproduction steps or proof of concept
- Suggested mitigation (if available)

If no private contact channel is configured yet, open a minimal GitHub issue requesting a secure contact path without disclosing exploit details.

## Security Best Practices for Deployments

- Set strong API keys and keep them out of source control.
- Restrict CORS and network exposure for production.
- Add authentication/authorization before public deployment.
- Add rate limiting, audit logs, and monitoring.
- Rotate credentials regularly and use least-privilege access.
