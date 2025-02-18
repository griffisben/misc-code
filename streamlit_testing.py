import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st

char_replacements = str.maketrans({" ": "%20", "ü": "u", "ó": "o", "ö": "o", "ã": "a", "ç": "c"})

league = 'Danish 1. Division'
ssn = '24-25'

full_league_name = f"{league} {ssn}"
formatted_name = full_league_name.translate(char_replacements)
df = pd.read_csv(f'https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Main%20App/{formatted_name}.csv')
raw_df = pd.read_csv(f'https://raw.githubusercontent.com/griffisben/misc-code/refs/heads/main/files/{formatted_name}%20API%20RAW%20DATA.csv')
main_cols = ['minutes_on_field','goalkeeper_action','action','goal_kick','goalkeeper_distribution','goalkeeper_goal_kick','goal_kick_long','shot_against','near_shot_against','any_goal','conceded_goal','meaningless','near_conceded_goal','any_free_kick','goal_kick_short','goalkeeper_exit','pass','recovery','save','aerial_duel','aerial_duel_in_own_penalty_area','buildup_pass','duel','forward_pass','goalkeeper_action_on_corner_faced','goalkeeper_action_on_cross_faced','goalkeeper_claim','goalkeeper_foot_pass','goalkeeper_long_pass','hand_pass','head_conceded_goal','heading','interception','last','lateral_pass','long_pass','long_pass_into_duel','long_pass_or_cross','long_shot_against','pass_followed_by_teammate_loss','pass_into_duel','penalty_conceded_goal','pick_up','plus','progressive_pass','run','run_to_final_third','save_with_reflex','short_medium_pass','vertical_pass','goalkeeper_action_success','action_success','goal_kick_success','goalkeeper_distribution_success','goalkeeper_goal_kick_success','goal_kick_long_success','shot_against_success','near_shot_against_success','any_goal_success','conceded_goal_success','near_conceded_goal_success','any_free_kick_success','pass_success','recovery_success','save_success','buildup_pass_success','forward_pass_success','goal_kick_short_success','goalkeeper_foot_pass_success','goalkeeper_long_pass_success','hand_pass_success','head_conceded_goal_success','interception_success','lateral_pass_success','long_pass_success','long_pass_into_duel_success','long_pass_or_cross_success','long_shot_against_success','pass_followed_by_teammate_loss_success','pass_into_duel_success','penalty_conceded_goal_success','pick_up_success','plus_success','progressive_pass_success','save_with_reflex_success','short_medium_pass_success','vertical_pass_success','xg_shot','xg_assist','xg_save','total_actions','total_actions_success','yellow_card_minute','red_card_minute','quick_recovery','foul_suffered','goalkeeper_sweep','legacy_won_duel','real_won_duel','duel_with_foul','ground_duel','legacy_won_offensive_duel','offensive_duel','offensive_duel_with_progress','offensive_shielding','pass_to_final_third','pass_to_zone_fourteen','clearance','goalkeeper_action_on_free_kick_faced','goalkeeper_short_pass','launch','loose_ball_duel','loss','loss_v2','touch','quick_recovery_success','duel_success','foul_suffered_success','goalkeeper_sweep_success','legacy_won_duel_success','real_won_duel_success','duel_with_foul_success','ground_duel_success','legacy_won_offensive_duel_success','offensive_duel_success','offensive_duel_with_progress_success','offensive_shielding_success','pass_to_final_third_success','pass_to_zone_fourteen_success','goalkeeper_short_pass_success','loose_ball_duel_success','loss_success','loss_v2_success','easy_conceded_goal','received_pass','far_conceded_goal','long_conceded_goal','loss_after_pass','minus','dangerous_own_half_loss','goalkeeper_pass_under_pressure','goalkeeper_short_pass_under_pressure','own_half_loss','pressed_sequence_loss','pressed_sequence_recovery','recovery_counterpressing','through_pass_interception','under_pressure','easy_conceded_goal_success','far_conceded_goal_success','long_conceded_goal_success','received_pass_success','minus_success','through_pass_interception_success','received_long_pass','goalkeeper_action_on_cross_faced_success','received_long_pass_success','goalkeeper_shot_buildup','goalkeeper_accurate_punch','goalkeeper_punch','shot_buildup_pass','pressed_sequence_loss_success','loss_after_pass_success','goalkeeper_shot_buildup_success','goalkeeper_mistake_on_corner_faced','loss_after_duel','aerial_duel_success','aerial_duel_in_own_penalty_area_success','heading_success','clearance_success','dangerous_own_half_loss_success','loss_after_duel_success','own_half_loss_success','recovery_counterpressing_success','launch_success','pressed_sequence_recovery_success','card_suffered','card_suffered_success','goalkeeper_action_on_free_kick_faced_success','last_success','goalkeeper_medium_pass_under_pressure','defensive_duel','legacy_won_defensive_duel','pre_shot_assist','stopped_progress_defensive_duel','defensive_duel_success','legacy_won_defensive_duel_success','pre_shot_assist_success','stopped_progress_defensive_duel_success','penalty_save','penalty_save_success','ball_delivery_to_danger_zone','ball_delivery_to_penalty_area','deep_completed_pass','pass_behind_the_back','pass_to_penalty_area','pass_to_penalty_area_v2','through_pass','very_deep_completion','ball_delivery_to_danger_zone_success','ball_delivery_to_penalty_area_success','deep_completed_pass_success','pass_behind_the_back_success','pass_to_penalty_area_success','pass_to_penalty_area_v2_success','through_pass_success','very_deep_completion_success','goalkeeper_medium_pass_under_pressure_success','goalkeeper_pass_under_pressure_success','under_pressure_success','goalkeeper_short_pass_under_pressure_success','fairplay','infraction','out_of_play_foul','yellow_cards','dangerous_lost_defensive_duel','dribble_against','lost_defensive_duel','run_success','run_to_final_third_success','shot_buildup_pass_success','action_in_counterattack','action_in_counterattack_success','goalkeeper_action_on_corner_faced_success','misconduct','time_lost_foul','goalkeeper_long_pass_under_pressure','highlight','own_goal','goalkeeper_long_pass_under_pressure_success','foul','regular_foul','missed_ball','pre_assist','pre_assist_success','dribble','dribble_attempt','dribble_with_progress','dribble_with_take_on','dribble_won_v2','legacy_dribble_success','one_on_one','dribble_success','dribble_attempt_success','dribble_with_progress_success','dribble_with_take_on_success','dribble_won_v2_success','legacy_dribble_success_success','one_on_one_success','head_pass','head_pass_success','free_kick','free_kick_cross','indirect_free_kick','progressive_run','defensive_one_on_one','dribble_against_with_take_on','dribbled_past_attempt','defensive_duel_regain','super_save','defensive_one_on_one_success','dribble_against_success','dribble_against_with_take_on_success','dribbled_past_attempt_success','defensive_duel_regain_success','super_save_success','red_cards','hand_foul','ball_loss','ball_loss_in_area','penalty_foul','counterattack_interception','dribble_with_space','dribble_with_space_success','counterattack_interception_success','defensive_positioning','covering_depth','opponent_half_recovery','opponent_half_recovery_success','opportunity','received_dangerous_pass','received_deep_completion','received_pass_in_final_third','received_very_deep_completion','right_foot_shot','shot','shot_after_corner','shot_after_received_deep_completion','shot_after_received_very_deep_completion','shot_block','shot_from_box','shot_from_danger_zone','shot_from_penalty_area','shot_from_play','shot_wide','touch_in_box','touch_in_final_third','touch_in_penalty_area','back_pass','back_pass_success','dangerous_foul','head_shot','left_foot_shot','pressing_duel','right_throw_in','shot_after_free_kick','shot_to_far_corner','throw_in','right_throw_in_success','throw_in_success','first_goal','goal','goal_after_corner','head_goal','non_penalty_goal','shot_on_goal','first_goal_success','goal_success','goal_after_corner_success','head_goal_success','head_shot_success','highlight_success','non_penalty_goal_success','opportunity_success','shot_success','shot_after_corner_success','shot_from_box_success','shot_from_danger_zone_success','shot_from_penalty_area_success','shot_from_play_success','shot_on_goal_success','touch_in_box_success','touch_in_final_third_success','touch_in_penalty_area_success','acceleration','back_pass_to_gk','tackle','acceleration_success','back_pass_to_gk_success','progressive_run_success','cross_block','long_ground_pass','off_the_ball','pass_within_final_third','long_ground_pass_success','pass_within_final_third_success','tackle_success','cross_block_success','shot_to_near_corner','key_pass','key_pass_v2','shot_assist','received_progressive_pass','received_deep_completion_success','received_pass_in_final_third_success','received_progressive_pass_success','received_very_deep_completion_success','offside','opportunity_creation','shot_after_free_kick_success','received_cross','received_cross_success','diagonal_to_flank','pass_to_another_flank','pre_pre_assist','pre_pre_assist_success','cross','cross_from_left','cross_low','cross_to_penalty_area','shot_from_cross','shot_on_goal_assist','received_dangerous_pass_success','shot_assist_success','shot_from_cross_success','shot_on_goal_assist_success','pass_to_another_flank_success','left_throw_in','received_pass_in_final_third_on_side','left_throw_in_success','received_pass_in_final_third_on_side_success','shot_on_post','dangerous_opponent_half_recovery','dangerous_opponent_half_recovery_success','cutback','penalty','penalty_goal','right_foot_goal','penalty_success','penalty_goal_success','right_foot_goal_success','right_foot_shot_success','decisive_goal','decisive_goal_success','cross_high','deep_completed_cross','cross_success','cross_from_left_success','cross_high_success','deep_completed_cross_success','smart_pass','low_through_ball','smart_pass_v2','through_pass_v2','shot_block_success','smart_pass_success','smart_pass_v2_success','controlled_penalty_area_entry','controlled_penalty_area_entry_success','blocked_shot','cross_blocked','cross_to_goalie_box','shot_from_outside_area','diagonal_to_flank_success','cross_to_goalie_box_success','protest_foul','left_foot_shot_success','shot_from_outside_area_success','late_card_foul','pending_card','left_foot_goal','successful_dribble_leading_to_shot','cross_to_penalty_area_success','left_foot_goal_success','shot_to_near_corner_success','successful_dribble_leading_to_shot_success','ball_entry_in_final_third','ball_entry_in_final_third_success','opportunity_creation_success','desdoble','desdoble_success','linkup_play','inside_run','inside_run_success','cross_low_success','key_pass_success','key_pass_v2_success','low_through_ball_success','through_pass_v2_success','free_kick_shot_gained','free_kick_shot_gained_success','shot_assist_in_counterattack','shot_assist_in_counterattack_success','short_back_shot_assist','short_back_shot_assist_success','shot_to_far_corner_success','direct_free_kick','free_kick_shot','free_kick_with_shot','direct_free_kick_success','free_kick_success','free_kick_shot_success','free_kick_with_shot_success','shot_after_received_deep_completion_success','shot_after_received_very_deep_completion_success','shot_in_counterattack','corner','cross_from_right','corner_with_shot','corner_won_from_off_duel','linkup_play_success','corner_success','corner_with_shot_success','corner_won_from_off_duel_success','cross_from_right_success','free_kick_cross_success','indirect_free_kick_success','corner_won_from_aerial_duel','corner_won_from_aerial_duel_success','corner_won_from_cross','goal_from_outside_area','deep_completed_run','dribble_in_danger_zone','free_kick_goal','kick_off','goal_from_outside_area_success','corner_won_from_cross_success','deep_completed_run_success','dribble_in_danger_zone_success','free_kick_goal_success','kick_off_success','corner_won_from_shot','corner_won_from_shot_success','penalty_suffered','penalty_suffered_success','assist','assist_success','shot_after_throw_in','corner_won_from_loose_ball_duel','corner_won_from_another_corner','corner_won_from_another_corner_success','goal_after_throw_in','corner_won_from_loose_ball_duel_success','goal_after_throw_in_success','shot_after_throw_in_success','assist_from_set_piece','assist_from_set_piece_success','goal_from_cross','goal_from_cross_success','cutback_success','shot_in_counterattack_success','goal_after_free_kick','goal_after_free_kick_success','touch_success','free_kick_conceded_goal','free_kick_conceded_goal_success']

