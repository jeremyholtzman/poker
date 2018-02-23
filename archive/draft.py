import pandas as pd
import os
import random
import numpy as np
##
#setting up dictionary of cards
print('I am setting up the game')
num_list = []

for i in range(13):
    num_list.append(i+2)
    
print(num_list)

suit_list = ['spades','diamonds','hearts','clubs']

print(suit_list)

card_list = []
card_nums = []
card_suits = []

random.randint(0, 10)

for i in range(0, len(num_list)):
    for j in range(0, len(suit_list)):
        print(str(num_list[i]) + suit_list[j])
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
    
print(card_select(1))

df['Card Name Adj'] = df['Card Num'].apply(card_select)



print(df)


##
#randomly shuffle the deck
print('I am shuffling')

df = df.reindex(np.random.permutation(df.index))
print(df)

##
#deal a hand

print('Here is your hand')

print(df.head(7))

print('---------------------')

hand1 = df.iloc[0:2,:]
#print(hand1)
#print('######################')
flop = df.iloc[2:5,:]
turn = df.iloc[6,:]
river = df.iloc[7,:]
#print(flop)

board = df.iloc[2:7,:]
#print(board)

fullhand = df.iloc[0:7,:]
fullhand = fullhand.sort_values(by = 'Card Num', axis = 0, ascending = True)
fullhand['diff'] = fullhand['Card Num'].diff()
print(fullhand)
##
#defining pairs

#print(fullhand.groupby('Card Num').count())
pairs = fullhand.groupby('Card Num').count()
pairs = pairs[pairs['Card Name'] > 1]
pairs = pairs.iloc[:, 0:1]
pairs.columns = ['Count']
print(pairs)
pairs = pairs.sort_values(by = 'Count', axis = 0, ascending = False)
print(pairs)
print(str(len(pairs)) + ' pair(s)')

##
#defining flush
print(fullhand)

suits = fullhand.groupby('Card Suit').count()
suits = suits[suits['Card Name'] >= 5].sort_values(by = 'Card Name', axis = 0, ascending = False)
suits = suits.iloc[:, 0:1]
suits.columns = ['Count']


suits_cards = fullhand.groupby('Card Suit').max()
suits_cards = suits_cards['Card Num']
print(suits_cards)

print(str(len(suits)) + ' flushes')

suits_final = pd.concat([suits, suits_cards], axis = 1, join = 'inner').sort_values(by = 'Card Num', axis = 0, ascending = False)

if len(suits_final) == 0:
    suits_high_card = 0
else:
    suits_high_card = suits_final['Card Num'][0]

print(suits_final)
print(suits_high_card)


##
#defining straight
print(fullhand)

straight = fullhand.loc[:, ['Card Num', 'Card Name Adj']]
straight = straight.sort_values(by = 'Card Num')
straight.drop_duplicates(inplace = True)

num_aces = len(straight[straight['Card Name Adj'] == 'Ace'])


if num_aces > 0:
    ace = pd.DataFrame([[1, 'Ace']], columns = ['Card Num', 'Card Name Adj'])
    straight = straight.append(ace)



straight['diff'] = straight['Card Num'].diff()

print(straight)

straight_counter = 0
straight_high_card = 0
if len(straight) >= 5:
    for i in range(0, len(straight)-4):
        print('testing ' + str(i))
        print(straight.iloc[1+i:5+i].loc[:,'diff'] == 1)
        is_straight = (sum(straight.iloc[1+i:5+i].loc[:,'diff'] == 1) == 4)
        high_card = straight['Card Num'].iloc[4+i]
        straight_counter += is_straight        
        straight_high_card = max(straight_high_card, is_straight * high_card)

print(straight_high_card)
straight_high_card_avg = (straight_high_card + (straight_high_card - 4)) / 2 
print(straight_high_card_avg)
print(straight_counter)
print(straight)
print(str(straight_counter) + ' straights')
print(straight_high_card)

##

straight_flush_counter = 0
straight_flush_high_card = 0
if len(suits) > 0 & straight_counter > 0:
    straight_flush_df = fullhand[fullhand['Card Suit'] == suits.index[0]]
    num_aces = len(straight[straight['Card Name Adj'] == 'Ace'])
    if num_aces > 0:
        ace = pd.DataFrame([['Ace ' + suits.index[0], 1, suits.index[0], 'Ace', 0]], columns = ['Card Name', 'Card Num', 'Card Suit', 'Card Name adj', 'diff'])
        straight = straight.append(ace)
    print(straight_flush_df)
    straight_flush_df['diff'] = straight_flush_df['Card Num'].diff()
    if len(straight_flush_df) >= 5:
        for i in range(0, len(straight_flush_df) - 4):
            is_straight_flush = (sum(straight_flush_df.iloc[1+i:5+i].loc[:,'diff'] == 1) == 4) & (sum(straight_flush_df['Card Suit'].iloc[i:5+i] == suits.index[0]) == 5)
            high_card = straight_flush_df['Card Num'].iloc[4+i]
            straight_flush_counter += is_straight_flush
            straight_flush_high_card = max(straight_flush_high_card, is_straight_flush * high_card)
else:
    straight_flush_df = pd.DataFrame()

print(straight_flush_counter)

##
#notes of hands

#high card
#pair - done
#two pair - done
#three of a kind - done
#straight - done
#flush - done
#full house - done
#four of a kind - done
#straight flush - done

#kicker - done

#dealing with aces - done

##
#declaring hands

print('what you got')

one_pair = (sum(pairs['Count'] == 2) == 1)
if one_pair == True:
    one_pair_pair = pairs.index[0]
else:
    one_pair_pair = 0

two_pair = (sum(pairs['Count'] == 2) >= 2)
if two_pair == True:
    two_pair_top = pairs.sort_index().index[0]
    two_pair_bottom = pairs.sort_index().index[1]
else:
    two_pair_top = 0
    two_pair_bottom = 0

trips = sum(pairs['Count'] == 3) >= 1
if trips == True:
    trips_pair = pairs.index[0]
else:
    trips_pair = 0
    
boat = (sum(pairs['Count'] == 3) >= 1) & (sum(pairs['Count'] == 2) >= 1)
if boat == True:
    boat_top = pairs.sort_index().index[0]
    boat_bottom = pairs.sort_index().index[1]
else:
    boat_top = 0
    boat_bottom = 0

quads = sum(pairs['Count'] == 4) >= 1
if quads == True:
    quads_pair = pairs.index[0]
else:
    quads_pair = 0

has_straight = (straight_counter > 0)
has_straight_top = straight_high_card

has_flush = (len(suits) > 0)
has_flush_top = suits_high_card

has_straight_flush = (straight_flush_counter > 0)
has_straight_flush_top = straight_flush_high_card

print(one_pair)
print(two_pair)
print(trips)
print(has_straight)
print(has_flush)
print(boat)
print(quads)
print(has_straight_flush)



##

