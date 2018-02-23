import pandas as pd
import os
import random
import numpy as np
import collections
import importlib

os.chdir('/Users/jeremyholtzman/Documents/Personal/Poker')

from action_helper_5 import betting, evaluate_hands_v2
from classes import deal_cards



def action(num_players, button_position, small_blind, big_blind, balance_dict):
    players = list(balance_dict.keys())
    cards = deal_cards(num_players, players).cards().shuffle_and_deal().df

    blind_order = list(balance_dict.keys())
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

def whos_playing():
    more_players = True
    minimum_buyin = 100
    balance_dict = {}
    while more_players:
        counter = 0
        while counter < 5:
            player = input('Who wants to play? - ')
            buyin = input('How much would you like to buy in? - ')
            try:
                buyin = int(buyin)
                if buyin >= minimum_buyin:
                    break
                else:
                    print('that was not high enough. minimum amount is ' + str(minimum_buyin))
                    j+=1
                    #set default to 1k
                    a = 1000
            except ValueError:
                j+=1
                print('must enter a number')
                #set default to 1k
                a = 1000
                counter += 1

        balance_dict[player] = buyin

        more = input('are there more players?')
        if (more != 'y') & (len(balance_dict) > 1):
            more_players = False
        elif (more != 'y'):
            print('not enough players yet. adding more players')

    return balance_dict

def lets_play(small_blind, big_blind):
    balance_dict = whos_playing()
    num_players = len(balance_dict)

    keep_playing = True
    hand_num = 0
    cumulative_action_df = pd.DataFrame() #need to populate this with all action df plus hand num

    while keep_playing:
        if hand_num == 0:
            button_position = random.randint(0,num_players)
        elif button_position + 1 > num_players - 1:
            button_position = 0
        else:
            button_position += 1

        action_df, balance_dict, cards = action(num_players, button_position, small_blind, big_blind, balance_dict)
        action_df, cards, balance_dict, winner, hand_score_dict, final_hand_dict = end_hand(action_df, cards, balance_dict)
        print('winner(s):', winner)
        print('hand scores:', hand_score_dict)
        print('final_hand_dict:', final_hand_dict)
        print('cards:', cards)
        print('balance_dict:', balance_dict)

        user_choice = input('Do you want to continue? (y/n) - ')
        balance_dict = {key: value for key, value in balance_dict.items() if value > 0}

        if (user_choice == 'n') or (len(balance_dict) < 2):
            keep_playing = False
        else:
            hand_num += 1

    return balance_dict
