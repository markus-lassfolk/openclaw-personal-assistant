# Quick reference: m365-agent-cli

Optional reference when using [`m365-agent-cli`](https://github.com/markus-lassfolk/m365-agent-cli) as the Microsoft 365 implementation. For delegation: EWS commands use `--mailbox`; Graph commands such as `todo`, `planner`, `files`, `findtime` use `--user`. These flags are **not** interchangeable—check `m365-agent-cli <command> --help`.

| Workflow | m365-agent-cli command | Notes |
|---|---|---|
| Scan unread mail | `m365-agent-cli mail inbox --unread [--mailbox <email>]` | EWS — use `--mailbox` for delegated |
| Flag an email | `m365-agent-cli mail --flag <id> [--mailbox <email>]` | EWS |
| Create a draft | `m365-agent-cli drafts --create --to <to> --subject <subj> --body <body> [--mailbox <email>]` | EWS |
| Reply as draft | `m365-agent-cli mail --reply <id> --draft [--mailbox <email>]` | EWS |
| Move email | `m365-agent-cli mail --move <id> --to <folder> [--mailbox <email>]` | EWS |
| Today's calendar | `m365-agent-cli calendar today [--mailbox <email>]` | EWS |
| Week calendar | `m365-agent-cli calendar week [--mailbox <email>]` | EWS |
| Create calendar event | `m365-agent-cli create-event <title> [start] [end] --day <date> [--mailbox <email>]` | EWS — verify flags with `m365-agent-cli create-event --help` |
| Select calendar (Graph) | `m365-agent-cli calendar ... --calendar <id>` | Graph-only selector; use when writing to non-default calendars |
| Find meeting time | `m365-agent-cli findtime [--user <email>]` | Graph — use `--user` for delegated |
| Create a To Do task | `m365-agent-cli todo create --title <title> --due <date> [--user <email>]` | Graph |
| Create a Planner task | `m365-agent-cli planner create-task --plan <plan> --bucket <bucket> --title <title> [--user <email>]` | Graph |
| Download a file | `m365-agent-cli files download <fileId> --out <local_path>` | Graph |
| Upload a file | `m365-agent-cli files upload <local_path> [--folder <folder_id>]` | Graph |
