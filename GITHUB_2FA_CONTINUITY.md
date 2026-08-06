# GitHub two-factor authentication continuity

**Status:** operational security runbook for contributors and stewards  
**Last verified:** 6 August 2026

## The short answer

Enabling GitHub two-factor authentication should **not** break an established local workflow that already uses GitHub CLI, Git Credential Manager, a personal access token, SSH, a GitHub App, or the built-in Actions token. Two-factor authentication governs interactive account login and sensitive account changes. Git does not accept an account password or a time-based one-time code as an HTTPS credential.

The actual continuity risks are lost recovery methods, an expired or revoked token, a token stored as plaintext, an unmaintained SSH key, or automation tied to one human account. Treat those as separate failure modes.

## Lowest-friction safe setup

Before GitHub's enrollment deadline:

1. Add a passkey for ordinary low-friction login, for example through Windows Hello or a password manager that securely synchronizes passkeys.
2. Add an independent second method: preferably a TOTP authenticator or physical security key on a different device.
3. Download the one-time recovery codes. Store them in an encrypted password manager and one separate offline location. Never put them in Git, a project folder, an issue, an agent prompt, a log, or an Actions artifact.
4. Keep the account email current and preserve at least one previously verified browser or device.
5. Complete a real login and GitHub's post-enrollment checkup before relying on the setup.

A passkey can satisfy both the password and 2FA step. A security key used only as a second factor still requires the password. GitHub Support cannot restore an account when every configured recovery route is lost, so two independent methods matter more than which brand of authenticator is chosen.

Official guidance: [configure 2FA](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/configuring-two-factor-authentication), [configure recovery methods](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/configuring-two-factor-authentication-recovery-methods), and [recover a 2FA account](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/recovering-your-account-if-you-lose-your-2fa-credentials).

## Local Git and GitHub CLI

### HTTPS through GitHub CLI

Preferred Windows setup:

```powershell
gh auth login --web --git-protocol https
gh auth setup-git
```

The browser authorization performs 2FA when needed. GitHub CLI then stores an OAuth token or supplied access token through the operating-system credential store and acts as Git's host-specific credential helper. Normal pulls and pushes do not ask for a TOTP code.

Never use `--insecure-storage`, `gh auth token`, or `--show-token` in an agent session or recorded terminal. Do not put `GH_TOKEN` in a profile, repository file, task prompt, or log. See the [GitHub CLI login reference](https://cli.github.com/manual/gh_auth_login).

### Fine-grained personal access tokens

Enabling 2FA does not by itself revoke an existing personal access token. A token can still fail because it expires, is revoked, is unused for too long, loses repository access, or no longer satisfies an organization policy. If a PAT is unavoidable:

- scope it to one owner and selected repositories;
- grant only the required permissions;
- give it a finite lifetime;
- track its renewal outside the repository; and
- store it in the OS credential manager or a secrets vault, never plaintext.

Prefer the GitHub CLI web flow for a human workstation. See [GitHub's PAT guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

### SSH as an independent transport and recovery route

2FA does not change SSH Git authentication. A passphrase-protected or hardware-backed SSH authentication key is a useful independent backup, but it must be configured and tested before browser lockout. Only the public key goes to GitHub; the private key stays on the device or hardware key.

Do not remove working HTTPS credentials while adding SSH. Test the new route first. GitHub can remove an SSH authentication key after a long period of non-use, so a key is not a substitute for recovery codes. See [connecting with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

## Safe smoke test

Run this before enrollment, directly after enrollment, and after any credential rotation:

```powershell
gh api user --jq .login
git fetch --dry-run origin
git push --dry-run origin HEAD:refs/heads/2fa-continuity-smoke-test
```

The last command checks write authentication without creating the branch. Run it only inside a repository where the account is meant to have write access. If SSH is configured, also run `ssh -T git@github.com`; GitHub's successful authentication message still exits without opening a shell.

If a human wants to inspect the credential-storage diagnosis from `gh auth status`, do so only in a private, unrecorded terminal and do not paste its output into an agent, issue, log, or artifact. Automated checks should use the non-secret API/fetch/dry-run results above.

If HTTPS fails after enrollment, keep any other working credential intact. Reauthorize with `gh auth login --web`, then run `gh auth setup-git` and repeat the smoke test. A 2FA code belongs in GitHub's browser prompt, never in the Git password field.

## Automation and local agents

- GitHub Actions' built-in `GITHUB_TOKEN` is a short-lived repository-scoped GitHub App token. Human 2FA does not interrupt it. Declare explicit least privileges.
- Prefer GitHub Apps with short-lived installation tokens for unattended or cross-repository automation.
- Avoid Actions and scheduled jobs that depend on a sole maintainer's PAT. If one remains temporarily, document its owner, scope, expiry, rotation procedure, and failure signal outside the public repository.
- Local agents should call ordinary `git` and `gh` commands through the configured credential helper. They must never retrieve, display, copy, or log the underlying credential.
- Keep public pull-request workflows secret-free and do not run untrusted code on a persistent credentialed workstation.

See [the Actions token model](https://docs.github.com/en/actions/concepts/security/github_token) and [GitHub App practices](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app).

## Organization continuity

Before moving the Commons to an organization:

- appoint at least two independent human owners, each with tested 2FA and separate recovery custody;
- notify members and outside collaborators before enforcing 2FA;
- prefer secure methods rather than SMS-only enrollment;
- use personal accounts for humans and GitHub Apps for automation; and
- keep mirrors and DOI archives so an account lockout cannot erase the scientific record.

An organization requirement can block noncompliant members and automatically remove noncompliant outside collaborators, including machine-user accounts. Raise the current bootstrap review requirement only after the second steward has working access. See [organization 2FA enforcement](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-two-factor-authentication-for-your-organization/requiring-two-factor-authentication-in-your-organization) and [ownership continuity](https://docs.github.com/en/organizations/managing-peoples-access-to-your-organization-with-roles/maintaining-ownership-continuity-for-your-organization).

## Lockout runbook

1. Do not delete a still-working CLI token, PAT, SSH key, App installation, or clean mirror merely because web login failed.
2. Try a passkey, then the independent TOTP/security key, then one unused recovery code.
3. Use GitHub's recovery flow with a verified email and eligible verified device, SSH key, or PAT if necessary.
4. If compromise rather than ordinary lockout is suspected, revoke and rotate affected credentials from a clean device and inspect recent account/repository activity.
5. If no recovery route remains, preserve the public repository from a clone or mirror; GitHub Support cannot override the account's 2FA security boundary.
