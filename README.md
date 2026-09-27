# NetHack identity portfolio

This deterministic player selects a source bot for each of NetHackers' 73 starting
characters. On its first two actions it opens and closes NetHack's attributes
screen to read the starting role, race, alignment, and sex without advancing
the game turn. `identity-choices.json` contains the routing table.

The source packages are renamed to keep their Python imports separate.
`nethackers.solution.json` lists every upstream commit used by this portfolio.
The underlying AutoAscend code carries the license in `LICENSE`; consult the
linked upstream repositories for their additional notices.
