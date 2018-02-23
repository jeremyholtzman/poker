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

##player balances
#load player balances into table

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

#balance_dict = player_balance(5)
#print(balance_dict)

##blind action
#blind action

def blind_action(order, small_blind, big_blind, cards, balance_dict):
    wnba = None
    #wnba = order[0]
    
    dollar_dict = {}
    for player in order:
        dollar_dict["Player {0}".format(player)] = 0
        
    action_df_columns = ['Player ID','Bet Round','Player Action','Cumulative Amount in Round']
    action_df = pd.DataFrame(columns = action_df_columns)
    
    all_actions = ['check','raise','fold','call']
    players_left = len(order)
    starting_num_players = players_left
    all_in_amount = 0
    round = 'pre-flop'
    
    #blind betting
    
    if balance_dict["Player {0}".format(order[-1])] > big_blind:
        dollar_dict["Player {0}".format(order[-1])]=big_blind
        balance_dict["Player {0}".format(order[-1])] -= big_blind
        action_df = action_df.append(pd.DataFrame([["Player {0}".format(order[-1]),round,'big blind',big_blind]], columns = action_df_columns))
    else:
        all_in_amount = balance_dict["Player {0}".format(order[-1])]
        dollar_dict["Player {0}".format(order[-1])]=all_in_amount
        action_df = action_df.append(pd.DataFrame([["Player {0}".format(order[-1]),round,'big blind - all in',all_in_amount]], columns = action_df_columns))
        balance_dict["Player {0}".format(order[-1])] = 0

    
    if balance_dict["Player {0}".format(order[-2])] > small_blind:
        dollar_dict["Player {0}".format(order[-2])]=small_blind
        balance_dict["Player {0}".format(order[-2])] -= small_blind    
        action_df = action_df.append(pd.DataFrame([["Player {0}".format(order[-2]),round,'small blind',small_blind]], columns = action_df_columns))
    else:
        all_in_amount = balance_dict["Player {0}".format(order[-2])]
        dollar_dict["Player {0}".format(order[-2])]=all_in_amount
        action_df = action_df.append(pd.DataFrame([["Player {0}".format(order[-2]),round,'small blind - all in',all_in_amount]], columns = action_df_columns))
        balance_dict["Player {0}".format(order[-2])] = 0
    
    for i in range(players_left):
        print('in for loop')
        print(str("Player {0}".format(i)) + ' has $'+ str(balance_dict["Player {0}".format(i)]) + ' remaining')
        if balance_dict["Player {0}".format(i)] == 0:
            print(str(i) + ' should be taken out')
            order.remove(i)
            
    print(order)
    
    #create if statement that checks if only 1 player left after blinds
    if len(order) > 1:
    
        turn = order[0]
        in_process = True
        while in_process:
    
            
            print('player turn')
            print(turn)
    
            print(cards[cards['assigned_card'] == turn])
            total_to_call_round = max(max(dollar_dict.values()), big_blind)
            
            j = 0
            b = 0
            while j < 10:
                a = input('what would you like to do?')
                if (dollar_dict["Player {0}".format(turn)] < total_to_call_round) & ((a == 'check') or (a == 'bet')):
                    j+=1
                    a = 'fold'
                    print('cannot check. must call, raise, or fold')
                
                elif not(a in all_actions):
                    j+=1
                    a = 'fold'
                    print('that was not an option')
                    
                    
                elif (a == 'raise') or (a == 'bet'):
                    wnba = turn
                    print('new wnba')
                    print(wnba)
                    
                    b = input('how much would you like to ' + a)
                    try:
                        b = int(b)
                        if (b >= 2 * total_to_call_round) & (b >= big_blind) & (b <= balance_dict["Player {0}".format(turn)]):
                            break
                        elif b > balance_dict["Player {0}".format(turn)]:
                            print('that was too high. you only have ' + str(balance_dict["Player {0}".format(turn)]))
                            j += 1
                        else:
                            print('that was not high enough. you must ' + a + ' to at least ' + str(max(2 * total_to_call_round, big_blind)))
                            j+=1
                            b = 2 * total_to_call_round
                    except ValueError:
                        j+=1
                        print('must enter a number')
                            
                
                elif (a == 'call') & (total_to_call_round > balance_dict["Player {0}".format(turn)]):
                    j += 1
                    print('that was too high. you only have ' + str(balance_dict["Player {0}".format(turn)]))
    
                elif a == 'call':
                    b = total_to_call_round
                    print('here')
                    break
                    
    
                elif a == 'check':
                    b = total_to_call_round
                    break
    
                elif a == 'fold':
                    b = 0
                    break
                
            #move to after while
            balance_dict["Player {0}".format(turn)] -= (b - dollar_dict["Player {0}".format(turn)])
            
            dollar_dict["Player {0}".format(turn)]=b
            action_df = action_df.append(pd.DataFrame([["Player {0}".format(turn),round,a,b]], columns = action_df_columns))
    
            
            if a == 'fold':                
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
            
            players_bet = list(set(action_df[~action_df['Player Action'].isin(['big blind', 'small blind'])]['Player ID']))
            print('here is players_bet')
            print(players_bet)
            
            
            if (wnba == turn or players_left == 1) or (wnba is None and total_to_call_round <= big_blind and len(players_bet) == starting_num_players):
                in_process = False
    
    print('here')
    print(dollar_dict)
    print(balance_dict)
    return dollar_dict, action_df, order
    
