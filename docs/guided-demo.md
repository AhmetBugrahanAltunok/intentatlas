# Guided local demo

Run the complete IntentAtlas product story without preparing or scanning a repository:

```console
intentatlas demo
```

The command opens the production local viewer with an original twelve-node same-file
counterexample. Start at `feat: rotate authenticated sessions`, inspect the exact
`rotate_session` symbol and recommended `tests/test_auth_rotation.py`, then compare the independent
`record_login_audit` symbol, `Preserve login audit events` requirement, and
`tests/test_auth_audit.py`. The ordinary **Relationships** and **Evidence paths** sections expose
every direct typed link and bounded structural path.

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

The demo does not read the current directory, execute project code, access the network, or persist
its graph in the repository. It serves a temporary graph on loopback and removes that graph when
the viewer stops. Use `Ctrl+C` in the terminal to stop it. Report mode does not bind a port or open
a browser. Neither mode claims that omitted requirements are unaffected or omitted tests are
unnecessary.

For a real local repository, continue with:

```console
intentatlas init
intentatlas scan
intentatlas open
```
