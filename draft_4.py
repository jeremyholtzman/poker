import pandas as pd
import os
import random
import numpy as np
import collections
import importlib

os.chdir('/Users/jeremyholtzman/Documents/Personal/Poker')

from action_helper_4 import deal_cards, betting, player_balance, evaluate_hands_v2


def action(num_players, button_position, small_blind, big_blind, balance_dict):

    all_players = list(range(num_players))
    cards = deal_cards(num_players)

    blind_order = list(range(num_players))
    if button_position + 3 <= num_players - 1:
        blind_order_first = button_position + 3
    else:
        blind_order_first =  button_position + 3 - num_players
    blind_order = blind_order[blind_order_first:] + blind_order[:blind_order_first]

    print(blind_order)

    post_blind_order = blind_order[-2:] + blind_order[:-2]

    action_df_columns = ['Player ID','Bet Round','Player Action','Cumulative Amount in Round']
    action_df = pd.DataFrame(columns = action_df_columns)

    #dollar_dict, action_df, blind_order = blind_action(blind_order, small_blind, big_blind)
    dollar_dict, action_df, blind_order = betting(blind_order, action_df, small_blind, big_blind, 'pre-flop', cards, balance_dict)
    print('done with blind betting')
    print(blind_order)

    if len(blind_order) > 1:
        #flop betting
        order = [i for i in post_blind_order if i in blind_order]
        dollar_dict, action_df, order = betting(order, action_df ,small_blind, big_blind, 'flop', cards, balance_dict)
        print('done with flop betting')

        if len(order) > 1:

            #turn betting
            order = [i for i in post_blind_order if i in order]
            dollar_dict, action_df, order = betting(order, action_df ,small_blind, big_blind, 'turn', cards, balance_dict)
            print('done with turn betting')

            if len(order) > 1:

                #river betting
                order = [i for i in post_blind_order if i in order]
                dollar_dict, action_df, order = betting(order, action_df ,small_blind, big_blind, 'river', cards, balance_dict)
                print('done with river betting')

    print(action_df)
    return action_df, balance_dict, cards


def start_hand(num_players, small_blind, big_blind):
    balance_dict = player_balance(num_players)

    button_position = 2

    action_df, balance_dict, cards = action(num_players, button_position, small_blind, big_blind, balance_dict)

    print(balance_dict)
    print(action_df)

    if button_position + 1 > num_players - 1:
        button_position = 0
    else:
        button_position += 1

    print('new button position: ' + str(button_position))

    return action_df, cards, balance_dict

def end_hand(action_df, cards, balance_dict):
    hand_score_dict, final_hand_dict = evaluate_hands_v2(action_df, cards)
    top_hands = []
    for player, hand in hand_score_dict.items():
        if hand == max(hand_score_dict.values()):
            top_hands.append(player)

    if len(top_hands) == 1:
        winner = [top_hands[0]]
    else:
        remaining_hand_dict = {key: final_hand_dict[key] for key in top_hands}
        remaining_df = pd.DataFrame(remaining_hand_dict)
        #remaining_df['top_value']=remaining_df.max(axis=1)
        #stuck. still evaluating top cards
        remaining_df = remaining_df.rank(axis=1, ascending = False, method='min')
        remaining_df = remaining_df.transpose()
        for column in remaining_df.columns:
            remaining_df = remaining_df.rank(method='min',ascending=True, axis = 0)
            remaining_df = remaining_df[remaining_df[column]==1.0]
            if len(remaining_df) == 1:
                winner = [remaining_df.index[0]]
                break
        if len(remaining_df>1):
            winner = list(remaining_df.index)

    total_pot = sum(action_df.groupby(['Bet Round','Player ID']).max()['Cumulative Amount in Round'])

    if len(winner)==1:
        balance_dict[winner[0]]+=total_pot
    else:
        for player in winner:
            balance_dict[player]+=round((total_pot.astype(float) / len(winner)),2)

    return action_df, cards, balance_dict, winner, hand_score_dict, final_hand_dict

action_df, cards, balance_dict = start_hand(3, 10, 20)
action_df, cards, balance_dict, winner, hand_score_dict, final_hand_dict = end_hand(action_df, cards, balance_dict)