#dollar_dict, action_df, test = blind_action([0,1,2,3], 100, 200)
#print(test)

##post flop betting
#post flop betting

def post_flop_betting(order, action_df, small_blind, big_blind, round, cards, balance_dict):
    turn = order[0]
    dollar_dict = {}
    for player in order:
        dollar_dict["Player {0}".format(player)] = 0
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
        
        
        total_to_call_round = max(dollar_dict.values())
        
        j = 0
        b = 0
        while j < 10:
            a = input('what would you like to do?')
            if (dollar_dict["Player {0}".format(turn)] < total_to_call_round) & ((a == 'check') or (a == 'bet')):
                j+=1
                a = 'fold'
                print('cannot check. must call, raise, or fold')
            
            elif not(a in all_actions):
                j+=1
                a = 'fold'
                print('that was not an option')
                
                
            elif (a == 'raise') or (a == 'bet'):
                wnba = turn
                print('new wnba')
                print(wnba)
                
                b = input('how much would you like to ' + a)
                try:
                    b = int(b)
                    if (b >= 2 * total_to_call_round) & (b >= big_blind) & (b <= balance_dict["Player {0}".format(turn)]):
                        break
                    elif b > balance_dict["Player {0}".format(turn)]:
                        print('that was too high. you only have ' + str(balance_dict["Player {0}".format(turn)]))
                        j += 1
                    else:
                        print('that was not high enough. you must ' + a + ' to at least ' + str(max(2 * total_to_call_round, big_blind)))
                        j+=1
                        b = 2 * total_to_call_round
                except ValueError:
                    j+=1
                    print('must enter a number')
                        
            
            elif (a == 'call') & (total_to_call_round > balance_dict["Player {0}".format(turn)]):
                j += 1
                print('that was too high. you only have ' + str(balance_dict["Player {0}".format(turn)]))

            elif a == 'call':
                b = total_to_call_round
                print('here')
                break
                

            elif a == 'check':
                b = 0
                break

            elif a == 'fold':
                b = 0
                break
            
        #move to after while
        balance_dict["Player {0}".format(turn)] -= (b - dollar_dict["Player {0}".format(turn)])
        
        dollar_dict["Player {0}".format(turn)]=b
        action_df = action_df.append(pd.DataFrame([["Player {0}".format(turn),round,a,b]], columns = action_df_columns))

        
        if a == 'fold':
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
