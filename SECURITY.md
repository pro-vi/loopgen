# Security

Loopgen is prose that composes prompts for autonomous coding loops. Treat all
skill files, generated prompts, repository content, connector output, and tool
responses as untrusted input until their origin and authority are established.

## Security model

Generated loops may read and modify repository files, run repository-approved
verification, create local commits, and use capabilities explicitly authorized
by their prompt or operator. They must not infer permission to:

- disclose repository or connector data to external models or services;
- copy restricted connector data into tracked files or commits;
- install or execute new packages, plugins, binaries, MCP servers, or remote
  installers;
- access or transmit secrets, credentials, tokens, private keys, personal data,
  or customer data; or
- publish, push, upload, or send messages.

The runtime contract for these rules is
`loopgen/primitives/external-trust-boundary.md`. Contract verification ensures
that it is present in every rendered archetype.

## Reporting a vulnerability

Do not open a public issue containing exploit details, credentials, private
repository content, or personal data. Use GitHub's private vulnerability
reporting feature for this repository when available. If it is unavailable,
contact the repository owner through a private channel listed on their GitHub
profile and include only the minimum information needed to establish contact.

Please include the affected file and section, impact, reproduction conditions,
and a suggested mitigation. Remove secrets and personal or customer data from
all reports.
