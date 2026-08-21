# Start a translation

1. Decide whether you are using a local repository-aware agent or a hosted web agent.
2. Give that agent the corresponding bootstrap prompt: `LOCAL.md` or `WEB.md`.
3. Answer two required questions:
   - Which work do you want to translate?
   - What exact target language, locale, script, and orthographic standard should the edition use?
4. Review the agent's report on existing editions, active work, source availability, and license/build requirements.
5. If the source is eligible, obtain the exact source archive or repository commit named by the agent and add it to the project.
6. Do not begin translation until `SOURCE.json` contains exact immutable source identities and the unchanged baseline build has been attempted.

If a chosen work is already active, you may choose a different target language or declare an independently useful parallel edition. Do not overwrite another edition. If the source or derivative rights are incomplete, the valid job is source preflight—not translation.
