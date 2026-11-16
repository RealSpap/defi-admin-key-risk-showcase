# watch-data

This branch holds the two files the daily Watch writes: status.json (the state of the last run) and snapshot.json (the authorities it read).
It only grows: nothing rewrites it and nothing forces it. The code, the registry and the findings are on main.
See docs/data-contract.md on main for who reads what.
