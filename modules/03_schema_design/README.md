# Module 03 — Tool Schema Design

**Goal:** write tool definitions Claude uses correctly on the first try, and errors it can recover from.

**Exam topics:** JSON Schema for tool inputs, naming, descriptions, enums and constraints, `required`, error handling in tool results.

## Concepts

Claude only knows your tool through its **name, description and input schema**. A vague schema causes wrong calls, invented argument values and retries that cost tokens. Good schemas:

- Use clear `snake_case` verb names: `search_tickets`, not `doStuff`.
- Have descriptions that say **what** the tool does, **when** to use it, and **what it returns** (3–4 sentences is normal).
- Constrain values with `enum`, `pattern`, `minimum`/`maximum`, and the right type (`integer`, not `number`, for counts).
- Mark only truly necessary fields as `required`; make filters optional.
- Describe every property, including its format, e.g. "Ticket ID like NW-104".
- Set `additionalProperties: false` so invented arguments are rejected.

And when a call fails, return an error **Claude can act on**: `"Unknown status 'pending'. Use one of: open, in_progress, resolved, closed"` instead of `"bad input"`.

## Exercises

1. Read `bad_schemas.py`. For each of the three tools, write down every problem you find (there are at least 10 in total).
2. In `starter.py`, fill in `TOOLS`: two well-designed Claude API tool definitions, `search_tickets` and `get_ticket`, that replace all three bad ones. (Why two, not three? Two of the bad tools are really the same capability.)
3. Implement `search_tickets(...)` and `get_ticket(...)` in `starter.py`, with the validation and error messages described in the docstrings.

```bash
pytest modules/03_schema_design
```

## Stretch

Paste a bad and a good schema into the Claude API (Workbench or a quick script) with the question *"Which critical tickets are open in Engineering?"* and compare the tool calls Claude makes.

## Check your understanding

- When would you split one tool into two, and when would you merge two into one?
- Why raise an error with the allowed values instead of silently returning `[]`?
