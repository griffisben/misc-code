import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
import os
from pathlib import Path
import time
import warnings
warnings.filterwarnings("ignore")


comps = ['Liga MX', 'MLS', 'Brasileirão', 'Eredivisie', 'Primeira Liga', 'Championship']

for k in range(len(comps)):
    comp = comps[k]
    print('Working on %s' %comp)

    raw_nongk = 'Raw FBRef 2022-2023 - %s' %comp
    raw_gk = 'Raw FBRef GK 2022-2023 - %s' %comp
    final_nongk = 'Final FBRef 2022-2023 - %s' %comp
    final_gk = 'Final FBRef GK 2022-2023 - %s' %comp

    if comp == 'Liga MX':
        lg_str = 'Liga-MX'
        lg_id = 31
    if comp == 'MLS':
        lg_str = 'Major-League-Soccer'
        lg_id = 22
    if comp == 'Brasileirão':
        lg_str = 'Serie-A'
        lg_id = 24
    if comp == 'Eredivisie':
        lg_str = 'Eredivisie'
        lg_id = 23
    if comp == 'Primeira Liga':
        lg_str = 'Primeira-Liga'
        lg_id = 32
    if comp == 'Championship':
        lg_str = 'Championship'
        lg_id = 10
    

    # this is the file path root, i.e. where this file is located
    root = str(Path(os.getcwd()).parents[0]).replace('\\','/')+'/'

    # This section creates the programs that gather data from FBRef.com... Data is from FBRef and Opta
    def _get_table(soup):
        return soup.find_all('table')[0]

    def _get_opp_table(soup):
        return soup.find_all('table')[1]

    def _parse_row(row):
        cols = None
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        return cols

    def _parse_team_row(row):
        cols = None
        cols = row.find_all(['td', 'th'])
        cols = [ele.text.strip() for ele in cols]
        return cols

    def get_players_df(path):
        URL = path
        time.sleep(4)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        comment = soup.find_all(text=lambda t: isinstance(t, Comment))
        c=0
        for i in range(len(comment)):
            if comment[i].find('\n\n<div class="table_container"') != -1:
                c = i
        a = comment[c]
        tbody = a.find('table')
        sp = BeautifulSoup(a[tbody:], 'html.parser')
        table = _get_table(sp)
        data = []
        headings=[]
        headtext = sp.find_all("th",scope="col")
        for i in range(len(headtext)):
            heading = headtext[i].get_text()
            headings.append(heading)
        headings=headings[1:len(headings)]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row_index in range(len(rows)):
            row = rows[row_index]
            cols = _parse_row(row)
            data.append(cols)

        data = pd.DataFrame(data)
        data = data.rename(columns=data.iloc[0])
        data = data.reindex(data.index.drop(0))
        data = data.replace('',0)
        data.insert(4, 'Comp', [comp]*len(data))
        return data

    def get_team_df(path):
        URL = path
        time.sleep(4)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        table = _get_table(soup)
        data = []
        headings=[]
        headtext = soup.find_all("th",scope="col")
        for i in range(len(headtext)):
            heading = headtext[i].get_text()
            headings.append(heading)
        headings=headings[0:len(headings)]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row_index in range(len(rows)):
            row = rows[row_index]
            cols = _parse_team_row(row)
            data.append(cols)

        data = pd.DataFrame(data)
        data = data.rename(columns=data.iloc[0])
        data = data.reindex(data.index.drop(0))
        data = data.replace('',0)
        data.insert(1, 'Comp', [comp]*len(data))
        return data


    def get_opp_df(path):
        URL = path
        time.sleep(4)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        table = _get_opp_table(soup)
        data = []
        headings=[]
        headtext = soup.find_all("th",scope="col")
        for i in range(len(headtext)):
            heading = headtext[i].get_text()
            headings.append(heading)
        headings=headings[0:len(headings)]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row_index in range(len(rows)):
            row = rows[row_index]
            cols = _parse_team_row(row)
            data.append(cols)

        data = pd.DataFrame(data)
        data = data.rename(columns=data.iloc[0])
        data = data.reindex(data.index.drop(0))
        data = data.replace('',0)
        data.insert(1, 'Comp', [comp]*len(data))
        return data


    # this section gets the raw tables from FBRef.com

    standard = "https://fbref.com/en/comps/%i/stats/%s-Stats" %(lg_id, lg_str)
    shooting = "https://fbref.com/en/comps/%i/shooting/%s-Stats" %(lg_id, lg_str)
    passing = "https://fbref.com/en/comps/%i/passing/players/%s-Stats" %(lg_id, lg_str)
    pass_types = "https://fbref.com/en/comps/%i/passing_types/players/%s-Stats" %(lg_id, lg_str)
    gsca = "https://fbref.com/en/comps/%i/gca/players/%s-Stats" %(lg_id, lg_str)
    defense = "https://fbref.com/en/comps/%i/defense/players/%s-Stats" %(lg_id, lg_str)
    poss = "https://fbref.com/en/comps/%i/possession/players/%s-Stats" %(lg_id, lg_str)
    misc = "https://fbref.com/en/comps/%i/misc/players/%s-Stats" %(lg_id, lg_str)

    df_standard = get_players_df(standard)
    df_shooting = get_players_df(shooting)
    df_passing = get_players_df(passing)
    df_pass_types = get_players_df(pass_types)
    df_gsca = get_players_df(gsca)
    df_defense = get_players_df(defense)
    df_poss = get_players_df(poss)
    df_misc = get_players_df(misc)

    # this section sorts the raw tables then resets their indexes. Without this step, you will
    # run into issues with players who play minutes for 2 clubs in a season.

    df_standard.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_shooting.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_passing.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_pass_types.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_gsca.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_defense.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_poss.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_misc.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)

    df_standard = df_standard.reset_index(drop=True)
    df_shooting = df_shooting.reset_index(drop=True)
    df_passing = df_passing.reset_index(drop=True)
    df_pass_types = df_pass_types.reset_index(drop=True)
    df_gsca = df_gsca.reset_index(drop=True)
    df_defense = df_defense.reset_index(drop=True)
    df_poss = df_poss.reset_index(drop=True)
    df_misc = df_misc.reset_index(drop=True)

    # Now the fun part... merging all raw tables into one.
    # Change any column name you want to change:
    # Example --   'Gls': 'Goals'  changes column "Gls" to be named "Goals", etc.
    ## Note that I inclide all columns but don't always change the names... this is useful to me when I need to update the columns, like when FBRef witched to Opta data haha. I got lucky as this made it easier on me!

    df = df_standard.iloc[:, 0:10]
    df = df.join(df_standard.iloc[:, 13])
    df = df.join(df_standard.iloc[:, 26])
    df = df.rename(columns={'G-PK': 'npGoals'})
    df = df.join(df_shooting.iloc[:,8:25])
    df = df.rename(columns={'Gls': 'Goals', 'Sh': 'Shots', 'SoT': 'SoT', 'SoT%': 'SoT%', 'Sh/90': 'Sh/90', 'SoT/90': 'SoT/90', 'G/Sh': 'G/Sh', 'G/SoT': 'G/SoT', 'Dist': 'AvgShotDistance', 'FK': 'FKShots', 'PK': 'PK', 'PKatt': 'PKsAtt', 'xG': 'xG', 'npxG': 'npxG', 'npxG/Sh': 'npxG/Sh', 'G-xG': 'G-xG', 'np:G-xG': 'npG-xG'})

    df = df.join(df_passing.iloc[:,8:13])
    df = df.rename(columns={'Cmp': 'PassesCompleted', 'Att': 'PassesAttempted', 'Cmp%': 'TotCmp%', 'TotDist': 'TotalPassDist', 'PrgDist': 'ProgPassDist', })
    df = df.join(df_passing.iloc[:,13:16])
    df = df.rename(columns={'Cmp': 'ShortPassCmp', 'Att': 'ShortPassAtt', 'Cmp%': 'ShortPassCmp%', })
    df = df.join(df_passing.iloc[:,16:19])
    df = df.rename(columns={'Cmp': 'MedPassCmp', 'Att': 'MedPassAtt', 'Cmp%': 'MedPassCmp%', })
    df = df.join(df_passing.iloc[:,19:22])
    df = df.rename(columns={'Cmp': 'LongPassCmp', 'Att': 'LongPassAtt', 'Cmp%': 'LongPassCmp%', })
    df = df.join(df_passing.iloc[:,22:31])
    df = df.rename(columns={'Ast': 'Assists', 'xAG':'xAG', 'xA': 'xA', 'A-xA': 'A-xA', 'KP': 'KeyPasses', '1/3': 'Final1/3Cmp', 'PPA': 'PenAreaCmp', 'CrsPA': 'CrsPenAreaCmp', 'Prog': 'ProgPasses', })

    df = df.join(df_pass_types.iloc[:, 9:23])
    df = df.rename(columns={'Live': 'LivePass', 'Dead': 'DeadPass', 'FK': 'FKPasses', 'TB': 'ThruBalls', 'Sw': 'Switches', 'Crs': 'Crs', 'CK': 'CK', 'In': 'InSwingCK', 'Out': 'OutSwingCK', 'Str': 'StrCK', 'TI': 'ThrowIn', 'Off': 'PassesToOff', 'Blocks':'PassesBlocked'})

    df = df.join(df_gsca.iloc[:, 8:16].rename(columns={'SCA': 'SCA', 'SCA90': 'SCA90', 'PassLive': 'SCAPassLive', 'PassDead': 'SCAPassDead', 'Drib': 'SCADrib', 'Sh': 'SCASh', 'Fld': 'SCAFld', 'Def': 'SCADef'}))
    df = df.join(df_gsca.iloc[:, 16:24].rename(columns={'GCA': 'GCA', 'GCA90': 'GCA90', 'PassLive': 'GCAPassLive', 'PassDead': 'GCAPassDead', 'Drib': 'GCADrib', 'Sh': 'GCASh', 'Fld': 'GCAFld', 'Def': 'GCADef'}))

    df = df.join(df_defense.iloc[:,8:13].rename(columns={'Tkl': 'Tkl', 'TklW': 'TklWinPoss', 'Def 3rd': 'Def3rdTkl', 'Mid 3rd': 'Mid3rdTkl', 'Att 3rd': 'Att3rdTkl'}))
    df = df.join(df_defense.iloc[:,13:24].rename(columns={'Tkl': 'DrbTkl', 'Att': 'DrbPastAtt', 'Tkl%': 'DrbTkl%', 'Past': 'DrbPast', 'Blocks': 'Blocks', 'Sh': 'ShBlocks', 'Pass': 'PassBlocks', 'Int': 'Int', 'Tkl+Int': 'Tkl+Int', 'Clr': 'Clr', 'Err': 'Err'}))

    df = df.join(df_poss.iloc[:,8:22])
    df = df.rename(columns={'Touches': 'Touches', 'Def Pen': 'DefPenTouch', 'Def 3rd': 'Def3rdTouch', 'Mid 3rd': 'Mid3rdTouch', 'Att 3rd': 'Att3rdTouch', 'Att Pen': 'AttPenTouch', 'Live': 'LiveTouch', 'Succ': 'SuccDrb', 'Att': 'AttDrb', 'Succ%': 'DrbSucc%', 'Mis': 'CarryMistakes', 'Dis': 'Disposesed', 'Targ': 'PassTarget', 'Rec': 'ReceivedPass', 'Prog':'ProgPassesRec'})

    df = df.join(df_misc.iloc[:, 8:14])
    df = df.rename(columns={'CrdY': 'Yellows', 'CrdR': 'Reds', '2CrdY': 'Yellow2', 'Fls': 'Fls', 'Fld': 'Fld', 'Off': 'Off', })
    df = df.join(df_misc.iloc[:,17:24])
    df = df.rename(columns={'PKwon': 'PKwon', 'PKcon': 'PKcon', 'OG': 'OG', 'Recov': 'Recov', 'Won': 'AerialWins', 'Lost': 'AerialLoss', 'Won%': 'AerialWin%', })

    # Make sure to drop all blank rows (FBRef's tables have several)
    df.dropna(subset = ["Player"], inplace=True)

    # Turn the minutes columns to integers. So from '1,500' to '1500'. Otherwise it can't do calculations with minutes
    for i in range(0,len(df)):
        df.iloc[i][9] = df.iloc[i][9].replace(',','')
    df.iloc[:,9:] = df.iloc[:,9:].apply(pd.to_numeric)

    # Save the file to the root location
    df.to_csv("%s%s.csv" %(root, raw_nongk), index=False)


    ##################################################################################
    ############################## GK SECTION ########################################
    ##################################################################################

    gk = "https://fbref.com/en/comps/%i/keepers/players/%s-Stats" %(lg_id, lg_str)
    advgk = "https://fbref.com/en/comps/%i/keepersadv/players/%s-Stats" %(lg_id, lg_str)

    df_gk = get_players_df(gk)
    df_advgk = get_players_df(advgk)

    df_gk.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
    df_advgk.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)

    df_gk = df_gk.reset_index(drop=True)
    df_advgk = df_advgk.reset_index(drop=True)

    ###############################################################################

    df = pd.read_csv("%s%s.csv" %(root, raw_nongk))
    df = df[df['Pos'].str.contains("GK")].reset_index().iloc[:,1:]
    df_gk['Pos'] = df_gk['Pos'].astype(str)
    df_gk = df_gk[df_gk['Pos'].str.contains('GK')]
    df_gk = df_gk.reset_index().iloc[:,1:]
    df_gk = df_gk.rename(columns={'PKatt':'PKsFaced'})

    df = df.join(df_gk.iloc[:, 11:26].astype(float), lsuffix='.1', rsuffix='.2')
    df = df.rename(columns={'GA': 'GA', 'GA90': 'GA90', 'SoTA': 'SoTA', 'Saves': 'Saves', 'Save%.1': 'Save%', 'W': 'W', 'D': 'D', 'L': 'L', 'CS': 'CS', 'CS%': 'CS%', 'PKsFaced': 'PKsFaced', 'PKA': 'PKA', 'PKsv': 'PKsv', 'PKm': 'PKm', 'Save%.2': 'PKSave%', })

    df_advgk['Pos'] = df_advgk['Pos'].astype(str)
    df_advgk = df_advgk[df_advgk['Pos'].str.contains('GK')]
    df_advgk = df_advgk.reset_index().iloc[:,1:]
    df = df.join(df_advgk.iloc[:,9:20].astype(float).rename(columns={'PKA': 'PKGA', 'FK': 'FKGA', 'CK': 'CKGA', 'OG': 'OGA', 'PSxG': 'PSxG', 'PSxG/SoT': 'PSxG/SoT', 'PSxG+/-': 'PSxG+/-', '/90': 'PSxG+/- /90', 'Cmp': 'LaunchCmp', 'Att': 'LaunchAtt', 'Cmp%': 'LaunchPassCmp%'}))
    df = df.join(df_advgk.iloc[:,20:24].astype(float).rename(columns={'Att': 'PassAtt', 'Thr': 'PassThr', 'Launch%': 'PassesLaunch%', 'AvgLen': 'AvgLenLaunch'}))
    df = df.join(df_advgk.iloc[:,24:33].astype(float).rename(columns={'Att': 'GoalKicksAtt', 'Launch%': 'GoalKicksLaunch%', 'AvgLen': 'AvgLen', 'Opp': 'OppCrs', 'Stp': 'StpCrs', 'Stp%': 'CrsStp%', '#OPA': '#OPA', '#OPA/90': '#OPA/90', 'AvgDist': 'AvgDistOPA'}))

    df.to_csv("%s%s.csv" %(root,raw_gk), index=False)

    ##################################################################################
    ##################### Final file for outfield data ###############################
    ##################################################################################

    df = pd.read_csv("%s%s.csv" %(root, raw_nongk))
    df_90s = pd.read_csv("%s%s.csv" %(root, raw_nongk))
    df_90s['90s'] = df_90s['Min']/90
    for i in range(10,125):
        df_90s.iloc[:,i] = df_90s.iloc[:,i]/df_90s['90s']
    df_90s = df_90s.iloc[:,10:].add_suffix('Per90')
    df_new = df.join(df_90s)

    if comp in ['Liga MX', 'Primeira Liga', 'Eredivisie', 'Championship']:
        for i in range(len(df_new)):
            df_new['Age'][i] = int(df_new['Age'][i][:2])

    df_new.to_csv("%s%s.csv" %(root, final_nongk), index=False)


    ##################################################################################
    ##################### Final file for keeper data #################################
    ##################################################################################

    df = pd.read_csv("%s%s.csv" %(root, raw_gk))
    df_90s = pd.read_csv("%s%s.csv" %(root, raw_gk))
    df_90s['90s'] = df_90s['Min']/90
    for i in range(10,164):
        df_90s.iloc[:,i] = df_90s.iloc[:,i]/df_90s['90s']
    df_90s = df_90s.iloc[:,10:].add_suffix('Per90')
    df_new = df.join(df_90s)

    if comp in ['Liga MX', 'Primeira Liga', 'Eredivisie', 'Championship']:
        for i in range(len(df_new)):
            df_new['Age'][i] = int(df_new['Age'][i][:2])

    df_new.to_csv("%s%s.csv" %(root, final_gk), index=False)


    ##################################################################################
    ################ Download team data, for possession-adjusting ####################
    ##################################################################################

    standard = "https://fbref.com/en/comps/%i/stats/squads/%s-Stats" %(lg_id, lg_str)
    poss = "https://fbref.com/en/comps/%i/possession/squads/%s-Stats" %(lg_id, lg_str)

    df_standard = get_team_df(standard)
    df_poss = get_team_df(poss)

    df_standard = df_standard.reset_index(drop=True)
    df_poss = df_poss.reset_index(drop=True)

    ############################################

    df = df_standard.iloc[:, 0:30]

    # Gets the number of touches a team has per 90
    df['TeamTouches90'] = float(0.0)
    for i in range(len(df)):
        df.iloc[i,30] = float(df_poss.iloc[i,5]) / float(df_poss.iloc[i,4])

    # Take out the comma in minutes like above
    for j in range(0,len(df)):
        df.at[j,'Min'] = df.at[j,'Min'].replace(',','')
    df.iloc[:,7:] = df.iloc[:,7:].apply(pd.to_numeric)
    df.to_csv("%s%s TEAMS.csv" %(root, final_nongk), index=False)


    ##################################################################################
    ################ Download opposition data, for possession-adjusting ##############
    ##################################################################################

    opp_poss = "https://fbref.com/en/comps/%i/possession/squads/%s-Stats" %(lg_id, lg_str)

    df_opp_poss = get_opp_df(opp_poss)
    df_opp_poss = df_opp_poss.reset_index(drop=True)

    ############################################

    df = df_opp_poss.iloc[:, 0:15]
    df = df.rename(columns={'Touches':'Opp Touches'})
    df = df.reset_index()

    #############################################

    df1 = pd.read_csv("%s%s TEAMS.csv"%(root, final_nongk))

    df1['Opp Touches'] = 1
    for i in range(len(df1)):
        df1['Opp Touches'][i] = df['Opp Touches'][i]
    df1 = df1.rename(columns={'Min':'Team Min'})
    df1.to_csv("%s%s TEAMS.csv" %(root, final_nongk), index=False)


    ##################################################################################
    ################ Make the final, complete, outfield data file ####################
    ##################################################################################

    df = pd.read_csv("%s%s.csv" %(root, final_nongk))
    teams = pd.read_csv("%s%s TEAMS.csv" %(root, final_nongk))

    df['AvgTeamPoss'] = float(0.0)
    df['OppTouches'] = int(1)
    df['TeamMins'] = int(1)
    df['TeamTouches90'] = float(0.0)

    player_list = list(df['Player'])

    for i in range(len(player_list)):
        team_name = df[df['Player']==player_list[i]]['Squad'].values[0]
        team_poss = teams[teams['Squad']==team_name]['Poss'].values[0]
        opp_touch = teams[teams['Squad']==team_name]['Opp Touches'].values[0]
        team_mins = teams[teams['Squad']==team_name]['Team Min'].values[0]
        team_touches = teams[teams['Squad']==team_name]['TeamTouches90'].values[0]
        df.at[i, 'AvgTeamPoss'] = team_poss
        df.at[i, 'OppTouches'] = opp_touch
        df.at[i, 'TeamMins'] = team_mins
        df.at[i, 'TeamTouches90'] = team_touches

    # All of these are the possession-adjusted columns. A couple touch-adjusted ones at the bottom
    df['pAdjTkl+IntPer90'] = (df['Tkl+IntPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjClrPer90'] = (df['ClrPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjShBlocksPer90'] = (df['ShBlocksPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjPassBlocksPer90'] = (df['PassBlocksPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjIntPer90'] = (df['IntPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjDrbTklPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjTklWinPossPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjDrbPastPer90'] = (df['DrbPastPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjAerialWinsPer90'] = (df['AerialWinsPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjAerialLossPer90'] = (df['AerialLossPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjDrbPastAttPer90'] = (df['DrbPastAttPer90']/(100-df['AvgTeamPoss']))*50
    df['TouchCentrality'] = (df['TouchesPer90']/df['TeamTouches90'])*100
    df['Tkl+IntOppTouch'] = df['Tkl+Int'] /(df['OppTouches']*(df['Min']/df['TeamMins']))*600
    df['pAdjTouchesPer90'] = (df['TouchesPer90']/(df['AvgTeamPoss']))*50


    # Now we'll add the players' actual positions, from @jaseziv, into the file
    tm_pos = pd.read_csv('https://github.com/griffisben/Soccer-Analyses/blob/main/TransfermarktPositions-Jase_Ziv83.csv?raw=true')
    df = pd.merge(df, tm_pos, on ='Player', how ='left')

    for i in range(len(df)):
        if df.Pos[i] == 'GK':
            df['Main Position'][i] = 'Goalkeeper'
    df.to_csv("%s%s.csv" %(root, final_nongk), index=False)


    ##################################################################################
    ################ Make the final, complete, keepers data file #####################
    ##################################################################################

    df = pd.read_csv("%s%s.csv" %(root, final_gk))
    teams = pd.read_csv("%s%s TEAMS.csv" %(root, final_nongk))

    df['AvgTeamPoss'] = float(0.0)
    df['OppTouches'] = int(1)
    df['TeamMins'] = int(1)
    df['TeamTouches90'] = float(0.0)

    player_list = list(df['Player'])

    for i in range(len(player_list)):
        team_name = df[df['Player']==player_list[i]]['Squad'].values[0]
        team_poss = teams[teams['Squad']==team_name]['Poss'].values[0]
        opp_touch = teams[teams['Squad']==team_name]['Opp Touches'].values[0]
        team_mins = teams[teams['Squad']==team_name]['Team Min'].values[0]
        team_touches = teams[teams['Squad']==team_name]['TeamTouches90'].values[0]
        df.at[i, 'AvgTeamPoss'] = team_poss
        df.at[i, 'OppTouches'] = opp_touch
        df.at[i, 'TeamMins'] = team_mins
        df.at[i, 'TeamTouches90'] = team_touches

    # Same thing, makes pAdj stats for the GK file
    df['pAdjTkl+IntPer90'] = (df['Tkl+IntPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjClrPer90'] = (df['ClrPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjShBlocksPer90'] = (df['ShBlocksPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjPassBlocksPer90'] = (df['PassBlocksPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjIntPer90'] = (df['IntPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjDrbTklPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjTklWinPossPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjDrbPastPer90'] = (df['DrbPastPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjAerialWinsPer90'] = (df['AerialWinsPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjAerialLossPer90'] = (df['AerialLossPer90']/(100-df['AvgTeamPoss']))*50
    df['pAdjDrbPastAttPer90'] = (df['DrbPastAttPer90']/(100-df['AvgTeamPoss']))*50
    df['TouchCentrality'] = (df['TouchesPer90']/df['TeamTouches90'])*100
    df['pAdj#OPAPer90'] =(df['#OPAPer90']/(100-df['AvgTeamPoss']))*50
    df['Tkl+IntOppTouch'] = df['Tkl+Int'] /(df['OppTouches']*(df['Min']/df['TeamMins']))*600
    df['pAdjTouchesPer90'] = (df['TouchesPer90']/(df['AvgTeamPoss']))*50


    # Just adding the main positions to the GK too, but of course, they will all be GK lol. Keeps other program variables clean
    tm_pos = pd.read_csv('https://github.com/griffisben/Soccer-Analyses/blob/main/TransfermarktPositions-Jase_Ziv83.csv?raw=true')
    df = pd.merge(df, tm_pos, on ='Player', how ='left')

    for i in range(len(df)):
        if df.Pos[i] == 'GK':
            df['Main Position'][i] = 'Goalkeeper'
    df.to_csv("%s%s.csv" %(root, final_gk), index=False)

df_usa = pd.read_csv("%sFinal FBRef 2022-2023 - MLS.csv" %root)
df_bra = pd.read_csv("%sFinal FBRef 2022-2023 - Brasileirão.csv" %root)
df_mex = pd.read_csv("%sFinal FBRef 2022-2023 - Liga MX.csv" %root)
df_ned = pd.read_csv("%sFinal FBRef 2022-2023 - Eredivisie.csv" %root)
df_por = pd.read_csv("%sFinal FBRef 2022-2023 - Primeira Liga.csv" %root)
df_eng = pd.read_csv("%sFinal FBRef 2022-2023 - Championship.csv" %root)

df = df_usa.append(df_bra)
df = df.append(df_mex)
df = df.append(df_ned)
df = df.append(df_por)
df = df.append(df_eng)
df.to_csv('%sSecond 6 Leagues.csv' %root)

df_usa = pd.read_csv("%sFinal FBRef GK 2022-2023 - MLS.csv" %root)
df_bra = pd.read_csv("%sFinal FBRef GK 2022-2023 - Brasileirão.csv" %root)
df_mex = pd.read_csv("%sFinal FBRef GK 2022-2023 - Liga MX.csv" %root)
df_ned = pd.read_csv("%sFinal FBRef GK 2022-2023 - Eredivisie.csv" %root)
df_por = pd.read_csv("%sFinal FBRef GK 2022-2023 - Primeira Liga.csv" %root)
df_eng = pd.read_csv("%sFinal FBRef GK 2022-2023 - Championship.csv" %root)

df = df_usa.append(df_bra)
df = df.append(df_mex)
df = df.append(df_ned)
df = df.append(df_por)
df = df.append(df_eng)
df.to_csv('%sSecond 6 Leagues GK.csv' %root)

print('Done :) Files are located at  %s' %root)

