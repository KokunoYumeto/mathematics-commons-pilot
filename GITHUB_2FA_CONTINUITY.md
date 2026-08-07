# GitHub two-factor authentication continuity

**Status:** operational security runbook for contributors and stewards
**Last verified:** 7 August 2026

## The short answer

**GitHub's documented behavior:** enabling two-factor authentication does not revoke or change existing personal-access or OAuth tokens, and it does not change SSH command-line authentication. Git and API access continue to use a token, application, or SSH key; Git does not accept an account password or a time-based one-time code as an HTTPS credential. An established local workflow using GitHub CLI, Git Credential Manager, a valid token, SSH, a GitHub App, or the built-in Actions token should therefore continue through enrollment.

If an account selected for mandatory 2FA misses GitHub's enrollment and grace periods, its existing tokens continue to function, but browser access is blocked and the account cannot authorize a new app or create a new personal access token until it enrolls. Do not postpone enrollment on the theory that a token alone is a recovery plan. See GitHub's [mandatory-2FA explanation](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/about-mandatory-two-factor-authentication) and [command-line 2FA guidance](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/accessing-github-using-two-factor-authentication).

The actual continuity risks are lost recovery methods, an expired or revoked token, a token stored as plaintext, an unmaintained SSH key, or automation tied to one human account. Treat those as separate failure modes.

## Lowest-friction safe setup

**Current GitHub requirement:** initial 2FA enrollment uses a TOTP authenticator or SMS. GitHub recommends TOTP and currently treats a passkey or security key as a backup rather than the primary enrollment method.

**Commons recommendation for a low-friction, recoverable setup:** before the account's displayed enrollment deadline:

1. Configure a TOTP authenticator as the primary method.
2. Download the one-time recovery codes. Store them in an encrypted password manager and one separate offline location. Never put them in Git, a project folder, an issue, an agent prompt, a log, or an Actions artifact.
3. Add a passkey for ordinary low-friction login or a physical security key as a backup. Keep at least one method on a different device or failure domain from the TOTP method.
4. Keep the account email current and preserve at least one previously verified browser or device. GitHub uses a retained device cookie as one possible recovery factor.
5. Complete a real login and GitHub's 28-day post-enrollment checkup before relying on the setup.

A passkey can satisfy both the password and 2FA step after it is registered. A security key used only as a second factor still requires the password. Synced passkeys are convenient; device-bound passkeys are not a substitute for an independent recovery method. GitHub Support cannot restore an account when every configured recovery route is lost, so separate recovery paths matter more than which brand of authenticator is chosen.

Official guidance: [configure 2FA](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/configuring-two-factor-authentication), [configure recovery methods](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/configuring-two-factor-authentication-recovery-methods), and [recover a 2FA account](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/recovering-your-account-if-you-lose-your-2fa-credentials).

## Local Git and GitHub CLI

### HTTPS through GitHub CLI

**Commons recommendation for a human Windows workstation:** if Git Credential Manager already handles HTTPS Git successfully, enrollment does not require replacing it. Otherwise, GitHub CLI offers a straightforward browser flow:

```powershell
gh auth login --hostname github.com --web --git-protocol https
gh auth setup-git --hostname github.com
```

The browser authorization performs 2FA when needed. GitHub CLI prefers to store its OAuth token in the operating-system credential store, but its documented fallback is a plaintext file if no credential store is available or storage fails. Before relying on it, a human should run `gh auth status --active --hostname github.com` in a private terminal, without `--show-token`, and confirm the reported storage is secure. Fix credential-store support instead of accepting a plaintext fallback.

`gh auth setup-git` configures GitHub CLI as Git's credential helper. The `--git-protocol` choice applies to all users of that GitHub host, so do not change it casually on a shared or multi-account machine. Normal pulls and pushes then use the stored credential without asking for a TOTP code. An SSH Git remote is separate from GitHub CLI's API authentication: `gh` still needs its own token.

