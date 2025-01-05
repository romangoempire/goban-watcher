def get_amount_combinations(moves):
    move_amount = moves // 2
    if moves % 2 == 0:
        black_amount, white_amount = move_amount, move_amount
    else:
        black_amount, white_amount = move_amount + 1, move_amount

    black_turn = True
    combinations = 1

    while True:
        if black_amount == 0:
            break
        if black_turn:
            combinations *= black_amount
            black_amount -= 1
            black_turn = False
        else:
            combinations *= white_amount
            white_amount -= 1
            black_turn = True

    return combinations


for i in range(1, 20):
    print(f"Moves {i} \t {get_amount_combinations(i)}")
