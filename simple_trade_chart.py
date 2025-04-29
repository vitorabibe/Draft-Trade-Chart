import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import requests
from bs4 import BeautifulSoup
import json

class NFLDraftTradeModel:
    def __init__(self):
        self.war_by_position = None
        self.salary_cap_data = None
        self.consensus_board = None
        self.team_data = None
        
    def load_data(self):
        
        self.war_by_position = pd.DataFrame({
            'Position': ['QB', 'RB/FB', 'WR', 'TE', 'T', 'G', 'C', 'DI', 'ED', 'LB', 'CB', 'S'],
            'Mean_WAR': [1.63, 0.10, 0.28, 0.18, 0.09, 0.10, 0.10, 0.06, 0.06, 0.11, 0.23, 0.23],
            'CoV_WAR': [0.70, 0.64, 0.84, 0.62, 1.09, 1.11, 1.08, 1.34, 1.54, 0.83, 0.91, 0.77],
        })
        
    def calculate_performance_value(self, pick_number):
        '''
        Weibull distribution formula from Massey & Thaler (2013)
        Formula: v(t) = e^(-λ(t-1)^β)
        Value for the first pick is normalized to 1.0
        Based on their analysis of actual NFL draft-day trades
        '''

        lambda_param = 0.146
        beta_param = 0.698

        return np.exp(-lambda_param * ((pick_number - 1) ** beta_param))
                    
    def evaluate_player_strength(self, player_position, player_war):

        '''
        Here, I get the top WAR for the position because we are considering that
        the player contributes as a top 3-5 player would.
        '''

        # Get WAR data for the best player in position
        position_war = (
            self.war_by_position[
                self.war_by_position['Position'] == player_position]['Mean_WAR'].values[0]
            + self.war_by_position[
                self.war_by_position['Position'] == player_position]['CoV_WAR'].values[0]
        )
    
        # Return relative strength
        return player_war / position_war
    
    def evaluate_pick_relative_to_consensus(self, player, pick):
        consensus_pick = self.consensus_board[
                self.consensus_board['Player'] == player]['Mean_WAR'].values[0]
    
        return consensus_pick / pick

    def evaluate_position_relevance(self, position):
        '''
        Here, I get the top WAR for the position because we are considering that
        the player contributes as a top 3-5 player would.
        '''

        # Get WAR data for the best player in position
        position_war = (
            self.war_by_position[
                self.war_by_position['Position'] == position]['Mean_WAR'].values[0]
            + self.war_by_position[
                self.war_by_position['Position'] == position]['CoV_WAR'].values[0]
        )
        
        # Compare to best QB (highest WAR position)
        qb_war = (
            self.war_by_position[
                self.war_by_position['Position'] == 'QB']['Mean_WAR'].values[0]
            + self.war_by_position[
                self.war_by_position['Position'] == 'QB']['CoV_WAR'].values[0]
        )
        
        # Return relative importance
        return position_war / qb_war
    
    def evaluate_team_need(self, team_position_cap, league_avg_position_cap):

        return league_avg_position_cap / team_position_cap if team_position_cap > 0 else None
    
    def evaluate_trade(self, team_giving_picks, team_receiving_picks, team_position_cap, 
                      league_avg_position_cap, picks_given, picks_received, player_war,
                      player, target_position):

        # Calculate raw performance value of picks
        perfomance_value_given = sum(self.calculate_performance_value(pick) for pick in picks_given)
        performance_value_received = sum(self.calculate_performance_value(pick) for pick in picks_received)
        
        raw_value_difference = performance_value_received - perfomance_value_given
        adjusted_value_difference = raw_value_difference

        player_strength = self.evaluate_player_strength(
            target_position, player_war)
        position_relevance = self.evaluate_position_relevance(target_position)
        team_need = self.evaluate_team_need(team_position_cap, league_avg_position_cap)
        
        adjustment_factor = player_strength * position_relevance * team_need
        adjusted_value_difference = (
            raw_value_difference * adjustment_factor if adjustment_factor < 1
            else abs(raw_value_difference * adjustment_factor)
        )
        
        if abs(adjusted_value_difference/perfomance_value_given) < 0.2:
            favored_team = "Equal value"
            degree = "Equal"
        elif adjusted_value_difference > 0:
            favored_team = team_giving_picks
            if abs(adjusted_value_difference/perfomance_value_given) > 1:
                degree = "Strongly favors"
            else:
                degree = "Slightly favors"
        else:
            favored_team = team_receiving_picks
            if abs(adjusted_value_difference/perfomance_value_given) > 1:
                degree = "Strongly favors"
            else:
                degree = "Slightly favors"
        
        return {
            "raw_value_difference": raw_value_difference,
            "adjusted_value_difference": adjusted_value_difference,
            "favored_team": favored_team,
            "degree": degree
        }

def main():
    model = NFLDraftTradeModel()
    
    model.load_data()
    
    result = model.evaluate_trade(
        team_giving_picks="Jaguars",
        team_receiving_picks="Browns",
        team_position_cap=20,
        league_avg_position_cap=35,
        picks_given=[5, 16, 36, 126],
        picks_received=[2, 104, 200],
        player_war=0.9,
        player="Travis Hunter",
        target_position="WR"
    )
    
    print(result)

main()