Never use `--insecure-storage`, `gh auth token`, or `--show-token` in an agent session or recorded terminal. Do not put `GH_TOKEN` in a profile, repository file, task prompt, or log. See the [GitHub CLI login reference](https://cli.github.com/manual/gh_auth_login).

### Fine-grained personal access tokens

Enabling 2FA does not by itself revoke an existing personal access token. A token can still fail because it expires, is revoked, goes unused for one year, loses repository access, lacks an endpoint permission, or no longer satisfies an organization policy. A `Resource not accessible by personal access token` response is therefore usually a scope, permission, feature-support, ownership, or organization-policy problem rather than a 2FA problem.

GitHub recommends fine-grained tokens when they support the task, but currently documents important gaps. A fine-grained token cannot contribute to a public repository where its user is not a member, cannot contribute where its user is an outside or repository collaborator, cannot span multiple organizations, and does not support Packages, the Checks API, or Projects owned by a user account. Each fine-grained token selects one resource owner and may be limited to selected repositories.

If a fine-grained PAT is unavoidable:

- scope it to one owner and selected repositories;
- grant only the required permissions;
- give it a finite lifetime;
- track its renewal outside the repository; and
- store it in the OS credential manager or a secrets vault, never plaintext.

Prefer the GitHub CLI web flow or Git Credential Manager for a human workstation. GitHub CLI's `--with-token` flow expects a classic PAT with broad minimum scopes and warns that a fine-grained PAT can behave confusingly there. Although the CLI documents `GH_TOKEN` for a fine-grained token, this project allows it only as a process-bounded automation input supplied from a secret store, never as a persistent profile variable. Use a classic PAT only when a documented feature gap requires it; its repository scope can cover every repository the user can access. See [GitHub's PAT guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) and the [GitHub CLI login reference](https://cli.github.com/manual/gh_auth_login).

### SSH as an independent Git transport and potential recovery factor

2FA does not change SSH Git authentication. A passphrase-protected or hardware-backed SSH authentication key is a useful independent transport and may be offered as an account-recovery factor, but recovery availability is not guaranteed. It must be configured and tested before browser lockout. Only the public key goes to GitHub; the private key stays on the device or hardware key.

Do not remove working HTTPS credentials while adding SSH. Test the new route first. GitHub automatically deletes SSH keys that have not been used in one year, so a key is not a substitute for recovery codes. See [connecting with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh) and [deleted or missing SSH keys](https://docs.github.com/en/authentication/troubleshooting-ssh/deleted-or-missing-ssh-keys).

## Safe smoke test

Run this before enrollment, directly after enrollment, and after any credential rotation:

```powershell
gh api user --jq .login
git fetch --dry-run origin
git push --dry-run origin HEAD:refs/heads/2fa-continuity-smoke-test
```

The commands prove different things:

- `gh api user` tests GitHub CLI's API credential and prints only the public account name;
- fetching this public repository tests network and remote configuration but can succeed anonymously, so it does not prove write authentication; and
- the push dry run tests Git write authentication without creating the branch.

Run the push test only inside a repository where the account is meant to have write access. If SSH is configured, also run `ssh -T git@github.com`. A successful response names the GitHub account and says that GitHub provides no shell access; the command intentionally exits with status 1. See GitHub's [SSH connection test](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection).

If a human wants to inspect the credential-storage diagnosis from `gh auth status`, do so only in a private, unrecorded terminal and do not paste its output into an agent, issue, log, or artifact. Automated checks should use the non-secret API/fetch/dry-run results above.

If HTTPS fails after enrollment, keep any other working credential intact. Reauthorize with `gh auth login --web`, then run `gh auth setup-git` and repeat the smoke test. A 2FA code belongs in GitHub's browser prompt, never in the Git password field.

## Automation and local agents

- GitHub Actions' built-in `GITHUB_TOKEN` is a short-lived, per-job, repository-scoped GitHub App installation token. Human 2FA does not interrupt it. Declare explicit least privileges.
- Most events created with `GITHUB_TOKEN` do not start another workflow. Do not silently substitute it where workflow chaining or cross-repository access is required.
- Prefer GitHub Apps with scoped, short-lived installation tokens for unattended or cross-repository automation.
- Avoid Actions and scheduled jobs that depend on a sole maintainer's PAT. If one remains temporarily, document its owner, scope, expiry, rotation procedure, and failure signal outside the public repository.
- Local agents should call ordinary `git` and `gh` commands through the configured credential helper. They must never retrieve, display, copy, or log the underlying credential.
- Keep public pull-request workflows secret-free and do not run untrusted code on a persistent credentialed workstation.

See [the Actions token model](https://docs.github.com/en/actions/concepts/security/github_token) and [GitHub App practices](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app).

## Organization continuity

**GitHub's documented enforcement effects:** noncompliant organization members and billing managers retain membership but cannot access organization resources. Noncompliant outside collaborators, including unattended or shared accounts, are removed and lose repository access. A separate secure-methods setting treats passkeys, security keys, TOTP apps, and GitHub Mobile as secure; a user with an insecure method such as SMS configured can be blocked under that stricter setting.

**Commons recommendation:** before moving the Commons to an organization or enabling either enforcement setting:

- appoint at least two independent human owners, each with tested 2FA and separate recovery custody;
- notify members, outside collaborators, and billing managers at least one week before enforcing 2FA;
- audit the effect of the optional secure-methods-only setting, including any SMS configuration;
- use personal accounts for humans and GitHub Apps for automation; and
- keep mirrors and DOI archives so an account lockout cannot erase the scientific record.

Audit organization authentication policies separately from 2FA. New organizations enable OAuth-app access restrictions by default; organization owners can also block PAT types or require approval for fine-grained PATs, and a later SSO policy can add another authorization layer. Those controls, not 2FA itself, can make a working CLI, token, or key lose organization access. Raise the current bootstrap review requirement only after the second steward has working access. See [preparing organization 2FA](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-two-factor-authentication-for-your-organization/preparing-to-require-two-factor-authentication-in-your-organization), [organization 2FA enforcement](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-two-factor-authentication-for-your-organization/requiring-two-factor-authentication-in-your-organization), [programmatic-access policies](https://docs.github.com/en/organizations/managing-programmatic-access-to-your-organization/about-programmatic-access-in-your-organization), [OAuth-app restrictions](https://docs.github.com/en/organizations/managing-oauth-access-to-your-organizations-data/about-oauth-app-access-restrictions), and [ownership continuity](https://docs.github.com/en/organizations/managing-peoples-access-to-your-organization-with-roles/maintaining-ownership-continuity-for-your-organization).

## Lockout runbook

1. Do not delete a still-working CLI token, PAT, SSH key, App installation, or clean mirror merely because web login failed.
2. Try a passkey, then the independent TOTP/security key, then one unused recovery code.
3. Use GitHub's recovery flow with a verified email and any eligible verified device, SSH key, or PAT offered by GitHub. These factors are not guaranteed to be available, and manual recovery review can take up to three business days.
4. If compromise rather than ordinary lockout is suspected, revoke and rotate affected credentials from a clean device and inspect recent account/repository activity.
5. If no recovery route remains, preserve the public repository from a clone or mirror; GitHub Support cannot override the account's 2FA security boundary.
