# Proposal

At most one page. Replace the prompts under each heading. Leave the headings.

## Hypothesis

Among two-colour limited decks, a deck's probability of winning a game is highest at a middle average mana value.

The quantity we will estimate is a deck's probability of winning at least one game at the tournament. It is measured in percentage. The time window is irrelevant for our project.

## Data

**Source.** Game results and the cards in the decks played come from the public draft datasets published by 17lands (17lands.com). Card attributes (mana value, card type, colours) come from Scryfall and MTGJSON, joined to the decklists by card name.

**Unit of observation.** The raw rows are individual games, each with the deck played and a win or loss. We group them by deck, so the units we will model for each deck is the average mana value, the number of lands, and the number of creatures.

**Sample size and time span.** N games from M decks in the game data, after keeping only two-colour decks with no splash.

**How the data were collected.** Players who run the 17lands tracker alongside Magic Arena upload their own draft picks and games. The data is voluntary and self-reported by the software, not a designed sample.

**How the measurement differs from what the decision needs.** The decision is what deck a player should bring to the tournament in order to increase their chances of winning, and we measure Arena draft games.

- *Bias:* 17lands users are a self-selected, more skilled group than the average player, and a deck's average mana value is tangled up with player skill, colour pair and the strength of the cards drafted. A raw relationship between mana value and win rate is therefore biased, not just noisy. We control for what the data record (for example a skill measure, if available) and state the rest as a limit.
- *Noise:* a deck with few games has a win rate with a wide standard error, so we weight by games played or drop decks below a minimum count.
- *Format:* best of one game.

**Republishing** 17lands data: free to share and adapt with license attached. MTGJSON: free to share and adapt with license attached.

## Decision affected by the model

log(P(win)) = b0 + b1m + b2m² + b3c + b4L

m = average mana value
m² = adds curvature so win probablity can peak and fall
c = number of creatures
L = number of lands

**Who acts.** A player building a 40-card deck to play with in a tournament.

**What they do differently.** Without the model, they build by feel. With it, they choose the average mana value of their nonland cards (m), the share of creatures (c), and the number of lands (L) that give the highest predicted win probability, building toward the best average mana value m_best = -b1 / (2*b2). If two builds are possible from the same pool, they bring the one with the higher predicted match win probability.

**Which mistake costs more.** Building a deck that is too expensive. A high-curve deck has dead cards in hand in the early turns, and a fast opponent can win before it gets going. A deck that is a little too cheap still functions, just with less power. We therefore expect the loss to rise faster on the high side of m_best than the low side. The fitted curve will tell us whether that is true, and if it is not, we will say so.

**Loss.** For a best-of-three match, with p the predicted game win probability:
P(win match) = p*p*(3 - 2*p)
loss = 1 - P(win match)