var = st.selectbox("Metric to Plot", main_cols)
mins = st.number_input("Minimum Minutes Played, Season", value=500)
min_mins = st.number_input("Minimum Minutes Played for Game to Count", value=30)

raw_df.date = pd.to_datetime(raw_df.date)
raw_df['all_buildup_pass'] = raw_df['buildup_pass'] + raw_df['shot_buildup_pass']

position_replacements = {
    'RB':'Fullback','RWB':'Fullback','GK':'Goalkeeper','LCB3':'Center Back','CF':'Striker','CB':'Center Back','RB5':'Fullback','RCB':'Center Back','LB':'Fullback','DMF':'Midfielder','RCMF':'Midfielder','RDMF':'Midfielder','LCB':'Center Back','RCB3':'Center Back','AMF':'Midfielder','LW':'Winger','LCMF':'Midfielder','LWB':'Fullback','RW':'Winger','LB5':'Fullback','LCMF3':'Midfielder','RWF':'Winger','RAMF':'Winger','LDMF':'Midfielder','LWF':'Winger','RCMF3':'Midfielder','LAMF':'Winger',
}
df['Primary position'] = df['Primary position'].replace(position_replacements)

df = df[(df['Minutes played']>=mins)]

data = raw_df[raw_df['player'].isin(df['Full name'].tolist())]
data['main_position'] = data['main_position'].replace(position_replacements)

