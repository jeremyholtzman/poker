import pandas as pd
import os
import random
import numpy as np
import collections
import importlib

os.chdir('/Users/jeremyholtzman/Documents/Personal/Poker') 


##
#create deck of cards

df = pd.DataFrame()

def cards():
    global df
    num_list = []
    
    for i in range(13):
        num_list.append(i+2)
    
    suit_list = ['spades','diamonds','hearts','clubs']
    
    
    card_list = []
    card_nums = []
    card_suits = []
    
    
    for i in range(0, len(num_list)):
        for j in range(0, len(suit_list)):
            card_list.append(str(num_list[i]) + ' ' + suit_list[j])
            card_nums.append(num_list[i])
            card_suits.append(suit_list[j])
    
    df = pd.DataFrame({'Card Name': card_list, 'Card Num': card_nums, 'Card Suit': card_suits})
    
    
    def card_select(num):
        if num == 14:
            result = 'Ace'
        elif num == 11:
            result = 'Jack'
        elif num == 12:
            result = 'Queen'
        elif num == 13:
            result = 'King'
        else:
            result = str(num)
        
        return result
    
    df['Card Name Adj'] = df['Card Num'].apply(card_select)
    
    return df

##
#deal cards

def deal_cards(num_players):
    global df
    cards()
    #shuffle the deck
    df = df.reindex(np.random.permutation(df.index))
    df = df.reset_index(drop=True)
    
    cards_needed = num_players * 2 + 5
    df = df[:cards_needed]

    
    players = []
    for i in range(num_players):
        players.append(i)
        
    

    assign_card_list = []
    for i in range(num_players):
        assign_card_list.append(i)
        assign_card_list.append(i)
    assign_card_list.append('F')
    assign_card_list.append('F')
    assign_card_list.append('F')
    assign_card_list.append('T')
    assign_card_list.append('R')
    
    df['assigned_card'] = assign_card_list
    
    return df

##
#load player balances into table

def player_balance(num_players):
    
    balance_dict = {}
    
    for i in range(num_players):
        
        j = 0
        while j < 5:
            a = input('Player ' + str(i) + ', how much would you like to play with:')
            
            try:
                a = int(a)
                if a >= 500:
                    break
                else:
                    print('that was not high enough. minimum amount is 500')
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

#balance_dict = player_balance(5)
#print(balance_dict)

##
#blind action

