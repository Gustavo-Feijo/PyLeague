-- In order to save up storage, two additional tables to the stats of the games were added, due to the repetition of the PUUID and Match ID fields.
-- Create statement for storing the player information.
CREATE TABLE IF NOT EXISTS tb_player_info (
    -- ID of the player.
    id INT PRIMARY KEY AUTO_INCREMENT,
    -- Unique identifier for the player (Globally).
    puuid CHAR(78) UNIQUE NOT NULL,
    -- Unique identifier for the account (Locally), not  in use for now.
    account_id CHAR(56),
    -- Name of the player inGame. Being inserted on the name at the time.
    game_name VARCHAR(50),
    -- Tag line of the player account. Not used for now.
    tag_line VARCHAR(5),
    -- Level of the player. Not used for now.
    summoner_level SMALLINT UNSIGNED,
    -- Profile icon of the player. Not used for now.
    profile_icon_id SMALLINT UNSIGNED,
    -- Last time the data of the player was fetched, used to mantain the fetch up to date.
    last_fetch TIMESTAMP DEFAULT '2024-01-01 00:00:00'
);

-- Create statement for storing the match information.
create table IF NOT EXISTS tb_match_info(
    -- ID of the match as a int.
    id int primary key auto_increment,
    -- Original ID of the match.
    match_id varchar(20) unique not null,
    -- Date of start of the match.
    match_start DATETIME,
    -- Duration of the match.
    match_duration SMALLINT UNSIGNED,
    -- Winner of the match. TRUE/1 => Blue team won.
    match_winner boolean,
    -- Match resulted on surrender.
    match_surrender boolean,
    -- Match resulted on remake. Preferably not use remaked matches when analysing the data.
    match_remake boolean
);

-- Create statement for storing the individual perfomance of each player in a given match.
create table IF NOT EXISTS tb_player_stats (
    -- ID of the player perfomance, used only as a primary key.
    id int auto_increment primary key,
    -- ID of the player, foreign key. Before inserted the id must be got from the corresponding PUUID.
    player_id int,
    -- ID of the match, foreign key. Before inserted the id must be got from the corresponding Match_ID.
    match_id int,
    -- ID of the champion used by the player. Data about this can be retrieved from DataDragon. A small database for that can also be created.
    champion_id SMALLINT UNSIGNED,
    -- Ammount of kills, death, assists and the calculation of ((K+A)/D).
    kills SMALLINT UNSIGNED,
    deaths SMALLINT UNSIGNED,
    assists SMALLINT UNSIGNED,
    kda float,
    -- Gold stats.
    gold_earned int,
    gold_spent int,
    gold_per_minute float,
    --Damage stats.
    damage_per_minute float,
    total_damage_dealt_to_champions int,
    --Farm stats.
    neutral_minions_killed SMALLINT UNSIGNED,
    total_minions_killed SMALLINT UNSIGNED,
    total_cs SMALLINT UNSIGNED,
    cs_per_min float,
    -- Vision stats.
    vision_score SMALLINT UNSIGNED,
    vision_score_per_min float,
    control_wards_placed SMALLINT UNSIGNED,
    wards_placed SMALLINT UNSIGNED,
    wards_killed SMALLINT UNSIGNED,
    --Individual position of the player on the game. Invalid was added due to the way that Riot works with their position system.
    individual_position ENUM(
        'TOP',
        'JUNGLE',
        'MIDDLE',
        'BOTTOM',
        'UTILITY',
        'Invalid'
    ),
    FOREIGN KEY (player_id) references tb_player_info(id),
    FOREIGN KEY (match_id) references tb_match_info(id),
    -- Unique composite key to avoid the same player being added twich from a match he already played.
    -- This should not happen normally.
    UNIQUE KEY (player_id, match_id)
);