# Guided local demo

Run the complete IntentAtlas product story without preparing or scanning a repository:

```console
intentatlas demo
```

The command opens the production local viewer with an original nine-node example. Start at
`Keep customer sessions secure`, then use **Evidence paths** to move from the requirement through
the decision and delivery work to the changed symbol, test, verification evidence, and commit.
The ordinary **Relationships** section remains available for inspecting every direct typed link.

The example demonstrates:

- Requirement → Decision → Issue → Pull Request delivery context;
- Decision/Issue → Code implementation links;
- File → Symbol structure and Test → Code verification links;
- Evidence → Test and Evidence → Commit proof/history links;
- Commit → File and Commit → Symbol change impact;
- an advisory medium-confidence test recommendation for the example commit.

Evidence paths are deterministic shortest structural paths in either graph direction. They are
bounded to depth 6, 800 visited nodes, and 6 results. A path explains why two graph records are
connected; it does not prove causality, label completeness, evidence freshness, or that a test is
required.

The demo does not read the current directory, execute project code, access the network, or persist
its graph in the repository. It serves a temporary graph on loopback and removes that graph when
the viewer stops. Use `Ctrl+C` in the terminal to stop it.

For a real local repository, continue with:

```console
intentatlas init
intentatlas scan
intentatlas open
```