data[f"{var}/90"] = data[var] / (data['minutes_on_field']/90)

data['match_name'] = data.teamA + " " + data.score + " " + data.teamB
data = data[data['minutes_on_field']>=min_mins]

positions = ['']+sorted(data['main_position'].unique().tolist())
teams = ['']+sorted(data.club.unique().tolist())

y_domain_min = 0 if min(data[f"{var}/90"]) >= 0 else min(data[f"{var}/90"])-1
y_domain_max = max(data[f"{var}/90"])+1

x_domain_max = data.groupby(['player'])[f"{var}/90"].mean().max()*1.05

date_min = data.date.min()
date_max = data.date.max()

fig, ax = plt.subplots(2, 1, figsize=(10, 12))

# Bar chart
team_dropdown = st.selectbox("Team", teams)
pos_dropdown = st.selectbox("Position", positions)

filtered_data = data
if pos_dropdown:
    filtered_data = filtered_data[filtered_data['main_position'] == pos_dropdown]
if team_dropdown:
    filtered_data = filtered_data[filtered_data['club'] == team_dropdown]

player_dropdown = st.selectbox("Player", filtered_data.full_name.unique().tolist())

if player_dropdown:
    filtered_data = filtered_data[filtered_data['full_name'] == player_dropdown]

bar_data = filtered_data.groupby('player')[f"{var}/90"].mean().sort_values(ascending=False)
ax[0].barh(bar_data.index, bar_data.values, color='#806c5e', edgecolor='#4a2e19', linewidth=0.5)
ax[0].set_xlim(0, x_domain_max)
ax[0].set_xlabel(f"{var.replace('_',' ').title()} per 90'")
ax[0].set_ylabel("Player")
ax[0].set_title(f"{league} {ssn}, {var.replace('_',' ').title()} per 90'\nIncludes players with at least {mins} minutes played")

# Time series chart
for player in filtered_data['player'].unique():
    player_data = filtered_data[filtered_data['player'] == player]
    ax[1].plot(player_data['date'], player_data[f"{var}/90"], label=player, marker='o')

ax[1].set_xlim(date_min, date_max)
ax[1].set_ylim(y_domain_min, y_domain_max)
ax[1].set_xlabel('Match Date')
ax[1].set_ylabel(f"{var.replace('_',' ').title()} per 90'")
ax[1].set_title(f"{var.replace('_',' ').title()} per 90', Match-by-Match Breakdown\nOnly includes games that players played at least {min_mins} mins.")
ax[1].xaxis.set_major_locator(mdates.MonthLocator())
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax[1].legend(loc='upper left', bbox_to_anchor=(1, 1))

plt.tight_layout()
st.pyplot(fig)
