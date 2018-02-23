import pandas as pd
import os
import random
import numpy as np
import collections


##
#pairs

def pairs(df):
    pairs = df.groupby('Card Num').count()
    pairs = pairs[pairs['Card Name'] > 1]
    pairs = pairs.iloc[:, 0:1]
    pairs.columns = ['Count']
    pairs = pairs.sort_index(ascending = False, axis = 0).sort_values(by = ['Count'], axis = 0, ascending = False)

    #always limit pairs df to two rows
    pairs = pairs.head(2)

    non_pair_cards = df[~df['Card Num'].isin(pairs.index)]
    non_pair_cards = non_pair_cards.sort_values(by = 'Card Num', axis = 0, ascending = False)

    one_pair = (sum(pairs['Count'] == 2) == 1)
    two_pair = (sum(pairs['Count'] == 2) >= 2)
    trips = sum(pairs['Count'] == 3) >= 1
    boat = (sum(pairs['Count'] == 3) >= 1) & (sum(pairs['Count'] == 2) >= 1)
    quads = sum(pairs['Count'] == 4) >= 1
    #add final hand
    if quads == True:
        c1 = pairs.index[0]
        c2 = pairs.index[0]
        c3 = pairs.index[0]
        c4 = pairs.index[0]
        c5 = max(non_pair_cards['Card Num'])
    elif boat == True:
        c1 = pairs.index[0]
        c2 = pairs.index[0]
        c3 = pairs.index[0]
        c4 = pairs.index[1]
        c5 = pairs.index[1]
    elif trips == True:
        c1 = pairs.index[0]
        c2 = pairs.index[0]
        c3 = pairs.index[0]
        c4 = non_pair_cards['Card Num'].iloc[0]
        c5 = non_pair_cards['Card Num'].iloc[1]
    elif two_pair == True:
        c1 = pairs.index[0]
        c2 = pairs.index[0]
        c3 = pairs.index[1]
        c4 = pairs.index[1]
        c5 = non_pair_cards['Card Num'].iloc[0]
    elif one_pair == True:
        c1 = pairs.index[0]
        c2 = pairs.index[0]
        c3 = non_pair_cards['Card Num'].iloc[0]
        c4 = non_pair_cards['Card Num'].iloc[1]
        c5 = non_pair_cards['Card Num'].iloc[2]
    else:
        c1 = non_pair_cards['Card Num'].iloc[0]
        c2 = non_pair_cards['Card Num'].iloc[1]
        c3 = non_pair_cards['Card Num'].iloc[2]
        c4 = non_pair_cards['Card Num'].iloc[3]
        c5 = non_pair_cards['Card Num'].iloc[4]


    return one_pair, two_pair, trips, boat, quads, [c1,c2,c3,c4,c5]


##
#straight
def straight(df):
    straight = df.loc[:, ['Card Num', 'Card Name Adj']]
    straight = straight.sort_values(by = 'Card Num')
    straight.drop_duplicates(inplace = True)

    num_aces = len(straight[straight['Card Name Adj'] == 'Ace'])

    if num_aces > 0:
        ace = pd.DataFrame([[1, 'Ace']], columns = ['Card Num', 'Card Name Adj'])
        straight = straight.append(ace)
        straight = straight.sort_values(by = 'Card Num')

    straight['diff'] = straight['Card Num'].diff()

    straight_counter = 0
    straight_high_card = 0
    if len(straight) >= 5:
        for i in range(0, len(straight)-4):
            is_straight = (sum(straight.iloc[1+i:5+i].loc[:,'diff'] == 1) == 4)
            high_card = straight['Card Num'].iloc[4+i]
            straight_counter += is_straight
            straight_high_card = max(straight_high_card, is_straight * high_card)

    has_straight = (straight_counter > 0)
    #add final hand

    if has_straight == True:
        c1 = straight_high_card
        c2 = straight_high_card-1
        c3 = straight_high_card-2
        c4 = straight_high_card-3
        c5 = straight_high_card-4
    else:
        c1=0
        c2=0
        c3=0
        c4=0
        c5=0

    return has_straight, [c1,c2,c3,c4,c5]

##
#flush
def flush(df):
    suits = df.groupby('Card Suit').count()
    suits = suits[suits['Card Name'] >= 5]
    suits = suits.iloc[:, 0:1]
    suits.columns = ['Count']
    if len(suits)==0:
        flush_suit='None'
    else:
        flush_suit = suits.index[0]

    has_flush = (len(suits) > 0)

    #add final hand
    if has_flush == True:
        df = df[df['Card Suit']==suits.index[0]].sort_values(by = 'Card Num', axis = 0, ascending = False)
        c1=df['Card Num'].iloc[0]
        c2=df['Card Num'].iloc[1]
        c3=df['Card Num'].iloc[2]
        c4=df['Card Num'].iloc[3]
        c5=df['Card Num'].iloc[4]
    else:
        c1=0
        c2=0
        c3=0
        c4=0
        c5=0

    return has_flush, flush_suit, [c1,c2,c3,c4,c5]

##
#straight flush
def straight_flush(df, flush_suit):
    straight_flush_counter = 0
    straight_flush_high_card = 0
    df = df[df['Card Suit'] == flush_suit]
    num_aces = len(df[(df['Card Name Adj'] == 'Ace') & (df['Card Suit']==flush_suit)])
    if num_aces > 0:
        ace = pd.DataFrame([['Ace ' + flush_suit, 1, flush_suit, 'Ace', 0]], columns = ['Card Name', 'Card Num', 'Card Suit', 'Card Name adj', 'assigned_card'])
        df = df.append(ace)
    df = df.sort_values(by = 'Card Num')
    df['diff'] = df['Card Num'].diff()
    if len(df) >= 5:
        for i in range(0, len(df) - 4):
            is_straight_flush = (sum(df.iloc[1+i:5+i].loc[:,'diff'] == 1) == 4) & (sum(df['Card Suit'].iloc[i:5+i] == flush_suit) == 5)
            high_card = df['Card Num'].iloc[4+i]
            straight_flush_counter += is_straight_flush
            straight_flush_high_card = max(straight_flush_high_card, is_straight_flush * high_card)

    has_straight_flush = (straight_flush_counter > 0)
    #add final hand

    if has_straight_flush == True:
        c1 = straight_flush_high_card
        c2 = straight_flush_high_card-1
        c3 = straight_flush_high_card-2
        c4 = straight_flush_high_card-3
        c5 = straight_flush_high_card-4
    else:
        c1=0
        c2=0
        c3=0
        c4=0
        c5=0

    return has_straight_flush, [c1,c2,c3,c4,c5]
