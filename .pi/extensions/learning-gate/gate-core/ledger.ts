/**
 * gate-core/ledger — the receipt + decision ledger.
 *
 * Two append-only NDJSON streams:
 *   - receipts.ndjson  — one line per minted receipt, with provenance.
 *   - decisions.ndjson — one line per gate decision, with the judge's reason.
 *
 * The ledger is the provenance source for the weekly audit, the accountability
 * record for the judge, and the source of test fixtures. It is best-effort: a
 * ledger fault must never block a learning turn.
 *
 * File I/O is injected so the core stays environment-agnostic.
 */
import type { Ledger, LedgerDecision, LedgerReceipt } from "./judge/types.ts";

export type AppendFn = (stream: "receipts" | "decisions", line: string) => void;

export function createLedger(append: AppendFn): Ledger {
  const write = (stream: "receipts" | "decisions", entry: unknown) => {
    try {
      append(stream, JSON.stringify(entry) + "\n");
    } catch {
      /* best effort */
    }
  };
  return {
    receipt(entry: LedgerReceipt) {
      write("receipts", { ...entry, at: entry.at || new Date().toISOString() });
    },
    decision(entry: LedgerDecision) {
      write("decisions", { ...entry, at: entry.at || new Date().toISOString() });
    },
  };
}

export const NOOP_LEDGER: Ledger = {
  receipt() {},
  decision() {},
};
