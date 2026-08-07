# One-way Git mirror runbook

**Status:** pilot-ready procedure; no independent mirror destination is claimed yet

**Purpose:** keep the complete scientific Git history recoverable outside the primary GitHub repository

Every ordinary clone already contains the repository's committed history. A formal mirror adds a second, independently administered bare repository that receives all branches, tags, and other Git refs from the primary. It does not pool model inference or make GitHub itself peer-to-peer. It makes the durable scientific record less dependent on one account or host.

## Safety boundary

`git push --mirror` synchronizes deletions as well as additions. It can delete destination-only refs. Use it only with a dedicated mirror repository that contains no independent work and whose sole purpose is to reflect this project. Never point it at a personal repository, a working repository, or a destination whose ownership and URL have not been checked by a human.

The first mirror push and every destination change require explicit human approval after the dry-run output is inspected. A local agent may prepare commands and compare read-only state; it receives no authority to create destinations, retrieve credentials, or perform the push merely from this document.

## What Git mirroring preserves

- commits, trees, blobs, branches, annotated tags, and other Git refs;
- the exact packet, evidence, review, correction, and manifest files committed to those refs; and
- the ability to reconstruct and verify releases whose artifacts are also archived separately.

It does not preserve GitHub Issues, Discussions, Projects, pull-request comments, Actions logs, repository settings, branch protections, release-asset bytes, Zenodo metadata, or account permissions. Mathematically material decisions therefore belong in committed records. Release files and DOI metadata need their own verified archives.

## One-time setup

Choose an independently administered, newly created, empty destination. Replace only the two URL placeholders. Do not paste a token into either URL or command.

```powershell
git clone --mirror https://github.com/KokunoYumeto/mathematics-commons-pilot.git mathematics-commons-pilot.git
Set-Location mathematics-commons-pilot.git
git remote rename origin primary
git remote add --mirror=push mirror https://SECOND-HOST/INDEPENDENT-OWNER/mathematics-commons-pilot.git
git remote -v
```

The displayed fetch and push URLs must identify the intended primary and the dedicated empty mirror. Stop if either is unexpected.

Fetch and inspect the source without writing to the destination:

```powershell
git fetch --prune primary
git fsck --full
git show-ref --head
git count-objects -vH
git push --mirror --dry-run mirror
```

The dry run may propose creating source refs. It must not propose deleting or overwriting destination work that is not already understood as obsolete mirror state. If it does, stop and inspect the destination with its administrator.

After a human explicitly approves the exact destination and dry-run plan:

```powershell
git push --mirror mirror
```

## Read-back verification

Do not treat a zero exit code alone as a mirror receipt. Compare the primary bare clone and destination refs:

```powershell
git fetch --prune primary
git rev-parse refs/heads/main
git ls-remote --exit-code mirror refs/heads/main
git for-each-ref --format='%(objectname) %(refname)' refs/heads refs/tags
git ls-remote --heads --tags mirror
```

Record the UTC verification time, primary main commit, release tag object IDs, destination URL, and any intentionally excluded non-Git surfaces. A small verification script may compare sorted ref maps, but a mismatch must fail closed and may not be repaired by deleting destination state until the cause is understood.

For every citable release, also verify the release manifest and checksums against the independently archived GitHub and Zenodo assets. Git tags identify source history; they do not substitute for external release-asset readback.

## Recurring synchronization

For the 30-day pilot, manual synchronization after protected merges and releases is sufficient. If scheduling is later automated:

- prefer a GitHub App with scoped, short-lived installation tokens when practical;
- for a single Git-only destination, use a dedicated deploy key only if its unique public key is attached to that destination repository with write access and its private key remains in the mirror host's secret store;
- store credentials only in the host's secret store, never in this repository or command logs;
- allow writes only to the dedicated destination;
- fetch from the public primary, run `git fsck`, perform and log a dry-run, then push;
- alert on ref deletion, force-update, unexpected source host, or verification mismatch; and
- keep at least one periodically tested offline bundle or archive in addition to the online mirror.

**GitHub facts:** a deploy key is bound to one repository, is read-only by default, does not expire, cannot be reused for another repository, and remains active if the person who created it later loses access. A write-enabled deploy key has broad Git authority, so it is not a generally low-privilege credential and needs a manual inventory, rotation date, and revocation procedure. GitHub recommends a GitHub App when finer permissions and short-lived credentials are needed. The source repository's built-in Actions `GITHUB_TOKEN` is repository-scoped and is not a credential for an independently owned mirror destination. See GitHub's [deploy-key guidance](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys) and [Actions token model](https://docs.github.com/en/actions/concepts/security/github_token).

GitHub 2FA does not add an interactive code prompt to every authenticated Git operation. If a machine-user account is used instead of a deploy key or GitHub App, organization 2FA enforcement can remove it as a noncompliant outside collaborator; it therefore needs its own secure 2FA and recovery custody. Follow [GITHUB_2FA_CONTINUITY.md](GITHUB_2FA_CONTINUITY.md).

## Failure and promotion

If the primary host is unavailable, freeze writes and compare at least two independent clones or archives before promoting a mirror. The stewards publish the exact last common commit and any missing non-Git state. They then configure a new protected rendezvous repository and have contributors add it as a new remote. Do not silently reverse the automated direction or merge divergent mirrors.

Two-way automatic synchronization is outside the first pilot. If independent forges later accept work concurrently, integration needs an explicit federation protocol for identities, signatures, review states, conflicts, and correction histories—not two opposing `git push --mirror` jobs.
