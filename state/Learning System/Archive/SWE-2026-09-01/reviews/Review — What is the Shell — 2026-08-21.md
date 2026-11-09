# REVIEW: What is the Shell — 2026-08-21

## Review Info
- **Date:** 2026-08-21
- **Concept:** What is the Shell
- **Last Reviewed:** 2026-08-08
- **Review Interval:** 7d (overdue)
- **Status Before Review:** developing

## Assistant's Prompt
> Discriminative (alternation from last definitional): Decode the prompt `missing:~$ cat notes.txt` — machine name, current directory, and user type. What does `$` (vs `#`) communicate about privileges, and why does that distinction matter for the commands you'd run there?

## Your Answer
- **Confidence:** confident
- **Answer:** The machine name is the hostname (not the username). The tilde `~` is the current directory = home. `$` = a normal (unprivileged) user. `#` = a "guest." The distinction matters because different users get different permission sets — you don't let everyone have the same privileges, to mitigate what untrusted people can do.

## Assistant's Evaluation
- **Result:** Mostly Pass — one misfire (held @7d)
- **Feedback:** Correctly decoded machine name, `~` = home, `$` = normal user, and the least-privilege reasoning. **Misfire:** `#` is NOT a "guest" — it is **root (superuser)**, the account with *maximum* privileges, the opposite of a guest. `$` = restricted normal user; `#` = all-powerful root (can write system files). Core insight: the prompt tells you how dangerous your next command could be — `#` is a warning you're running with destructive power, so you stay a normal `$` user and only escalate via `sudo` when required.
- **Status After Review:** developing

## Updated Concept Record
- **status:** developing (unchanged)
- **last_reviewed:** 2026-08-21
- **next_review:** 2026-08-28 (held @7d)
- **Last Q Type:** discriminative
- **notes:** Mostly pass — decoded machine/~/normal-user; misfire: `#`=root (superuser), not guest.

## Key Takeaway
> In the prompt, `$` = a restricted normal user; `#` = **root/superuser** with near-unlimited (potentially destructive) power — escalate only when you must.
