# Agent Instructions

Follow the repository README first.

Before changing files, read `.agents/STATE.md` if it exists. It is the durable
handoff used when work moves between agents, machines, or command-line tools.

Treat `.agents/` as shared project state, not personal scratch space. Write only
what another teammate or agent needs to continue the work: current task,
decisions, blockers, linked issues or PRs, and safe next steps.

Do not write secrets, credentials, personal details, live tokens, or private
customer/team data into `.agents/`, issues, logs, commits, or generated docs.

Keep `STATE.md` short and current. Put durable decisions in `JOURNAL.md`. Put
detailed resume notes in timestamped files under `.agents/handoffs/` so multiple
people do not overwrite one another.

Keep changes small, explain uncertainty, and prefer pull requests over direct
commits to `main`.
