import pandas as pd
import os
import random
import numpy as np
import collections
import importlib

os.chdir('/Users/jeremyholtzman/Documents/Personal/Poker') 

from action_helper_2 import deal_cards, blind_action, post_flop_betting, player_balance
#importlib.reload(action_helper)

##




#notes

#create deck of cards - done
#deal cards - done
#helper hand functions - done
#evaluate hands - almost done
#determine winner
#bet, check, raise, fold
#seeing your hand
#calculate balances
#easy to use output dataframe
    
##
    

def evaluate_hands(num_players):
    global df
    
    #should not call deal cards within evaluate hands. might want to move this out and take df as an input
    deal_cards(num_players)
    
    player_df = pd.DataFrame()
    hand_score_dict = {}
    final_hand_dict = {} #this is player #: [C1, C2, C3, C4, C5]
    
    for i in range(num_players):
        player_df = df[(df['assigned_card'].isin(['F','T','R'])) | (df['assigned_card'] == i)]
        
        #improvement, don't have to run pairs if has royal flush...
        one_pair, two_pair, trips, boat, quads = pairs(player_df)
        has_straight = straight(player_df)
        has_flush, flush_suit = flush(player_df)
        
        if has_flush == True & has_straight == True:
            has_straight_flush = straight_flush(player_df[player_df['Card Suit'] == flush_suit], flush_suit)
        else:
            has_straight_flush = False
        
        
        if has_straight_flush == True:
            hand_score_dict["Player {0}".format(i)]=8
        elif quads == True:
            hand_score_dict["Player {0}".format(i)]=7
        elif boat == True:
            hand_score_dict["Player {0}".format(i)]=6
        elif has_flush == True:
            hand_score_dict["Player {0}".format(i)]=5
        elif has_straight == True:
            hand_score_dict["Player {0}".format(i)]=4
        elif trips == True:
            hand_score_dict["Player {0}".format(i)]=3
        elif two_pair == True:
            hand_score_dict["Player {0}".format(i)]=2
        elif one_pair == True:
            hand_score_dict["Player {0}".format(i)]=1
        else:
            hand_score_dict["Player {0}".format(i)]=0
            
        #high card - high card 1-5
        #pair - pair card and high card 1-3
        #two pair - top pair, bottom pair, high card
        #three of a kind - top pair, high card 1-2
        #straight - high card 1
        #flush - high card 1-5
        #full house - top pair, bottom pair
        #four of a kind - top pair, high card
        #straight flush - high card 1
        
    return hand_score_dict #, final_hand_dict 

    

#evaluate_hands(5)

##DO NOT RUN, USED
#play hand
#pieces of this are good, others need to be reworked

#1. small blind and big blind
#2. deal 2 cards to everyone
#3. bet around table
#4. flop
#5. bet around table
#6. turn
#7. bet around table
#8. river
#9. bet around table
#10. evaluate winner

#deal with balances later

num_players = 5
deal_cards(num_players)

def gameplay(num_players, player_id, small_blind, big_blind, button_position, player_balance):
    global df    
    
    pot = 0
    
    #NEED to break out into multiple functions. individual players seeing hands needs to be different from betting.
    
    #1. small blind and big blind
    if button_position + 2 <= num_players - 1:
        small_blind_pos = button_position + 1
        big_blind_pos = button_position + 2
    elif button_position + 1 <= num_players - 1:
        small_blind_pos = button_position + 1
        big_blind_pos = 0
    else:
        small_blind_pos = 0
        big_blind_pos = 1

    #subtracting out blinds
    player_balance -= (player_id == small_blind_pos) * small_blind + (player_id == big_blind_pos) * big_blind
    print(player_balance)
    
    
    #2. deal 2 cards to everyone
    player_hand = df[df['assigned_card'] == player_id]

    #3. bet around table
    #call some function here
    
    #4. flop
    player_hand = player_hand.append(df[df['assigned_card'] == 'F'])


    #5. bet around table
    #call some function here
    
    #6. turn
    player_hand = player_hand.append(df[df['assigned_card'] == 'T'])

    #7. bet around table
    #call some function here    
    
    #8. river
    player_hand = player_hand.append(df[df['assigned_card'] == 'R'])
    print(player_hand)

    #9. bet around table
    #call some function here  
    
    #10. evaluate winner
    #call evaluate winner
    
gameplay(num_players, 0, 10, 20, 0, 5000)

##

#betting
    

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
    
    #dollar_dict, action_df, blind_order = blind_action(blind_order, small_blind, big_blind)
    dollar_dict, action_df, blind_order = blind_action(blind_order, small_blind, big_blind, cards, balance_dict)
    print('done with blind betting')
    print(blind_order)
    
    if len(blind_order) > 1:
        #flop betting
        order = [i for i in post_blind_order if i in blind_order]
        dollar_dict, action_df, order = post_flop_betting(order, action_df ,small_blind, big_blind, 'flop', cards, balance_dict)
        print('done with flop betting')
        
        if len(order) > 1:
        
            #turn betting
            order = [i for i in post_blind_order if i in order]
            dollar_dict, action_df, order = post_flop_betting(order, action_df ,small_blind, big_blind, 'turn', cards, balance_dict)
            print('done with turn betting')
            
            if len(order) > 1:
            
                #river betting
                order = [i for i in post_blind_order if i in order]
                dollar_dict, action_df, order = post_flop_betting(order, action_df ,small_blind, big_blind, 'river', cards, balance_dict)
                print('done with river betting')
            
    print(action_df)
    return action_df, balance_dict
    
    
##
 
    
def start_game(num_players, small_blind, big_blind):
    balance_dict = player_balance(num_players)
    print(balance_dict)
    
    button_position = 2
    
    action_df, balance_dict = action(num_players, button_position, small_blind, big_blind, balance_dict)
    
    print(balance_dict)
    print(action_df)
    
    if button_position + 1 > num_players - 1:
        button_position = 0
    else:
        button_position += 1
        
    print('new button position: ' + str(button_position))

start_game(3, 1000, 2000)