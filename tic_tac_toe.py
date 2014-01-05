from pprint import pprint
from copy import deepcopy
import random
import sys

X = "X"
O = "0"
E = " "

STATE_COMPONENTS = (
        #(0, 0),
        #(0, 1),
        (0, 2),
        (0, 3),
        #(1, 0),
        #(1, 1),
        #(1, 2),
        (2, 0),
        #(2, 1),
        (3, 0),
        None,
    )

class Spot(object):
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __str__(self):
        return "row: {self.row} col: {self.col}".format(self=self)


class StateChart(object):
    def __init__(self, iterations, cycles):
        self.states = {}
        for it in xrange(iterations):
            for cycle in xrange(cycles):
                if cycle % 10 == 0:
                    print >> sys.stdout, "{it:>2}: {cycle:>3}\r".format(
                            it=it, cycle=cycle),
                    sys.stdout.flush()
            self.update_probabilities()

    def get_prob(self, state):
        if isinstance(state, dict):
            state = StateChart.state_dict_to_tuple(state)
        if state not in self.states:
            return 0.5
        else:
            return self.states[state]['win_prob']

    def state_seen(self, state, player, winner):
        if isinstance(state, dict):
            state = StateChart.state_dict_to_tuple(state)
        if state not in self.states:
            self.states[state] = {
                    'player': player, 'win_prob': 0.5, X: 0, O: 0, E: 0}
        self.states[state][winner] += 1

    def update_probabilities(self):
        for state_info in self.states.values():
            wins = float(state_info[state_info['player']])
            total = state_info[X] + state_info[O] + state_info[E]
            state_info['win_prob'] = wins / total

    def clear_history(self):
        for state_info in self.states.values():
            state_info['wins'] = 0
            state_info['losses'] = 0

    @staticmethod
    def state_dict_to_tuple(state_dict):
        return tuple(state_dict[state] for state in STATE_COMPONENTS)


class Board(object):
    def __init__(self, state_chart, predefine=None):
        self.state_chart = state_chart
        self.board = {(r, c): E for r in range(3) for c in range(3)}
        self.player = X
        if predefine:
            self.player = X
            for a in range(3):
                for b in range(3):
                    self.board[a, b] = predefine[3 * a + b]
                    if self.board[a, b] != E:
                        self.player = X if self.player == O else O
        self.moves = []

    def copy(self):
        pass

    def at(self, spot):
        return self.board[spot.row, spot.col]

    def state(self):
        # Since these represent states, we need to be able to account for
        # the case where we have a win. Furthermore, the total number of
        # entries in a trio cannot exceed 3.
        s = {state: 0 for state in STATE_COMPONENTS}

        # Account rows
        for c in range(3):
            s[Board.identify_trio(
                    tuple(self.board[r, c] for r in range(3)))] += 1

        # Account cols
        for r in range(3):
            s[Board.identify_trio(
                    tuple(self.board[r, c] for c in range(3)))] += 1

        # Account down diagonal
        s[Board.identify_trio(
                tuple(self.board[x, x] for x in range(3)))] += 1

        # Account up diagonal
        s[Board.identify_trio(
                tuple(self.board[2 - x, x] for x in range(3)))] += 1

        return s

    def get_next_states_probs(self):
        """Returns lose_prob for the next player at each adjacent state."""
        next_states = {}
        # This is changed in self.move
        true_next_player = self.player
     #  print 'next:', true_next_player
        for coords in [(r, c) for r in range(3) for c in range(3)]:
            spot = Spot(*coords)
            if self.at(spot) == E:
            #   print 'NEXT:', self.player
                self.move(spot)
                next_states[spot] = self.state_chart.get_prob(self.state())
            #   print self
            #   print next_states[spot]
            #   raw_input()
                self.board[spot.row, spot.col] = E
                self.moves.pop()
                self.player = true_next_player
        return next_states

    def get_weighted_move(self):
        next_states_lose_probs = self.get_next_states_probs()
        total = sum(next_states_lose_probs.values())
        cdf = random.uniform(0, total)
        for spot, prob in next_states_lose_probs.items():
            if cdf <= prob:
                return spot
            else:
                cdf -= prob
        assert False, "No move picked by get_weighted_move()"

    def move(self, spot):
        if self.board[spot.row, spot.col] == E:
            self.board[spot.row, spot.col] = self.player
            self.moves.append(spot)

            if self.player == X:
                self.player = O
            else:
                self.player = X
        else:
            assert False, "Illegal move attempted."

    def game_is_over(self):
        s = self.state()
        if self.board.values().count(E) == 0 or s[3, 0] >= 1 or s[0, 3] >= 1:
            return True
        return False

    def winner(self):
        s = self.state()
        if s[3, 0] >= 1:
            return X
        elif s[0, 3] >= 1:
            return O
        else:
            return E

    def __str__(self):
        row_to_str = lambda row: "|".join(
                ["{0:>2}".format(self.board[row, c]) for c in range(3)])
        return "\n--+--+--\n".join(row_to_str(r) for r in range(3))

    @staticmethod
    def identify_trio(trio):
        ident = trio.count(X), trio.count(O)
        return ident if ident in STATE_COMPONENTS else None

def iteration(state_chart):
    board = Board(state_chart)
    while not board.game_is_over():
        board.move(board.get_weighted_move())

    winner = board.winner()
    if winner != E:
        replay_board = Board(None)
        # Now update the win/loss counts.
        for spot in board.moves:
            replay_board.move(spot)
            state_chart.state_seen(
                    replay_board.state(), replay_board.player, winner)
    return winner

def interactive(human, state_chart):
    pprint({k: v for k, v in state_chart.states.items()})
    board = Board(state_chart)
    while not board.game_is_over():
        print board.player, StateChart.state_dict_to_tuple(board.state()), state_chart.get_prob(board.state())
        if board.player == human:
            print
            print "HUMAN"
            print state_chart.get_prob(board.state())
            print board
            try:
                r, c = map(int, raw_input("Move (row, col): ").split())
                board.move(Spot(r, c))
            except (AssertionError, ValueError):
                pass
        else:
            print
            print "AI"
            print board
            next_states_win_probs = board.get_next_states_probs()
            total = sum(next_states_win_probs.values())
            print "Next state lose probs (for human player)"
            pprint({str(k): v for k, v in next_states_win_probs.items()})
            print "total win_probs:", total
            board.move(board.get_weighted_move())

    print "Game over!"
    print board

def main():
    state_chart = StateChart(2, 100)

    board = Board(state_chart)
    board.move(Spot(0, 0))
    board.move(Spot(0, 1))
    board.move(Spot(1, 0))

    print
    print "AI"
    print board
    next_states_win_probs = board.get_next_states_probs()
    total = sum(next_states_win_probs.values())
    print "Next state lose probs (for human player)"
    pprint({str(k): v for k, v in next_states_win_probs.items()})
    print "total win_probs:", total
    print board.get_weighted_move()

    #interactive(X, state_chart)

if __name__ == '__main__':
    state_chart = StateChart(2, 100)
    board = Board(state_chart, "O X"
                               "OXO"
                               " XX")
    print board
    print board.get_next_states_probs()
    print board.get_weighted_move()
    #main()

