import pandas as pd
import numpy as np

class NFLDraftTradeModel:
    def __init__(self):
        self.war_by_position = None
        self.salary_cap_data = None
        self.board = None
        self.team_data = None
        
    def load_data(self, board_path, wr_grades):
        
        self.board = pd.read_csv(board_path)
        self.wr_grade = pd.read_csv(wr_grades)
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
    
    def evaluate_pick_relative_to_board(self, player, pick):
        
        player_rank = self.board[
            self.board['Player'] == player]['Rank'].values[0]

        return player_rank / pick

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
    
    def evaluate_team_need(self, position, team="NE"):
        
        league_position_grade = self.wr_grade[
            (self.wr_grade['position'] == position) & (self.wr_grade['targets'] > 35)]['grades_offense'].values
        avg_league_position_grade = np.mean(league_position_grade)

        team_players_grade = self.wr_grade[
            (self.wr_grade['position'] == position) & (self.wr_grade['team_name'] == team) 
            & (self.wr_grade['targets'] > 35)]['grades_offense'].values
        avg_team_position_grade = np.mean(team_players_grade)
        
        print(avg_league_position_grade, avg_team_position_grade)
    
    def evaluate_trade(self, your_team, other_team, picks_given, picks_received, mode, player, 
                       team_position_cap=None, league_avg_position_cap=None, player_war=None, target_position=None):

        # Calculate raw performance value of picks
        perfomance_value_given = sum(self.calculate_performance_value(pick) for pick in picks_given)
        performance_value_received = sum(self.calculate_performance_value(pick) for pick in picks_received)
        
        value_difference = performance_value_received - perfomance_value_given

        if mode == "trade_up":
            player_strength = self.evaluate_player_strength(target_position, player_war)
            position_relevance = self.evaluate_position_relevance(target_position)
            team_need = self.evaluate_team_need(target_position)
            pick_value = self.evaluate_pick_relative_to_board(player, min(picks_received))

            adjustment_factor = player_strength * position_relevance * team_need * pick_value

            value_difference += abs(value_difference * adjustment_factor)

        degree_of_favoreness = value_difference/perfomance_value_given

        if abs(degree_of_favoreness) < 0.2:
            favored_team = "Equal value"
            degree = "Equal"
        elif value_difference > 0:
            favored_team = your_team
            if abs(degree_of_favoreness) > 1:
                degree = "Strongly favors"
            else:
                degree = "Slightly favors"
        else:
            favored_team = other_team
            if abs(degree_of_favoreness) > 1:
                degree = "Strongly favors"
            else:
                degree = "Slightly favors"
        
        return {
            "value_difference": value_difference,
            "degree of favoreness": degree_of_favoreness,
            "favored_team": favored_team,
            "degree": degree
        }

def main():
    model = NFLDraftTradeModel()
    
    model.load_data(
        board_path="board.csv",
        wr_grades="receiving_summary (2).csv"
    )
    
    result = model.evaluate_trade(
        your_team="Jaguars",
        other_team="Browns",
        team_position_cap=20,
        league_avg_position_cap=35,
        picks_given=[5, 16, 36, 126],
        picks_received=[2, 104, 200],
        player_war=2,
        target_position="WR",
        player="Travis Hunter",
        mode="trade_up"
    )
    
    print(result)

main()