def blind_action(blind_order, small_blind, big_blind, cards, balance_dict):
    wnba = None
    
    dollar_dict = {}
    action_df_columns = ['Player ID','Bet Round','Player Action','Cumulative Amount in Round']
    action_df = pd.DataFrame(columns = action_df_columns)
    
    all_actions = ['bet','check','raise','fold','call']
    players_left = len(blind_order)
    
    #blind betting
    
    if balance_dict["Player {0}".format(blind_order[-1])] > big_blind:
        dollar_dict["Player {0}".format(blind_order[-1])]=big_blind
        balance_dict["Player {0}".format(blind_order[-1])] -= big_blind
        action_df = action_df.append(pd.DataFrame([["Player {0}".format(blind_order[-1]),'pre-flop','big blind',big_blind]], columns = action_df_columns))
    else:
        dollar_dict["Player {0}".format(blind_order[-1])]=balance_dict["Player {0}".format(blind_order[-1])]
        action_df = action_df.append(pd.DataFrame([["Player {0}".format(blind_order[-1]),'pre-flop','big blind - all in',balance_dict["Player {0}".format(blind_order[-1])]]], columns = action_df_columns))
        balance_dict["Player {0}".format(blind_order[-1])] = 0

    
    if balance_dict["Player {0}".format(blind_order[-2])] > small_blind:
        dollar_dict["Player {0}".format(blind_order[-2])]=small_blind
        balance_dict["Player {0}".format(blind_order[-2])] -= small_blind    
        action_df = action_df.append(pd.DataFrame([["Player {0}".format(blind_order[-2]),'pre-flop','small blind',small_blind]], columns = action_df_columns))
    else:
        dollar_dict["Player {0}".format(blind_order[-2])]=balance_dict["Player {0}".format(blind_order[-2])]
        action_df = action_df.append(pd.DataFrame([["Player {0}".format(blind_order[-2]),'pre-flop','small blind - all in',balance_dict["Player {0}".format(blind_order[-2])]]], columns = action_df_columns))
        balance_dict["Player {0}".format(blind_order[-2])] = 0
    
    for i in range(players_left):
        print('in for loop')
        print(balance_dict["Player {0}".format(i)])
        if balance_dict["Player {0}".format(i)] == 0:
            print(str(i) + ' should be taken out')
            blind_order.remove(i)
            
    print(blind_order)
    
    #create if statement that checks if only 1 player left after blinds
    if len(blind_order) > 1:
    
        turn = blind_order[0]
        in_process = True
        while in_process:
    
            
            print('player turn')
            print(turn)
    
            print(cards[cards['assigned_card'] == turn])
            total_to_call_round = max(max(dollar_dict.values()), big_blind)
            
            j = 0
            while j < 10:
                a = input('what would you like to do?')
                if "Player {0}".format(turn) not in dollar_dict:
                    if (a == 'check') or (a == 'bet'):
                        j+=1
                        a = 'fold'
                        print('cannot check or bet. must call, raise, or fold')
                    elif a in all_actions:
                        break
                    else:
                        j+=1
                        a = 'fold'
                
                elif (dollar_dict["Player {0}".format(turn)] < total_to_call_round) & (a == 'check'):
                    j+=1
                    a = 'fold'
                    print('cannot check. must call, raise, or fold')
                    
                elif (dollar_dict["Player {0}".format(turn)] == total_to_call_round) & ((a == 'call') or (a == 'bet')):
                    j+=1
                    a = 'fold'
                    print('cannot call or bet. must check, raise, or fold')
                    
                elif a == 'bet':
                    j+=1
                    a = 'fold'
                    print('cannot bet. must call, raise, or fold')
                
                elif a in all_actions:
                    break
                else:
                    j+=1
                    a = 'fold'
            
            print(a)
            
            if a == 'raise':
                wnba = turn
                print('new wnba')
                print(wnba)
                j = 0
                while j < 10:
                    b = input('how much would you like to raise to?')
                    try:
                        b = int(b)
                        if b >= 2* total_to_call_round:
                            break
                        else:
                            print('that was not high enough. you must raise to at least ' + str(2 * total_to_call_round))
                            j+=1
                            b = 2 * total_to_call_round
                    except ValueError:
                        j+=1
                        print('must enter a number')
                    
                
                if "Player {0}".format(turn) not in dollar_dict:
                    balance_dict["Player {0}".format(turn)] -= b
                else:
                    balance_dict["Player {0}".format(turn)] -= (b - dollar_dict["Player {0}".format(turn)])
                    
                dollar_dict["Player {0}".format(turn)]=b
                
                action_df = action_df.append(pd.DataFrame([["Player {0}".format(turn),'pre-flop',a,b]], columns = action_df_columns))
                
            elif a == 'call':
                if wnba is None:
                    wnba = turn
                
                if "Player {0}".format(turn) not in dollar_dict:
                    balance_dict["Player {0}".format(turn)] -= total_to_call_round
                else:
                    balance_dict["Player {0}".format(turn)] -= (total_to_call_round - dollar_dict["Player {0}".format(turn)])
    
                dollar_dict["Player {0}".format(turn)]=total_to_call_round
                action_df = action_df.append(pd.DataFrame([["Player {0}".format(turn),'pre-flop',a,total_to_call_round]], columns = action_df_columns))
                
            elif a == 'check':
                if "Player {0}".format(turn) not in dollar_dict:
                    action_df = action_df.append(pd.DataFrame([["Player {0}".format(turn),'pre-flop',a,0]], columns = action_df_columns))
                else:
                    action_df = action_df.append(pd.DataFrame([["Player {0}".format(turn),'pre-flop',a,dollar_dict["Player {0}".format(turn)]]], columns = action_df_columns))
            
            if a == 'fold':
                if "Player {0}".format(turn) not in dollar_dict:
                    action_df = action_df.append(pd.DataFrame([["Player {0}".format(turn),'pre-flop',a,0]], columns = action_df_columns))
                else:
                    action_df = action_df.append(pd.DataFrame([["Player {0}".format(turn),'pre-flop',a,dollar_dict["Player {0}".format(turn)]]], columns = action_df_columns))
                
                blind_order.pop(0)
                
            else:
                blind_order = blind_order[1:] + blind_order[:1]
                
            print(blind_order)
            turn = blind_order[0]
            
            players_left = len(blind_order)
    
            print('players left')
            print(players_left)
            print('wnba')
            print(wnba)
            
            if wnba == turn or players_left == 1:
                in_process = False
    
    return dollar_dict, action_df, blind_order
    
#dollar_dict, action_df, test = blind_action([0,1,2,3], 100, 200)
#print(test)

##
#post flop betting

