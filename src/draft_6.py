import pandas as pd
import os
import random
import numpy as np
import collections
import importlib

os.chdir('/Users/jeremyholtzman/Documents/Personal/Poker/src')

from action_helper_6 import betting, evaluate_hands_v2
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
    blind_order = [x for x in blind_order if balance_dict[x] > 0]
    print('remaining players in action function')
    print(blind_order)
    print('done with blind betting')
    print(blind_order)

    #NOTE: need to fix for all ins
    if len(blind_order) > 1:
        #flop betting
        order = [i for i in post_blind_order if i in blind_order]
        print('order in the action function before calling flop betting')
        print(order)
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
    bet_round_dict = {'pre-flop': 0, 'flop': 1, 'turn': 2, 'river': 3, 'final': 4}
    folded_players = list(set(action_df[action_df['Player Action']=='fold']['Player ID']))
    #num pots is number of all ins at different amounts (in diff rounds) plus 1 if there are any bets after the last all in
    temp = action_df.copy()
    temp = temp.reset_index()
    temp = temp.drop('index', axis = 1)
    #this line is not working
    temp['action_num'] = temp.index + 1
    temp['all_in'] = np.where(temp['Player Action']=='all in',True, False)
    temp['bet_round_num'] = temp['Bet Round'].map(bet_round_dict)
    last_action = temp[temp['Player Action'].isin(['all in','bet','raise'])].groupby(['all_in']).max().loc[:,'action_num']
    num_all_ins = len(temp[temp['all_in']==True])
    if num_all_ins > 0:
        last_action_all_in = last_action[last_action.index==True].iloc[0]
        if len(last_action)>1:
            last_action_reg = last_action[last_action.index==False].iloc[0]
        else:
            last_action_reg = 0
        num_pots = len(temp[temp['Player Action']=='all in'].drop(['Player ID','action_num'],axis=1).drop_duplicates()) + (last_action_reg > last_action_all_in)
    else:
        num_pots = 1

    print(temp)
    players = list(temp['Player ID'].drop_duplicates())
    if num_all_ins > 0:
        all_in_df = temp[temp['all_in']==True].groupby(['Bet Round','Cumulative Amount in Round']).max().loc[:,'action_num']
        all_in_df = all_in_df.reset_index()
        all_pots = 0
        all_in_players = []
        if last_action_reg > last_action_all_in:
            all_in_df = all_in_df.append(pd.DataFrame(columns = ['Bet Round', 'Cumulative Amount in Round', 'action_num'], data = [['final',0,last_action_reg]]))
        all_in_df = all_in_df.sort_values(by = 'action_num')
        for i in range(len(all_in_df)):
            #DEFINED POT SIZES. NEXT: figure out what players can win each pot
            if all_in_df.iloc[i].loc['Bet Round'] != 'final':
                all_in_round = all_in_df.iloc[i].loc['Bet Round']
                all_in_action_num = all_in_df.iloc[i].loc['action_num']
                all_in_amount = all_in_df.iloc[i].loc['Cumulative Amount in Round']
                pot_df = temp[temp['bet_round_num']<=bet_round_dict[all_in_round]]
                pot = 0
                #add in pot from previous round
                round_totals = pot_df.groupby(['bet_round_num','Player ID']).max()['Cumulative Amount in Round']
                round_totals = round_totals.reset_index()
                #add all previous rounds to pot
                pot += sum(round_totals[round_totals['bet_round_num']<bet_round_dict[all_in_round]].loc[:,'Cumulative Amount in Round'])

                #add specific amount from this round to pot
                round_totals = round_totals[round_totals['bet_round_num']==bet_round_dict[all_in_round]]
                round_totals['all_in_amount'] = np.where(round_totals['Cumulative Amount in Round'] > all_in_amount, all_in_amount, round_totals['Cumulative Amount in Round'])
                pot += sum(round_totals.loc[:,'all_in_amount'])

                #subtract out whatever was in a previous pot
                pot -= all_pots

                #add this pot to all pots
                all_pots += pot
            else:
                pot = sum(temp.groupby(['bet_round_num','Player ID']).max()['Cumulative Amount in Round'])-all_pots
                all_pots += pot

            #players that can win. could turn this whole thing into a function FROM HERE:
            print(all_in_players)
            print(folded_players)
            players_left = [x for x in players if x not in all_in_players and x not in folded_players]
            remaining_hand_scores = {key: hand_score_dict[key] for key in players_left}
            top_hands = []
            for player, hand in remaining_hand_scores.items():
                if hand == max(remaining_hand_scores.values()):
                    top_hands.append(player)

            if len(top_hands) == 1:
                winner = [top_hands[0]]
            else:
                #limit dictionary to those who are still left
                remaining_hand_dict = {key: final_hand_dict[key] for key in top_hands}
                #create dataframe of players still left
                remaining_df = pd.DataFrame(remaining_hand_dict)
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
            if len(winner)==1:
                balance_dict[winner[0]]+=pot
            else:
                for player in winner:
                    balance_dict[player]+=round((pot.astype(float) / len(winner)),2)
            #TO HERE

            #all in players
            all_in_players.extend(list(temp[(temp['Bet Round']==all_in_round)&(temp['Cumulative Amount in Round']==all_in_amount)&(temp['all_in']==True)].loc[:,'Player ID']))



            print('pot is worth:', pot)
            print('winner:')
            print(winner)


            print(i)

    else:
        top_hands = []
        for player, hand in hand_score_dict.items():
            if hand == max(hand_score_dict.values()):
                top_hands.append(player)

        if len(top_hands) == 1:
            winner = [top_hands[0]]
        else:
            #limit dictionary to those who are still left
            remaining_hand_dict = {key: final_hand_dict[key] for key in top_hands}
            #create dataframe of players still left
            remaining_df = pd.DataFrame(remaining_hand_dict)
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
                if (buyin >= minimum_buyin) & (not(player in balance_dict)):
                    break
                elif player in balance_dict:
                    print('username already exists. choose a new username')
                    counter+=1
                else:
                    print('that was not high enough. minimum amount is ' + str(minimum_buyin))
                    counter+=1
                    #set default to 1k
                    a = 1000
            except ValueError:
                counter+=1
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
    hand_num = 1
    cumulative_action_df = pd.DataFrame(columns = ['Player ID','Bet Round','Player Action','Cumulative Amount in Round', 'hand_num']) #need to populate this with all action df plus hand num

    while keep_playing:
        num_players = len([x for x in balance_dict if balance_dict[x]>0])
        if hand_num == 1:
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
        action_df['hand_num'] = hand_num
        cumulative_action_df = cumulative_action_df.append(action_df, ignore_index = True)
        print('cumulative action df', cumulative_action_df)

        user_choice = input('Do you want to continue? (y/n) - ')
        balance_dict = {key: value for key, value in balance_dict.items() if value > 0}
        print('balance_dict:', balance_dict)

        if (user_choice == 'n') or (len(balance_dict) < 2):
            keep_playing = False
        else:
            hand_num += 1

    return balance_dict, cumulative_action_df, cards
