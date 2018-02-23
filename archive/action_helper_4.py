import pandas as pd
import os
import random
import numpy as np
import collections
import importlib

from hand_helper import pairs, straight, flush, straight_flush

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


def betting(order, action_df, small_blind, big_blind, round, cards, balance_dict):
    #NOTE: Need to fix for all-ins

    turn = order[0]

    dollar_dict = {}
    for player in order:
        dollar_dict["Player {0}".format(player)] = 0

    action_df_columns = list(action_df)

    print('starting balance at beginning of round')
    print(balance_dict)

    if round == 'pre-flop':
        wnba = None
        #blind betting

        if balance_dict["Player {0}".format(order[-2])] > small_blind:
            dollar_dict["Player {0}".format(order[-2])]=small_blind
            balance_dict["Player {0}".format(order[-2])] -= small_blind
            action_df = action_df.append(pd.DataFrame([["Player {0}".format(order[-2]),round,'small blind',small_blind]], columns = action_df_columns))
        else:
            all_in_amount = balance_dict["Player {0}".format(order[-2])]
            dollar_dict["Player {0}".format(order[-2])]=all_in_amount
            action_df = action_df.append(pd.DataFrame([["Player {0}".format(order[-2]),round,'small blind - all in',all_in_amount]], columns = action_df_columns))
            balance_dict["Player {0}".format(order[-2])] = 0

        if balance_dict["Player {0}".format(order[-1])] > big_blind:
            dollar_dict["Player {0}".format(order[-1])]=big_blind
            balance_dict["Player {0}".format(order[-1])] -= big_blind
            action_df = action_df.append(pd.DataFrame([["Player {0}".format(order[-1]),round,'big blind',big_blind]], columns = action_df_columns))
        else:
            all_in_amount = balance_dict["Player {0}".format(order[-1])]
            dollar_dict["Player {0}".format(order[-1])]=all_in_amount
            action_df = action_df.append(pd.DataFrame([["Player {0}".format(order[-1]),round,'big blind - all in',all_in_amount]], columns = action_df_columns))
            balance_dict["Player {0}".format(order[-1])] = 0

    else:
        wnba = turn



    all_actions = ['check','raise','fold','call', 'bet']
    players_left = len(order)
    starting_num_players = players_left
    all_in_amount = 0





    for i in range(players_left):
        #print(str("Player {0}".format(i)) + ' has $'+ str(balance_dict["Player {0}".format(i)]) + ' remaining')
        if balance_dict["Player {0}".format(i)] == 0:
            print(str(i) + ' should be taken out')
            order.remove(i)

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
                if (dollar_dict["Player {0}".format(turn)] < total_to_call_round) & ((a == 'check') or (a == 'bet')):
                    j+=1
                    a = 'fold'
                    print('cannot check or bet. must call, raise, or fold')

                elif (a == 'call' or a == 'bet') & (total_to_call_round > 0) & (dollar_dict["Player {0}".format(turn)] == total_to_call_round):
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
                    print('here. called. at',b)
                    print('dollar dict:', dollar_dict["Player {0}".format(turn)])
                    break


                elif a == 'check':
                    b = total_to_call_round
                    break

                elif a == 'fold':
                    b = 0
                    break

            if b != 0:
                print('previous balance dict:', balance_dict["Player {0}".format(turn)])
                balance_dict["Player {0}".format(turn)] -= (b - dollar_dict["Player {0}".format(turn)])
                print('current balance dict:', balance_dict["Player {0}".format(turn)])
                print('subtracted out:', (b - dollar_dict["Player {0}".format(turn)]))

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

            print('players left - ', players_left)
            print('wnba - ', wnba)

            players_bet = list(set(action_df[~action_df['Player Action'].isin(['big blind', 'small blind'])]['Player ID']))

            if (wnba == turn or players_left == 1) or (wnba is None and len(players_bet) == starting_num_players):
                in_process = False

    print('balance_dict ---------- ')
    print(balance_dict)
    return dollar_dict, action_df, order

##old evaluate hands

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

##new evaluate hands

def evaluate_hands_v2(action_df, cards):

    players = list(set(action_df[~(action_df['Player Action']=='fold') & (action_df['Bet Round'] == 'river') ]['Player ID']))

    print(players)

    hand_score_dict = {}
    final_hand_dict = {} #this is player #: [C1, C2, C3, C4, C5]

    for i in players:
        player_df = cards[(cards['assigned_card'] == int(i[-1:])) | (cards['assigned_card'].isin(['F','T','R']))]
        print(i, 'has the following:')
        print(player_df)
        print(i[-1:])

        #improvement, don't have to run pairs if has royal flush...
        one_pair, two_pair, trips, boat, quads, pairs_cards = pairs(player_df)
        has_straight, straight_cards = straight(player_df)
        has_flush, flush_suit, flush_cards = flush(player_df)

        if has_flush == True & has_straight == True:
            has_straight_flush, straight_flush_cards = straight_flush(player_df[player_df['Card Suit'] == flush_suit], flush_suit)
        else:
            has_straight_flush = False


        if has_straight_flush == True:
            hand_score_dict[i]=8
            final_hand_dict[i]=straight_flush_cards
        elif quads == True:
            hand_score_dict[i]=7
            final_hand_dict[i]=pairs_cards
        elif boat == True:
            hand_score_dict[i]=6
            final_hand_dict[i]=pairs_cards
        elif has_flush == True:
            hand_score_dict[i]=5
            final_hand_dict[i]=flush_cards
        elif has_straight == True:
            hand_score_dict[i]=4
            final_hand_dict[i]=straight_cards
        elif trips == True:
            hand_score_dict[i]=3
            final_hand_dict[i]=pairs_cards
        elif two_pair == True:
            hand_score_dict[i]=2
            final_hand_dict[i]=pairs_cards
        elif one_pair == True:
            hand_score_dict[i]=1
            final_hand_dict[i]=pairs_cards
        else:
            hand_score_dict[i]=0
            final_hand_dict[i]=pairs_cards

        #high card - high card 1-5
        #pair - pair card and high card 1-3
        #two pair - top pair, bottom pair, high card
        #three of a kind - top pair, high card 1-2
        #straight - high card 1
        #flush - high card 1-5
        #full house - top pair, bottom pair
        #four of a kind - top pair, high card
        #straight flush - high card 1

    return hand_score_dict, final_hand_dict