def post_flop_betting(order, action_df, small_blind, big_blind, round, cards, balance_dict):
    turn = order[0]
    dollar_dict = {}
    wnba = turn
    in_process = True
    
    all_actions = ['bet','check','raise','fold','call']
    action_df_columns = ['Player ID','Bet Round','Player Action','Cumulative Amount in Round']
    players_left = len(order)
    
    
    while in_process == True:
        print('player turn')
        print(turn)
        
        if round == 'flop':
            print(cards[(cards['assigned_card'] == turn) | (cards['assigned_card'].isin(['F']))])
        elif round == 'turn':
            print(cards[(cards['assigned_card'] == turn) | (cards['assigned_card'].isin(['F','T']))])
        else:
            print(cards[(cards['assigned_card'] == turn) | (cards['assigned_card'].isin(['F','T','R']))])
        
        if wnba is None:
            wnba = turn
        
        
        if len(dollar_dict) == 0:
            total_to_call_round = 0
        else:
            total_to_call_round = max(dollar_dict.values())
        
        j = 0
        while j < 10:
            a = input('what would you like to do?')
            if "Player {0}".format(turn) not in dollar_dict:
                if (total_to_call_round > 0) & ((a == 'check') or (a == 'bet')):
                    j+=1
                    a = 'fold'
                    print('cannot check. must call, raise, or fold')
                elif (total_to_call_round == 0) & (a == 'raise' or a == 'call'):
                    j+=1
                    a = 'fold'
                    print('cannot raise or call. must check, bet, or fold')
                elif (a in all_actions):
                    break
                else:
                    j+=1
                    a = 'fold'
            elif (dollar_dict["Player {0}".format(turn)] < total_to_call_round) & ((a == 'check') or (a == 'bet')):
                j+=1
                a = 'fold'
                print('cannot check. must call, raise, or fold')
            
            elif a in all_actions:
                break
            else:
                j+=1
                a = 'fold'
                
        if (a == 'raise') or (a == 'bet'):
            wnba = turn
            print('new wnba')
            print(wnba)
            j = 0
            while j < 10:
                b = input('how much would you like to ' + a)
                try:
                    b = int(b)
                    if (b >= 2 * total_to_call_round) & (b >= big_blind) & (b <= balance_dict["Player {0}".format(turn)]):
                        break
                    elif b > balance_dict["Player {0}".format(turn)]:
                        print('that was too high. you only have ' + str(balance_dict["Player {0}".format(turn)]))
                    else:
                        print('that was not high enough. you must ' + a + ' to at least ' + str(max(2 * total_to_call_round, big_blind)))
                        j+=1
                        b = 2 * total_to_call_round
                except ValueError:
                    j+=1
                    print('must enter a number')
                    
            if "Player {0}".format(turn) not in dollar_dict:
                balance_dict["Player {0}".format(turn)] -= b
            else:
                balance_dict["Player {0}".format(turn)] -= (b - dollar_dict["Player {0}".format(turn)])
            
            dollar_dict["Player {0}".format(turn)]=b
            action_df = action_df.append(pd.DataFrame([["Player {0}".format(turn),round,a,b]], columns = action_df_columns))
        
        elif a == 'call':
            
            if "Player {0}".format(turn) not in dollar_dict:
                balance_dict["Player {0}".format(turn)] -= total_to_call_round
            else:
                balance_dict["Player {0}".format(turn)] -= (total_to_call_round - dollar_dict["Player {0}".format(turn)])


            dollar_dict["Player {0}".format(turn)]=total_to_call_round
            action_df = action_df.append(pd.DataFrame([["Player {0}".format(turn),round,a,total_to_call_round]], columns = action_df_columns))
            
        elif a == 'check':
            if "Player {0}".format(turn) not in dollar_dict:
                action_df = action_df.append(pd.DataFrame([["Player {0}".format(turn),round,a,0]], columns = action_df_columns))
            else:
                action_df = action_df.append(pd.DataFrame([["Player {0}".format(turn),round,a,dollar_dict["Player {0}".format(turn)]]], columns = action_df_columns))
            
            
        
        if a == 'fold':
            if "Player {0}".format(turn) not in dollar_dict:
                action_df = action_df.append(pd.DataFrame([["Player {0}".format(turn),round,a,0]], columns = action_df_columns))
            else:
                action_df = action_df.append(pd.DataFrame([["Player {0}".format(turn),round,a,dollar_dict["Player {0}".format(turn)]]], columns = action_df_columns))
            
            order.pop(0)
            
            if turn == wnba:
                wnba = None
            
        else:
            order = order[1:] + order[:1]
        
        turn = order[0]
        
        players_left = len(order)

        print('players left')
        print(players_left)
        print('wnba')
        print(wnba)
        
        if wnba == turn or players_left == 1:
            in_process = False
        
    return dollar_dict, action_df, order

#dollar_dict, action_df, order = blind_action([0,1,2,3], 100, 200)
#dollar_dict, action_df, order = post_flop_betting([0,1,2,3], action_df ,100, 200)
