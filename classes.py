import pandas as pd
import numpy as np

#will remove players
class players:
    '''
    no point in using this. dont want to make global variables
    '''

    def __init__(self, name, balance=1000):
        self.name = name
        self.balance = balance

    def name(self):
        return self.name

    def balance(self):
        return self.balance

class deal_cards:
    '''
    seems to work. gets called in the "action" function
    '''

    def __init__(self, num_players, players):
        self.df = pd.DataFrame()
        self.num_players = num_players
        self.players = players

    def num_players(self):
        return self.num_players

    def players(self):
        return self.players

    def cards(self):
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

        self.df = pd.DataFrame({'Card Name': card_list, 'Card Num': card_nums, 'Card Suit': card_suits})


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

        self.df['Card Name Adj'] = self.df['Card Num'].apply(card_select)

        return self

    def shuffle_and_deal(self):

        #shuffle the deck
        self.df = self.df.reindex(np.random.permutation(self.df.index))
        self.df = self.df.reset_index(drop=True)

        cards_needed = self.num_players * 2 + 5
        self.df = self.df[:cards_needed]

        assign_card_list = []
        for player in self.players:
            assign_card_list.append(player)
            assign_card_list.append(player)
        assign_card_list.append('F')
        assign_card_list.append('F')
        assign_card_list.append('F')
        assign_card_list.append('T')
        assign_card_list.append('R')

        self.df['assigned_card'] = assign_card_list

        return self

class hands:

    def __init__(self, df):
        self.df = df
        self.one_pair = ''
        self.two_pair = ''
        self.trips = ''
        self.boat = ''
        self.quads = ''
        self.has_straight = ''
        self.has_flush = ''
        self.flush_suit = ''
        self.has_straight_flush = ''
        self.cards_used_pairs = []
        self.cards_used_straight = []
        self.cards_used_flush = []
        self.cards_used_straight_flush = []

    def df(self):
        return df

    def pairs(self):
        pairs = self.df.groupby('Card Num').count()
        pairs = pairs[pairs['Card Name'] > 1]
        pairs = pairs.iloc[:, 0:1]
        pairs.columns = ['Count']
        pairs = pairs.sort_index(ascending = False, axis = 0).sort_values(by = ['Count'], axis = 0, ascending = False)

        #always limit pairs df to two rows
        pairs = pairs.head(2)

        non_pair_cards = self.df[~self.df['Card Num'].isin(pairs.index)]
        non_pair_cards = non_pair_cards.sort_values(by = 'Card Num', axis = 0, ascending = False)

        self.one_pair = (sum(pairs['Count'] == 2) == 1)
        self.two_pair = (sum(pairs['Count'] == 2) >= 2)
        self.trips = sum(pairs['Count'] == 3) >= 1
        self.boat = (sum(pairs['Count'] == 3) >= 1) & (sum(pairs['Count'] == 2) >= 1)
        self.quads = sum(pairs['Count'] == 4) >= 1
        #add final hand
        if self.quads == True:
            c1 = pairs.index[0]
            c2 = pairs.index[0]
            c3 = pairs.index[0]
            c4 = pairs.index[0]
            c5 = max(non_pair_cards['Card Num'])
        elif self.boat == True:
            c1 = pairs.index[0]
            c2 = pairs.index[0]
            c3 = pairs.index[0]
            c4 = pairs.index[1]
            c5 = pairs.index[1]
        elif self.trips == True:
            c1 = pairs.index[0]
            c2 = pairs.index[0]
            c3 = pairs.index[0]
            c4 = non_pair_cards['Card Num'].iloc[0]
            c5 = non_pair_cards['Card Num'].iloc[1]
        elif self.two_pair == True:
            c1 = pairs.index[0]
            c2 = pairs.index[0]
            c3 = pairs.index[1]
            c4 = pairs.index[1]
            c5 = non_pair_cards['Card Num'].iloc[0]
        elif self.one_pair == True:
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

        self.cards_used_pairs = [c1,c2,c3,c4,c5]


        return self

    def straight(self):
        straight = self.df.loc[:, ['Card Num', 'Card Name Adj']]
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

        self.has_straight = (straight_counter > 0)
        #add final hand

        if self.has_straight == True:
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

        self.cards_used_straight = [c1,c2,c3,c4,c5]

        return self

    def flush(self):
        suits = self.df.groupby('Card Suit').count()
        suits = suits[suits['Card Name'] >= 5]
        suits = suits.iloc[:, 0:1]
        suits.columns = ['Count']
        if len(suits)==0:
            self.flush_suit='None'
        else:
            self.flush_suit = suits.index[0]

        self.has_flush = (len(suits) > 0)

        #add final hand
        if self.has_flush == True:
            temp = self.df[self.df['Card Suit']==suits.index[0]].sort_values(by = 'Card Num', axis = 0, ascending = False)
            c1=temp['Card Num'].iloc[0]
            c2=temp['Card Num'].iloc[1]
            c3=temp['Card Num'].iloc[2]
            c4=temp['Card Num'].iloc[3]
            c5=temp['Card Num'].iloc[4]
        else:
            c1=0
            c2=0
            c3=0
            c4=0
            c5=0

        self.cards_used_flush = [c1,c2,c3,c4,c5]

        return self

    def straight_flush(self):
        straight_flush_counter = 0
        straight_flush_high_card = 0
        temp = self.df[self.df['Card Suit'] == self.flush_suit]
        num_aces = len(temp[(temp['Card Name Adj'] == 'Ace') & (temp['Card Suit']==self.flush_suit)])
        if num_aces > 0:
            ace = pd.DataFrame([['Ace ' + self.flush_suit, 1, self.flush_suit, 'Ace', 0]], columns = ['Card Name', 'Card Num', 'Card Suit', 'Card Name adj', 'assigned_card'])
            temp = temp.append(ace)
        temp = temp.sort_values(by = 'Card Num')
        temp['diff'] = temp['Card Num'].diff()
        if len(temp) >= 5:
            for i in range(0, len(temp) - 4):
                is_straight_flush = (sum(temp.iloc[1+i:5+i].loc[:,'diff'] == 1) == 4) & (sum(temp['Card Suit'].iloc[i:5+i] == self.flush_suit) == 5)
                high_card = temp['Card Num'].iloc[4+i]
                straight_flush_counter += is_straight_flush
                straight_flush_high_card = max(straight_flush_high_card, is_straight_flush * high_card)

        self.has_straight_flush = (straight_flush_counter > 0)
        #add final hand

        if self.has_straight_flush == True:
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

        self.cards_used_straight_flush = [c1,c2,c3,c4,c5]

        return self
