import pandas as pd
import os
import random
import numpy as np
import collections
import importlib

os.chdir('/Users/jeremyholtzman/Documents/Personal/Poker')
from classes import hands



def player_balance(num_players):

    balance_dict = {}
    minimum_buyin = 100

    for i in range(num_players):

        j = 0
        while j < 5:
            a = input('Player ' + str(i) + ', how much would you like to play with:')

            try:
                a = int(a)
                if a >= minimum_buyin:
                    break
                else:
                    print('that was not high enough. minimum amount is ' + str(minimum_buyin))
                    j+=1
                    #set default to 10k
                    a = 10000
            except ValueError:
                j+=1
                print('must enter a number')
                #set default to 10k
                a = 10000

        balance_dict['Player ' + str(i)] = a

    return balance_dict


def betting(order, action_df, small_blind, big_blind, round, cards, balance_dict):
    #NOTE: Need to fix for all-ins

    turn = order[0]

    dollar_dict = {}
    for player in order:
        dollar_dict[player] = 0

    action_df_columns = list(action_df)

    print('starting balance at beginning of round')
    print(balance_dict)

    if round == 'pre-flop':
        wnba = None
        #blind betting

        if balance_dict[order[-2]] > small_blind:
            dollar_dict[order[-2]]=small_blind
            balance_dict[order[-2]] -= small_blind
            action_df = action_df.append(pd.DataFrame([[order[-2],round,'small blind',small_blind]], columns = action_df_columns))
        else:
            all_in_amount = balance_dict[order[-2]]
            dollar_dict[order[-2]]=all_in_amount
            action_df = action_df.append(pd.DataFrame([[order[-2],round,'small blind - all in',all_in_amount]], columns = action_df_columns))
            balance_dict[order[-2]] = 0

        if balance_dict[order[-1]] > big_blind:
            dollar_dict[order[-1]]=big_blind
            balance_dict[order[-1]] -= big_blind
            action_df = action_df.append(pd.DataFrame([[order[-1],round,'big blind',big_blind]], columns = action_df_columns))
        else:
            all_in_amount = balance_dict[order[-1]]
            dollar_dict[order[-1]]=all_in_amount
            action_df = action_df.append(pd.DataFrame([[order[-1],round,'big blind - all in',all_in_amount]], columns = action_df_columns))
            balance_dict[order[-1]] = 0

    else:
        wnba = turn



    all_actions = ['check','raise','fold','call', 'bet']
    players_left = len(order)
    starting_num_players = players_left
    all_in_amount = 0





    for player in order:
        #print(str("Player {0}".format(i)) + ' has $'+ str(balance_dict["Player {0}".format(i)]) + ' remaining')
        if balance_dict[player] == 0:
            print(str(player) + ' should be taken out')
            order.remove(player)

    #create if statement that checks if only 1 player left after blinds
    if len(order) > 1:

        in_process = True
        while in_process:


            print('player turn')
            print(turn)

            if round == 'pre-flop':
                print(cards[cards['assigned_card'] == turn])
            elif round == 'flop':
                print(cards[(cards['assigned_card'] == turn) | (cards['assigned_card'].isin(['F']))])
            elif round == 'turn':
                print(cards[(cards['assigned_card'] == turn) | (cards['assigned_card'].isin(['F','T']))])
            else:
                print(cards[(cards['assigned_card'] == turn) | (cards['assigned_card'].isin(['F','T','R']))])

            if round == 'pre-flop':
                total_to_call_round = max(max(dollar_dict.values()), big_blind)
            else:
                total_to_call_round = max(dollar_dict.values())

            j = 0
            b = 0
            while j < 10:
                a = input('what would you like to do?')
                if (dollar_dict[turn] < total_to_call_round) & ((a == 'check') or (a == 'bet')):
                    j+=1
                    a = 'fold'
                    print('cannot check or bet. must call, raise, or fold')

                elif (a == 'call' or a == 'bet') & (total_to_call_round > 0) & (dollar_dict[turn] == total_to_call_round):
                    j+=1
                    a = 'fold'
                    print('cannot call or bet. must raise, check, or fold')

                elif (a == 'bet') & (round == 'pre-flop'):
                    j+=1
                    a = 'fold'
                    print('cannot bet. must call, raise, or fold')

                elif (a == 'call' or a == 'raise') & (total_to_call_round == 0):
                    j+=1
                    a = 'fold'
                    print('cannot call or raise. must check, bet, or fold.')

                elif not(a in all_actions):
                    j+=1
                    a = 'fold'
                    print('that was not an option')


                elif (a == 'raise') or (a == 'bet'):
                    wnba = turn
                    print('new wnba - ', wnba)

                    b = input('how much would you like to ' + a)
                    try:
                        b = int(b)
                        if (b >= 2 * total_to_call_round) & (b >= big_blind) & (b <= balance_dict[turn]):
                            break
                        elif b > balance_dict[turn]:
                            print('that was too high. you only have ' + str(balance_dict[turn]))
                            j += 1
                        else:
                            print('that was not high enough. you must ' + a + ' to at least ' + str(max(2 * total_to_call_round, big_blind)))
                            j+=1
                            b = 2 * total_to_call_round
                    except ValueError:
                        j+=1
                        print('must enter a number')


                elif (a == 'call') & (total_to_call_round > balance_dict[turn]):
                    j += 1
                    print('that was too high. you only have ' + str(balance_dict[turn]))

                elif a == 'call':
                    b = total_to_call_round
                    print('here. called. at',b)
                    print('dollar dict:', dollar_dict[turn])
                    break


                elif a == 'check':
                    b = total_to_call_round
                    break

                elif a == 'fold':
                    b = 0
                    break

            if b != 0:
                print('previous balance dict:', balance_dict[turn])
                balance_dict[turn] -= (b - dollar_dict[turn])
                print('current balance dict:', balance_dict[turn])
                print('subtracted out:', (b - dollar_dict[turn]))

                dollar_dict[turn]=b

            action_df = action_df.append(pd.DataFrame([[turn,round,a,b]], columns = action_df_columns))


            if a == 'fold':
                order.pop(0)

                if turn == wnba:
                    wnba = None

            else:
                order = order[1:] + order[:1]

            turn = order[0]

            players_left = len(order)

            print('players left - ', players_left)
            print('wnba - ', wnba)

            players_bet = list(set(action_df[~action_df['Player Action'].isin(['big blind', 'small blind'])]['Player ID']))

            if (wnba == turn or players_left == 1) or (wnba is None and len(players_bet) == starting_num_players):
                in_process = False

    print('balance_dict ---------- ')
    print(balance_dict)
    return dollar_dict, action_df, order

