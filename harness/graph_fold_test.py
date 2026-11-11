"""Differential tests pinning the two knowledge-graph ledger folds together.

`pi/graph.py` owns the teaching-side fold; `state/scripts/ops.py` keeps a second
copy for target-liveness checks. Two copies are a deliberate trade (the state
side must not import the pi layer), so the risk is a fix landing in one and not
the other. Every test here runs BOTH copies over the same synthetic ledger and
asserts they agree — and that both agree with an independently written oracle.

Nothing touches the real `state/` checkout or the live learner tree: each case
builds its own TemporaryDirectory with a `Knowledge Wiki/graph/` ledger inside.

Run with: python3 -m unittest discover -s harness -p '*_test.py'
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GRAPH_MODULE_PATH = REPO_ROOT / "pi" / "graph.py"
OPS_MODULE_PATH = REPO_ROOT / "state" / "scripts" / "ops.py"
GRAPH_DIR = Path("Knowledge Wiki") / "graph"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pi_graph = load_module("pi_graph_under_test", GRAPH_MODULE_PATH)
ops = load_module("state_ops_under_test", OPS_MODULE_PATH)


def oracle_fingerprint(premises, conclusion):
    """Independent restatement of the chain fingerprint both copies must match."""
    body = "\n".join(sorted(set(premises))) + "\n=>\n" + conclusion
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def oracle_chain_id(premises, conclusion):
    return "arg_" + oracle_fingerprint(premises, conclusion)[:10]


NODE_A = "n_ab12cd34ef"
NODE_B = "n_ffffffffff"
NODE_C = "n_cccccccccc"
CHAIN_A = "arg_ab12cd34ef"
CHAIN_B = "arg_zzzzzzzzzz"


def render(lines):
    """Render ledger lines: dicts as JSON, strings verbatim (comments, junk)."""
    rendered = []
    for item in lines:
        if isinstance(item, str):
            rendered.append(item)
        else:
            rendered.append(json.dumps(item, ensure_ascii=False, sort_keys=True))
    return "\n".join(rendered) + "\n"


def write_ledgers(root, nodes=None, chains=None):
    ledger = root / GRAPH_DIR
    ledger.mkdir(parents=True, exist_ok=True)
    if nodes is not None:
        (ledger / "nodes.jsonl").write_text(render(nodes), encoding="utf-8")
    if chains is not None:
        (ledger / "chains.jsonl").write_text(render(chains), encoding="utf-8")


def pi_folded_ids(root):
    """The live-id set implied by pi/graph.py's fold: nodes plus chains, minus
    the retracted tombstones."""
    loaded = pi_graph.load(root)
    node_ids = set(pi_graph._live_nodes(loaded))
    chain_ids = {chain["id"] for chain in pi_graph._live_chains(loaded)}
    return node_ids | chain_ids


# Every row is one synthetic ledger plus the live-id set the fold must produce.
# The expected sets are derived from the documented fold semantics, not from
# running the code, so a shared bug cannot hide behind agreement.
LEDGER_CASES = (
    (
        "define then retract then define revives",
        [
            {"id": NODE_A, "op": "define", "name": "A"},
            {"id": NODE_A, "op": "retract", "reason": "wrong claim"},
            {"id": NODE_A, "op": "define", "name": "A corrected"},
        ],
        [],
        {NODE_A},
    ),
    (
        "node retract without a define is never live",
        [{"id": NODE_A, "op": "retract", "reason": "never existed"}],
        [],
        set(),
    ),
    (
        "link before define does not create a node",
        [{"id": NODE_A, "op": "link", "statement": "an alias"}],
        [],
        set(),
    ),
    (
        "link after retract does not revive",
        [
            {"id": NODE_A, "op": "define", "name": "A"},
            {"id": NODE_A, "op": "retract", "reason": "wrong claim"},
            {"id": NODE_A, "op": "link", "statement": "an alias"},
        ],
        [],
        set(),
    ),
    (
        "duplicate define keeps one live id",
        [
            {"id": NODE_A, "op": "define", "name": "A"},
            {"id": NODE_A, "op": "define", "name": "A again"},
        ],
        [],
        {NODE_A},
    ),
    (
        "unknown node op is ignored",
        [
            {"id": NODE_A, "op": "frobnicate"},
            {"id": NODE_B, "op": "define", "name": "B"},
        ],
        [],
        {NODE_B},
    ),
    (
        "uppercase node id is rejected",
        [
            {"id": "n_AB12CD34EF", "op": "define", "name": "Upper"},
            {"id": NODE_B, "op": "define", "name": "B"},
        ],
        [],
        {NODE_B},
    ),
    (
        "chain assert then retract then assert revives",
        [],
        [
            {"id": CHAIN_A, "op": "assert", "premises": [NODE_A], "conclusion": NODE_B},
            {"id": CHAIN_A, "op": "retract", "reason": "fix the gloss"},
            {"id": CHAIN_A, "op": "assert", "premises": [NODE_A], "conclusion": NODE_B},
        ],
        {CHAIN_A},
    ),
    (
        "a new chain reusing a tombstoned id does not revive it",
        [],
        [
            {"id": CHAIN_A, "op": "retract", "reason": "never asserted"},
            {"id": CHAIN_A, "op": "assert", "premises": [NODE_A], "conclusion": NODE_B},
        ],
        set(),
    ),
    (
        "chain retract without id is ignored",
        [],
        [
            {"id": CHAIN_B, "op": "assert", "premises": [NODE_A], "conclusion": NODE_B},
            {"op": "retract", "reason": "no id to tombstone"},
        ],
        {CHAIN_B},
    ),
    (
        "chain without an id is content addressed",
        [],
        [{"op": "assert", "premises": [NODE_A, NODE_B], "conclusion": NODE_C}],
        {oracle_chain_id([NODE_A, NODE_B], NODE_C)},
    ),
    (
        "chain with an empty premise list is invalid",
        [{"id": NODE_A, "op": "define", "name": "A"}],
        [{"id": CHAIN_A, "op": "assert", "premises": [], "conclusion": NODE_A}],
        {NODE_A},
    ),
    (
        "re-assert with a new gloss keeps the first chain id",
        [],
        [
            {
                "op": "assert",
                "premises": [NODE_A],
                "conclusion": NODE_B,
                "statement": "first gloss",
            },
            {
                "id": CHAIN_B,
                "op": "assert",
                "premises": [NODE_A],
                "conclusion": NODE_B,
                "statement": "corrected gloss",
            },
        ],
        {oracle_chain_id([NODE_A], NODE_B)},
    ),
    (
        "chain with an uppercase id falls back to content addressing",
        [],
        [{"id": "arg_ZZZZZZZZZZ", "op": "assert", "premises": [NODE_A], "conclusion": NODE_B}],
        {oracle_chain_id([NODE_A], NODE_B)},
    ),
    (
        "unknown chain op is ignored",
        [],
        [
            {"id": CHAIN_A, "op": "assert", "premises": [NODE_A], "conclusion": NODE_B},
            {"id": CHAIN_B, "op": "frobnicate", "premises": [NODE_A], "conclusion": NODE_C},
        ],
        {CHAIN_A},
    ),
    (
        "comment and blank lines are ignored",
        [
            "# nodes header",
            "",
            "   ",
            '{"id": "n_ab12cd34ef", "op": "define", "name": "A"}',
        ],
        ["# chains header", ""],
        {NODE_A},
    ),
    (
        "a malformed JSON line cannot make an id live",
        [
            '{"id": "n_ab12cd34ef", "op": "define", "name": "A"}',
            "{not json at all",
        ],
        ['{"id": "arg_ab12cd34ef", "op": "assert", "premises": '],
        {NODE_A},
    ),
    (
        "non-object JSON lines are ignored",
        ['["not", "a", "record"]', "42", {"id": NODE_B, "op": "define", "name": "B"}],
        [],
        {NODE_B},
    ),
    (
        "a missing graph directory has no live ids",
        None,
        None,
        set(),
    ),
)


class HelperParityTest(unittest.TestCase):
    """The duplicated constants and id helpers must be the same values."""

    def test_graph_dir_constant_is_shared(self):
        self.assertEqual(Path(pi_graph.GRAPH_DIR), GRAPH_DIR)
        self.assertEqual(ops.GRAPH_DIR, GRAPH_DIR)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(pi_graph.graph_dir(root), root / ops.GRAPH_DIR)

    def test_ledger_filenames_are_shared(self):
        self.assertEqual(pi_graph.NODES_FILE, "nodes.jsonl")
        self.assertEqual(pi_graph.CHAINS_FILE, "chains.jsonl")
        self.assertEqual(ops.GRAPH_NODES_FILE, pi_graph.NODES_FILE)
        self.assertEqual(ops.GRAPH_CHAINS_FILE, pi_graph.CHAINS_FILE)

    def test_chain_fingerprint_matches_across_copies_and_oracle(self):
        samples = (
            ([NODE_A], NODE_B),
            ([NODE_B, NODE_A, NODE_A], NODE_C),
            ([], NODE_C),
            ([NODE_A, "arg_zzzzzzzzzz"], "n_ünicode ⟹ concl"),
        )
        for premises, conclusion in samples:
            with self.subTest(premises=premises, conclusion=conclusion):
                expected = oracle_fingerprint(premises, conclusion)
                self.assertEqual(pi_graph.chain_fingerprint(premises, conclusion), expected)
                self.assertEqual(ops._chain_fingerprint(premises, conclusion), expected)

    def test_chain_id_matches_across_copies_and_oracle(self):
        samples = (
            ([NODE_A], NODE_B),
            ([NODE_B, NODE_A], NODE_C),
            ([NODE_B, NODE_C], NODE_A),
        )
        for premises, conclusion in samples:
            with self.subTest(premises=premises, conclusion=conclusion):
                expected = oracle_chain_id(premises, conclusion)
                self.assertEqual(pi_graph.chain_id(premises, conclusion), expected)
                self.assertEqual(ops._chain_id(premises, conclusion), expected)
                self.assertRegex(ops._chain_id(premises, conclusion), r"^arg_[0-9a-f]{10}$")

    def test_id_grammar_agrees(self):
        accepted = (
            "n_ab12cd34ef",
            "arg_ab12cd34ef",
            "n_000000",
            "arg_zzzzzzzzzz",
        )
        rejected = (
            "n_AB12CD34EF",
            "arg_AB12CD34EF",
            "n_abc",
            "n_",
            "ab12cd34ef",
            "arg-abc123",
            "n_abc-def",
            "N_ab12cd34ef",
        )
        for ident in accepted:
            with self.subTest(ident=ident, accepted=True):
                self.assertIsNotNone(pi_graph.ID_RE.fullmatch(ident))
                self.assertIsNotNone(ops.GRAPH_TARGET_RE.match(ident))
        for ident in rejected:
            with self.subTest(ident=ident, accepted=False):
                self.assertIsNone(pi_graph.ID_RE.fullmatch(ident))
                self.assertIsNone(ops.GRAPH_TARGET_RE.match(ident))


class LedgerFoldParityTest(unittest.TestCase):
    """Both folds must return the same live-id set for every ledger shape."""

    def assert_folds_agree(self, root, expected):
        pi_ids = pi_folded_ids(root)
        ops_ids = ops.live_graph_ids(root)
        self.assertEqual(ops_ids, pi_ids, "the two graph folds disagree")
        self.assertEqual(pi_ids, set(expected))
        self.assertEqual(ops_ids, set(expected))
        return ops_ids

    def test_ledger_cases_fold_identically(self):
        for name, nodes, chains, expected in LEDGER_CASES:
            with self.subTest(case=name):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    write_ledgers(root, nodes, chains)
                    self.assert_folds_agree(root, expected)

    def test_folding_a_missing_ledger_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(pi_folded_ids(root), set())
            self.assertEqual(ops.live_graph_ids(root), set())
            self.assertFalse((root / GRAPH_DIR).exists())

    def test_a_populated_ledger_is_not_rewritten(self):
        nodes = [
            {"id": NODE_A, "op": "define", "name": "A"},
            {"id": NODE_B, "op": "define", "name": "B"},
        ]
        chains = [{"id": CHAIN_A, "op": "assert", "premises": [NODE_A], "conclusion": NODE_B}]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_ledgers(root, nodes, chains)
            ledger = root / GRAPH_DIR
            before = {
                path.name: path.read_bytes() for path in sorted(ledger.iterdir())
            }
            self.assert_folds_agree(root, {NODE_A, NODE_B, CHAIN_A})
            after = {
                path.name: path.read_bytes() for path in sorted(ledger.iterdir())
            }
            self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
