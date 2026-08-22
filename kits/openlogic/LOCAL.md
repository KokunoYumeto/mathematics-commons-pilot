# Local use

Unzip the packet into a new directory. Tell the local agent:

> Read `START.md` and follow it exactly. Verify the packet before editing. Keep `source/` byte-identical, ask the required target-language questions, and write all translation work under `target/`.

The agent must verify the manifest before any production action. It must copy `source/` to a disposable `baseline/` directory, reproduce the unmodified build there, record the local toolchain and inherited warnings, delete or retain that disposable build only as local evidence, and reverify that `source/` is byte-identical. It then copies the clean source tree to `target/` and begins with one complete representative unit. It must return the cumulative state defined in `RETURN.md` after every unit.
