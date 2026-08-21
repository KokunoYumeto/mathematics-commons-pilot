# Start a translation

1. Decide whether you are using a local repository-aware agent or a hosted web agent.
2. Give that agent the corresponding bootstrap prompt: `LOCAL.md` or `WEB.md`.
3. Answer two required questions:
   - Which mathematical work do you want to translate? Give its title and, if available, its public source URL or semantic catalog key.
   - What exact target language, locale, script, and orthographic standard should the edition use?
4. Review the agent's report on work-specific verified editions, reported but unverified editions, source availability, and license/build requirements.
5. If the source is eligible, obtain the exact source archive or repository commit named by the agent and add it to the project.
6. Do not begin translation until `SOURCE.json` contains exact immutable source identities and the unchanged baseline build has been attempted.

The listed works are suggestions, not a closed curriculum. You may propose another mathematical work with a verifiable open source and derivative license. If a chosen work already has activity in the requested language, you may choose another language or declare an independently useful parallel edition. Do not overwrite another edition. If the source or derivative rights are incomplete, the valid job is source preflight—not translation.
