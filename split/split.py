from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

class Player:
    def __init__(self, player_name):
        self.name = player_name
        self.hands = [1, 1]  # Each hand starts with 1 finger

    def hit(self, opponent, from_hand_index, to_hand_index):
        # Can't hit with a dead hand (5 fingers)
        if self.hands[from_hand_index] == 5:
            return False
            
        # Calculate new total and apply modulus 5 (0 becomes 5)
        total_fingers = (opponent.hands[to_hand_index] + self.hands[from_hand_index]) % 5
        opponent.hands[to_hand_index] = 5 if total_fingers == 0 else total_fingers
        return True

    def can_split(self):
        # Can split only if one hand has even number (2 or 4) and other hand is lost (5)
        return (self.hands[0] == 5 and self.hands[1] in [2, 4]) or \
               (self.hands[1] == 5 and self.hands[0] in [2, 4])

    def split(self):
        if not self.can_split():
            return False
            
        # Find the hand with even numbers (the non-5 hand)
        alive_hand = 1 if self.hands[0] == 5 else 0
        fingers = self.hands[alive_hand]
        
        # Split the fingers evenly
        half = fingers // 2
        self.hands = [half, half]
        return True

    def is_lost(self):
        return self.hands[0] >= 5 and self.hands[1] >= 5

    def to_dict(self):
        return {
            'name': self.name,
            'hands': self.hands,
            'canSplit': self.can_split()
        }

class Game:
    def __init__(self):
        self.player1 = Player("Player 1")
        self.player2 = Player("Player 2")
        self.current_turn = 1  # 1 for player1, 2 for player2
        self.winner = None

    def get_current_player(self):
        return self.player1 if self.current_turn == 1 else self.player2

    def get_opponent(self):
        return self.player2 if self.current_turn == 1 else self.player1

    def make_move(self, from_hand, to_hand):
        if self.winner:
            return False

        current_player = self.get_current_player()
        opponent = self.get_opponent()
        
        if current_player.hit(opponent, from_hand, to_hand):
            if opponent.is_lost():
                self.winner = current_player.name
            else:
                # Always switch turns after a hit
                self.current_turn = 3 - self.current_turn
            return True
        return False

    def try_split(self):
        if self.winner:
            return False

        current_player = self.get_current_player()
        if current_player.split():
            # Turn continues after split - player can still make one hit
            return True
        return False

    def get_state(self):
        return {
            'player1': self.player1.to_dict(),
            'player2': self.player2.to_dict(),
            'currentTurn': self.current_turn,
            'winner': self.winner
        }

# Global game instance
game = Game()

@app.route('/')
def index():
    return render_template('split.html')

@app.route('/game/state')
def get_game_state():
    return jsonify(game.get_state())

@app.route('/game/move', methods=['POST'])
def make_move():
    data = request.get_json()
    success = game.make_move(data['fromHand'], data['toHand'])
    return jsonify({
        'success': success,
        'gameState': game.get_state()
    })

@app.route('/game/split', methods=['POST'])
def make_split():
    success = game.try_split()
    return jsonify({
        'success': success,
        'gameState': game.get_state()
    })

@app.route('/game/reset', methods=['POST'])
def reset_game():
    global game
    game = Game()
    return jsonify(game.get_state())

if __name__ == '__main__':
    app.run(debug=True)