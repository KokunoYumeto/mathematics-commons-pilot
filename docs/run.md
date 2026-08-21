# Run a transcription job

Each runnable job is a bounded, resumable compute assignment. Its listed release asset part or parts together contain the source authority, exact page map, an ordered prompt file, state templates, manifests, and validation evidence. Prompt counts are workload-derived; there is no global minimum or maximum.

## Before starting

1. Choose a job whose catalog status is `runnable`.
2. Download every asset part listed for the job from the linked GitHub Release.
3. Verify every part's byte length and SHA-256 against `catalog/jobs.json`, then extract all parts into one job directory.
4. Open the exact `start_file` declared for the job in `catalog/jobs.json`, then inspect the bound validation and hardening evidence. Do not substitute a similarly named scan or an earlier packet generation.
5. Use one capable long-context local or hosted AI system. Give it every direct file from the reconstructed job directory.

`strict_pass` means the packet contract and source bundle replayed exactly. It does **not** mean that the edition has already been transcribed, translated, checked, or certified.

Some validation or hardening receipts are exposed as separately bound, path-neutral public projections under `catalog/receipts/`. When `included_in_packet` is `false`, verify the declared public projection instead of treating the absent private-path receipt as missing packet content.

## The exact interaction loop

1. Start with the exact declared `start_file`, then execute Prompt 1 from the exact declared `prompt_file` without rewriting it.
2. If the platform forces a response split and the response says `STATUS: IN_PROGRESS`, preserve its cumulative state and reply only `continue` in the same chat.
3. When that prompt says `STATUS: COMPLETE`, download the returned cumulative state ZIP, checkpoint, and manifest.
4. Reply `next prompt` to advance to the next numbered prompt in the same declared `prompt_file`.
5. Execute every declared prompt in order. The job ends only when its final declared prompt completes after PASS and requests no successor.

After every response, including an IN_PROGRESS response, preserve the returned cumulative state ZIP, checkpoint, and manifest. If the chat or model session must be replaced, attach that trio from the newest response—even if it was IN_PROGRESS. Never reconstruct state from a summary, roll back to the last completed prompt, or continue from memory.

There is no assumed time, runtime, token, response-count, or effort cap. `IN_PROGRESS` is only a platform-forced split, not a timeout or stopping condition. An ordinary `HOLD` or terminal `FAIL` is not an accepted outcome: resolve the defect from the attached authority bytes, record the repair, and run a fresh nonpatching audit until PASS. If a glyph, formula, figure, or table cannot be encoded safely, preserve an exact source crop in the edition, describe it in the apparatus, and continue without guessing or dropping content.

## What the completed job returns

- an editable diplomatic source-language edition;
- a separate standalone English or declared target-language edition;
- a separate restrained apparatus for corrections and mathematical observations;
- source/topology, decision, correction, figure, and build ledgers;
- deterministic source and reader builds;
- the cumulative checkpoint and exact manifest; and
- a fresh, non-patching cold-audit receipt.

The outputs are separate monolingual works. A bilingual or facing-page reader is not an accepted substitute.

## Hand back the result

Keep the final cumulative trio unchanged. Open a repository issue and provide:

- the exact job ID and packet ZIP SHA-256;
- a public immutable result URL or repository commit;
- the result manifest path, bytes, and SHA-256;
- the final prompt/checkpoint state;
- every failed, partial, reversed, or unresolved check; and
- the exact continuation cursor if the job did not reach terminal completion.

Parallel work is welcome. Declare overlap and preserve both inspectable generations instead of silently replacing someone else's work.