##new evaluate hands

def evaluate_hands_v2(action_df, cards):

    folded_players = list(action_df[action_df['Player Action']=='fold'].loc[:,'Player ID'])
    players = list(set(action_df[~(action_df['Player ID'].isin(folded_players)) ]['Player ID']))

    print(players)

    hand_score_dict = {}
    final_hand_dict = {} #this is player #: [C1, C2, C3, C4, C5]

    for i in players:
        player_df = cards[(cards['assigned_card'] == i) | (cards['assigned_card'].isin(['F','T','R']))]
        print(i, 'has the following:')
        print(player_df)

        #improvement, don't have to run pairs if has royal flush...
        player_hand = hands(player_df).pairs().straight().flush().straight_flush()


        if player_hand.has_straight_flush == True:
            hand_score_dict[i]=8
            final_hand_dict[i]=player_hand.cards_used_straight_flush
        elif player_hand.quads == True:
            hand_score_dict[i]=7
            final_hand_dict[i]=player_hand.cards_used_pairs
        elif player_hand.boat == True:
            hand_score_dict[i]=6
            final_hand_dict[i]=player_hand.cards_used_pairs
        elif player_hand.has_flush == True:
            hand_score_dict[i]=5
            final_hand_dict[i]=player_hand.cards_used_flush
        elif player_hand.has_straight == True:
            hand_score_dict[i]=4
            final_hand_dict[i]=player_hand.cards_used_straight
        elif player_hand.trips == True:
            hand_score_dict[i]=3
            final_hand_dict[i]=player_hand.cards_used_pairs
        elif player_hand.two_pair == True:
            hand_score_dict[i]=2
            final_hand_dict[i]=player_hand.cards_used_pairs
        elif player_hand.one_pair == True:
            hand_score_dict[i]=1
            final_hand_dict[i]=player_hand.cards_used_pairs
        else:
            hand_score_dict[i]=0
            final_hand_dict[i]=player_hand.cards_used_pairs


    return hand_score_dict, final_hand_dict
