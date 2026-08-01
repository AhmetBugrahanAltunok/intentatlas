# Guided local demo

Run the downstream recommendation and presentation regression scenario without preparing or
scanning a repository:

```console
intentatlas demo
```

The command opens the production local viewer with an original twelve-node same-file
counterexample. Open **Change report** to see the exact-symbol requirement evidence and the single selected
`tests/test_auth_rotation.py` candidate. Then compare the graph's independent
`record_login_audit` symbol, `Preserve login audit events` requirement, and
`tests/test_auth_audit.py`, which is visible in the graph but absent from the ranked test panel.
The panel's advisory explains that omission is not proof of no impact or no test need. The ordinary
**Relationships** and **Evidence paths** sections expose every direct typed link and bounded
structural path.

For a deterministic terminal or machine-readable tour that exits without starting a listener:

```console
intentatlas demo --report text
intentatlas demo --report json
```

The example demonstrates:

- Requirement → Decision → Issue → Pull Request delivery context;
- Decision/Issue → Code implementation links;
- File → Symbol structure and Test → Code verification links;
- Evidence → Test and Evidence → Commit proof/history links;
- Commit → File and Commit → Symbol change impact;
- an advisory medium-confidence recommendation for `tests/test_auth_rotation.py`;
- an independent requirement, symbol, and test in the same `src/auth.py` file that are not promoted
  by the available exact-symbol evidence.

Evidence paths are deterministic shortest structural paths in either graph direction. They are
bounded to depth 6, 800 visited nodes, and 6 results. A path explains why two graph records are
connected; it does not prove causality, label completeness, evidence freshness, or that a test is
required.

The synthetic graph and its evidence edges are prebuilt. The demo exercises the production graph,
recommendation, Change Report, rendering, and viewer contracts after evidence exists; it does not
exercise repository discovery, AST parsing, or Git diff extraction. It does not read the current
directory, execute project code, access the network, or persist its graph in the repository. It
serves the temporary graph and production-shaped report on loopback and removes the graph when the
viewer stops. Use `Ctrl+C` in the terminal to stop it. Report mode does not bind a port or open a
browser. Neither mode claims that omitted requirements are unaffected or omitted tests are
unnecessary.

For a real local repository, continue with:

```console
intentatlas init /absolute/path/to/your-project
intentatlas scan /absolute/path/to/your-project
intentatlas open /absolute/path/to/your-project
```

On Windows, use an explicit target such as `C:\path\to\your-project`. The explicit path keeps the
IntentAtlas source checkout from being initialized by accident.
