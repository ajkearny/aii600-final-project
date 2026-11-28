# Proposal

At most one page. Replace the prompts under each heading. Leave the headings.

## Hypothesis

Among two-colour limited decks, a deck's probability of winning a game is highest at a middle average mana value.

The quantity we will estimate is a deck's game win probability: games won divided by games played, a number between 0 and 1. It is measured per deck in Bloomburrow (BLB) Premier Draft, for games played from 2024-07-30 to 2024-09-03.

## Data

**Source.** Game results come from the public draft datasets published by 17lands (17lands.com). Card attributes (mana value, card type, colours) come from Scryfall (the Oracle Cards file dated 2026-11-16), joined to the decklists by card name.

**Unit of observation.** The raw rows are individual games, each with the deck played and a win or loss. We group them by deck, so the unit we model is one deck and its games won out of games played. A deck is one build of a draft pool, and a player who rebuilds between matches produces more than one deck from the same draft.

**Sample size and time span.** 526,475 games from 106,900 decks (from 90,671 drafts) in Bloomburrow (BLB) Premier Draft, played from 2024-07-30 to 2024-09-03, after keeping only two-colour decks with no splash. The full 17lands file for this set has 931,230 games from 160,150 drafts before that filter.

**How the data were collected.** Players who run the 17lands tracker alongside Magic Arena upload their own draft picks and games. The data is voluntary and self-reported by the software, not a designed sample.

**How the measurement differs from what the decision needs.** The decision is what deck a player should bring to the tournament in order to increase their chances of winning, and we measure Arena draft games.

- *Bias:* 17lands users are a self-selected, more skilled group than the average player, and a deck's average mana value is tangled up with player skill, colour pair and the strength of the cards drafted. A raw relationship between mana value and win rate is therefore biased, not just noisy. We control for what the data record (for example a skill measure, if available) and state the rest as a limit.
- *Noise:* a deck with few games has a win rate with a wide standard error, so we weight by games played or drop decks below a minimum count.
- *Format:* Premier Draft is best-of-one, so one game is one match. A real tournament may be best-of-three, so the model is not directly measuring that format.

**Republishing.** 17lands data: licensed under CC BY 4.0, which allows republishing with credit to 17lands, a link to the licence and a note of any changes. Scryfall: its terms do not allow its data to be repackaged or republished. MTGJSON is not used. Because we need both sources and Scryfall cannot be republished, no data files are on GitHub and there is no release tagged `data`. `data/README.md` gives the commands that download both files from their sources, and the SHA-256 of each file.

## Decision affected by the model

`log(p / (1 - p)) = b0 + b1*m + b2*m^2 + b3*c + b4*c^2 + b5*L + b6*L^2 + (colour pair effect)`

This is logistic regression. The left side is the log-odds of winning a game, so the predicted win probability p = 1 / (1 + e^-(right side)) always stays between 0 and 1. Each deck is fitted as games won out of games played, so decks with more games count more.

- p = the predicted probability that the deck wins a game
- m = average mana value of the nonland cards
- m^2 = adds curvature so the win probability can peak and fall
- c = number of creatures
- c^2 = lets the effect of creatures bend as well
- L = number of lands
- L^2 = adds curvature for lands
- colour pair = one effect for each of the 10 two-colour pairs, compared with a reference pair
- b0 to b6 = the numbers the model estimates. b1 and b2 are the coefficients on m and m^2. For a curve that bends down (b2 < 0), the best value of m is `-b1 / (2*b2)`.

**Who acts.** A player building a 40-card deck to play with in a tournament.

**What they do differently.** Without the model, they build by feel. With it, they choose four things from the model's predicted win probability, using only values that real decks use:
- *Lands (L):* the number with the highest predicted win probability. On the current split this is 16, a real peak.
- *Average mana value of nonland cards (m):* as low as their pool allows. The predicted win probability falls steadily as m rises, with no peak in the middle.
- *Creatures (c):* as many as their pool allows. The predicted win probability rises with creature count past about 13.
- *Colour pair:* the pair with the highest predicted win probability, or either of the top two if they cannot be told apart. The colour pair is often set by what was drafted, so this matters most as a tiebreaker.

If two builds are possible from the same pool, they bring the one with the higher predicted game win probability.

**Which mistake costs more.** We expected that building a deck that is too expensive costs more than one that is a little too cheap. A high-curve deck has dead cards in hand in the early turns, and a fast opponent can win before it gets going. A deck that is a little too cheap still functions, just with less power. The fitted curves partly support this. Predicted win probability falls about 0.25 wins per 100 games for every 0.1 of average mana value, and within the range of real decks there is no too-cheap side, because the cheapest decks do best. For lands, 15 costs more than 17 (about 1.6 wins per 100 games below the peak at 16, against 0.4). The effect of the creature count is smaller. These curves come from observed decks, not an experiment, so part of the pattern may come from the strength of the cards, not from mana value, lands or creatures themselves. We state that as a limit and report the result either way.

**Loss.** Premier Draft is best-of-one, so one game stands for one match. With p the predicted probability of winning a game:

loss = 1 - p

We score it in wins per 100 games, in two ways:
- *Accuracy:* on average, how far the predicted win rate is from the actual win rate, over decks the model has not seen.
- *Value:* the actual win rate of unseen decks that follow the model's advice, minus the actual win rate of decks that followed the baseline of always running 17 lands. This is the extra wins per 100 games.
