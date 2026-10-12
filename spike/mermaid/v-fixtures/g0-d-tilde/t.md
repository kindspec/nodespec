# Support runbook

Tickets are triaged within fifteen minutes during business hours.
Out of hours, only P1 tickets page anyone; everything else waits for the
morning shift. The triager sets the severity, links any duplicates and
assigns an owner before leaving the ticket.

A ticket with no owner after triage is a triage failure, not a queue
problem; raise it in the weekly review. Customers see the severity on
their portal, so set it carefully: downgrading a P1 later needs a note.

## Escalation

Escalate to the duty manager after two hours without a response. For a
P1, escalate after thirty minutes and open an incident channel. Record
every escalation in the ticket so the weekly review can find it.

If the duty manager cannot be reached, call the head of support directly.
Their number is pinned in the support channel. Never close an escalated
ticket yourself; the person who took the escalation closes it once the
customer confirms the fix, and links the incident review if there was one.

## Triage diagram

~~~mermaid
graph TD
  ticket[New ticket] --> sev{Severity}
  sev -->|P1| page[Page on-call]
  sev -->|P2+| queue[Support queue]
~~~
