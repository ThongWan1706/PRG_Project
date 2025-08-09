import S10275182A_Assignment

def test_winGP():
    assert S10275182A_Assignment.WIN_GP == 500

def test_mine_copper_adds_ore():
    S10275182A_Assignment.player['ore'] = {'copper': 0, 'silver': 0, 'gold': 0}
    S10275182A_Assignment.player['backpack_capacity'] = 10
    S10275182A_Assignment.mine_ore('C')
    assert S10275182A_Assignment.player['ore']['copper'] > 0