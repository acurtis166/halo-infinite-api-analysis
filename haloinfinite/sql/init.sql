/*
  Database initialization script
*/

-- ----------------------------
-- Table structure for experience
-- ----------------------------
-- DROP TABLE IF EXISTS "public"."experience";
-- CREATE TABLE "public"."experience" (
--   "id" smallserial PRIMARY KEY,
--   "name" text UNIQUE NOT NULL
-- );
-- INSERT INTO "experience" ("name")
-- VALUES ('arena'), ('btb'), ('featured'), ('pve-bots');

-- ----------------------------
-- Table structure for category
-- ----------------------------
DROP TABLE IF EXISTS "public"."category";
CREATE TABLE "public"."category" (
  "id" int2 PRIMARY KEY,
  "name" text
);
-- sourced from autocode halo api
INSERT INTO "category" ("id", "name")
VALUES
  (1, 'Campaign'),
  (6, 'Slayer'),
  (7, 'Attrition'),
  (9, 'Fiesta'),
  (11, 'Strongholds'),
  (12, 'KoTH'),
  (14, 'Total Control'),
  (15, 'CTF'),
  (16, 'Assault'),
  (17, 'Extraction'),
  (18, 'Oddball'),
  (19, 'Stockpile'),
  (20, 'Juggernaut'),
  (23, 'VIP'),
  (24, 'Escalation'),
  (25, 'Grifball'),
  (27, 'Unknown'),
  (32, 'Unknown'),
  (36, 'Unknown'),
  (39, 'Land Grab');

-- ----------------------------
-- Table structure for mode
-- ----------------------------
DROP TABLE IF EXISTS "public"."mode";
CREATE TABLE "public"."mode" (
  "id" smallserial PRIMARY KEY,
  "asset_id" text UNIQUE NOT NULL,
  "category_id" int2 NOT NULL REFERENCES "category" ("id"),
  "context" text,
  "name" text
);

-- ----------------------------
-- Table structure for mode_version
-- ----------------------------
DROP TABLE IF EXISTS "public"."mode_version";
CREATE TABLE "public"."mode_version" (
  "id" smallserial PRIMARY KEY,
  "mode_id" int2 NOT NULL REFERENCES "mode" ("id"),
  "version_id" text NOT NULL,
  UNIQUE("mode_id", "version_id")
);

-- ----------------------------
-- Table structure for map
-- ----------------------------
DROP TABLE IF EXISTS "public"."map";
CREATE TABLE "public"."map" (
  "id" smallserial PRIMARY KEY,
  "asset_id" text UNIQUE NOT NULL,
  "level_id" text UNIQUE NOT NULL,
  "name" text
);

-- ----------------------------
-- Table structure for map_version
-- ----------------------------
DROP TABLE IF EXISTS "public"."map_version";
CREATE TABLE "public"."map_version" (
  "id" smallserial PRIMARY KEY,
  "map_id" int2 NOT NULL,
  "version_id" text NOT NULL,
  UNIQUE("map_id", "version_id")
);

-- ----------------------------
-- Table structure for playlist
-- ----------------------------
DROP TABLE IF EXISTS "public"."playlist";
CREATE TABLE "public"."playlist" (
  "id" smallserial PRIMARY KEY,
  "asset_id" text UNIQUE NOT NULL,
  "name" text,
  "is_ranked" bool,
  "is_controller" bool, -- controller input accepted
  "is_mnk" bool, -- mouse and keyboard input accepted
  "max_fireteam_size" int2 -- can be used to determine open or solo/duo queue
);

-- ----------------------------
-- Table structure for playlist_version
-- ----------------------------
DROP TABLE IF EXISTS "public"."playlist_version";
CREATE TABLE "public"."playlist_version" (
  "id" smallserial PRIMARY KEY,
  "playlist_id" int2 NOT NULL,
  "version_id" text NOT NULL,
  UNIQUE("playlist_id", "version_id")
);

-- ----------------------------
-- Table structure for match_type
-- ----------------------------
-- DROP TABLE IF EXISTS "public"."match_type";
-- CREATE TABLE "public"."match_type" (
--   "id" smallserial PRIMARY KEY,
--   "name" text UNIQUE NOT NULL
-- );
-- INSERT INTO "match_type" ("name")
-- VALUES ('matchmaking'), ('featured'), ('pve-bots'), ('custom'), ('local');

-- ----------------------------
-- Table structure for medal_difficulty
-- ----------------------------
DROP TABLE IF EXISTS "public"."medal_difficulty";
CREATE TABLE "public"."medal_difficulty" (
  "id" smallserial PRIMARY KEY,
  "name" text UNIQUE NOT NULL
);
INSERT INTO "medal_difficulty" ("name")
VALUES ('normal'), ('heroic'), ('legendary'), ('mythic');

-- ----------------------------
-- Table structure for medal_type
-- ----------------------------
DROP TABLE IF EXISTS "public"."medal_type";
CREATE TABLE "public"."medal_type" (
  "id" smallserial PRIMARY KEY,
  "name" text UNIQUE NOT NULL
);
INSERT INTO "medal_type" ("name")
VALUES ('killing-spree'), ('multikill'), ('mode'), ('style'), ('proficiency'), ('skill');

-- ----------------------------
-- Table structure for medal
-- ----------------------------
DROP TABLE IF EXISTS "public"."medal";
CREATE TABLE "public"."medal" (
  "id" smallserial PRIMARY KEY,
  "api_id" int8 UNIQUE NOT NULL,
  "name" text UNIQUE NOT NULL,
  "description" text NOT NULL,
  "medal_difficulty_id" int2 REFERENCES "medal_difficulty" ("id"),
  "medal_type_id" int2 REFERENCES "medal_type" ("id")
);

-- ----------------------------
-- Table structure for bot
-- ----------------------------
DROP TABLE IF EXISTS "public"."bot";
CREATE TABLE "public"."bot" (
  "id" smallserial PRIMARY KEY,
  "bid" text NOT NULL UNIQUE, -- two examples were bid(56.0) and bid(40.0), store as varchar for now
  "gamertag" text UNIQUE -- not sure where i can get this info yet
);

-- ----------------------------
-- Table structure for bot_difficulty
-- ----------------------------
DROP TABLE IF EXISTS "public"."bot_difficulty";
CREATE TABLE "public"."bot_difficulty" (
  "id" int2 PRIMARY KEY,
  "name" text NOT NULL UNIQUE
);
-- these are guesses
INSERT INTO "bot_difficulty" ("id", "name")
VALUES
  (1, 'Recruit'),
  (2, 'Marine'),
  (3, 'ODST'),
  (4, 'Spartan');

-- ----------------------------
-- Table structure for player
-- ----------------------------
DROP TABLE IF EXISTS "public"."player";
CREATE TABLE "public"."player" (
  "id" serial PRIMARY KEY,
  "xuid" text NOT NULL UNIQUE, -- remove xuid() bracketing value for storage, the examples I've seen were 16 digits
  "gamertag" text UNIQUE -- I believe max length is 12
);

-- ----------------------------
-- Table structure for team
-- ----------------------------
DROP TABLE IF EXISTS "public"."team";
CREATE TABLE "public"."team" (
  "id" int2 PRIMARY KEY, -- this lines up with the halo infinite ID
  "name" text UNIQUE NOT NULL
);
INSERT INTO "team" ("id", "name")
VALUES
  (0, 'Eagle'),
  (1, 'Cobra'),
  (2, 'Hades'),
  (3, 'Valkyrie'),
  (4, 'Rampart'),
  (5, 'Cutlass'),
  (6, 'Valor'),
  (7, 'Hazard'),
  (8, 'Observer');

-- ----------------------------
-- Table structure for tier
-- ----------------------------
-- DROP TABLE IF EXISTS "public"."tier";
-- CREATE TABLE "public"."tier" (
--   "id" smallserial PRIMARY KEY,
--   "name" text UNIQUE NOT NULL
-- );
-- INSERT INTO "tier" ("name")
-- VALUES ('Bronze'), ('Silver'), ('Gold'), ('Platinum'), ('Diamond'), ('Onyx');

-- ----------------------------
-- Table structure for outcome
-- ----------------------------
DROP TABLE IF EXISTS "public"."outcome";
CREATE TABLE "public"."outcome" (
  "id" int2 PRIMARY KEY,
  "name" text UNIQUE NOT NULL
);
INSERT INTO "outcome" ("id", "name")
VALUES
  (1, 'tied'), -- this is a guess
  (2, 'won'),
  (3, 'lost');
  
-- ----------------------------
-- Table structure for season
-- ----------------------------
DROP TABLE IF EXISTS "public"."season";
CREATE TABLE "public"."season" (
  "id" smallserial PRIMARY KEY,
  "name" text UNIQUE NOT NULL,
  "number" int2, -- not sure where to get this yet
  "version" int2
);

-- ----------------------------
-- Table structure for job_type
-- ----------------------------
DROP TABLE IF EXISTS "public"."job_type";
CREATE TABLE "public"."job_type" (
  "id" smallserial PRIMARY KEY,
  "name" text NOT NULL UNIQUE
);
INSERT INTO "job_type" ("name")
VALUES ('match'), ('stats'), ('metadata');

-- ----------------------------
-- Table structure for job
-- ----------------------------
DROP TABLE IF EXISTS "public"."job";
CREATE TABLE "public"."job" (
  "id" serial PRIMARY KEY,
  "job_type_id" int4 NULL REFERENCES "job_type" ("id"),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "is_valid" bool NOT NULL DEFAULT false,
  "duration" real
);

-- ----------------------------
-- Table structure for job_player
-- ----------------------------
DROP TABLE IF EXISTS "public"."job_player";
CREATE TABLE "public"."job_player" (
  "job_id" int4 PRIMARY KEY,
  "player_id" int4 -- job can only have one player
);

-- ----------------------------
-- Table structure for match
-- ----------------------------
DROP TABLE IF EXISTS "public"."match";
CREATE TABLE "public"."match" (
  "id" serial PRIMARY KEY,
  "guid" text UNIQUE NOT NULL,
  "playlist_version_id" int2 NULL REFERENCES "playlist_version" ("id"), -- can be null
  "map_version_id" int2 NOT NULL REFERENCES "map_version" ("id"),
  "mode_version_id" int2 NOT NULL REFERENCES "mode_version" ("id"),
  "lifecycle_mode_id" int2 NOT NULL, -- "LifecycleMode", not sure what this refers to yet
  "experience_id" int2, -- "PlaylistExperience", not sure what this refers to yet, can be null
  "season_id" int2 NULL REFERENCES "season" ("id"), -- can be null
  "started_at" timestamptz(3) NOT NULL,
  "completed_at" timestamptz(3) NOT NULL,
  "total_duration" int2 NOT NULL, -- seconds
  "playable_duration" int2 NOT NULL -- seconds
);

-- ----------------------------
-- Table structure for job_match
-- ----------------------------
DROP TABLE IF EXISTS "public"."job_match";
CREATE TABLE "public"."job_match" (
  "job_id" int4 REFERENCES "job" ("id"),
  "match_id" int4 REFERENCES "match" ("id"),
  PRIMARY KEY ("job_id", "match_id")
);

-- ----------------------------
-- Table structure for stats
-- ----------------------------
DROP TABLE IF EXISTS "public"."stats";
CREATE TABLE "public"."stats" (
  "id" serial PRIMARY KEY,
  "kills" int2 NOT NULL,
  "deaths" int2 NOT NULL,
  "assists" int2 NOT NULL,
  "betrayals" int2 NOT NULL,
  "suicides" int2 NOT NULL,
  "spawns" int2 NOT NULL,
  "max_killing_spree" int2 NOT NULL,
  "vehicles_destroyed" int2 NOT NULL,
  "vehicles_hijacked" int2 NOT NULL,
  "medals" int2 NOT NULL,
  "damage_dealt" int4 NOT NULL,
  "damage_taken" int4 NOT NULL,
  "shots_fired" int4 NOT NULL,
  "shots_landed" int4 NOT NULL,
  "rounds_won" int2 NOT NULL,
  "rounds_lost" int2 NOT NULL,
  "rounds_tied" int2 NOT NULL,
  "melee_kills" int2 NOT NULL,
  "grenade_kills" int2 NOT NULL,
  "headshot_kills" int2 NOT NULL,
  "power_weapon_kills" int2 NOT NULL,
  "assassination_kills" int2 NOT NULL,
  "vehicle_splatter_kills" int2 NOT NULL,
  "repulsor_kills" int2 NOT NULL,
  "fusion_coil_kills" int2 NOT NULL,
  "emp_assists" int2 NOT NULL,
  "driver_assists" int2 NOT NULL,
  "callout_assists" int2 NOT NULL,
  "score_personal" int4 NOT NULL,
  "score_points" int2 NOT NULL,
  "mmr" real,
  "participation_confirmed" bool,
  "joined_in_progress" bool NOT NULL,
  "joined_at" timestamptz(3) NOT NULL,
  "left_at" timestamptz(3),
  "present_at_beginning" bool NOT NULL,
  "present_at_completion" bool NOT NULL,
  "kills_expected" real NOT NULL,
  "kills_std_dev" real NOT NULL,
  "deaths_expected" real NOT NULL,
  "deaths_std_dev" real NOT NULL,
  "outcome_id" int2 NOT NULL REFERENCES "outcome" ("id"),
  "rank" int2 NOT NULL
);

-- ----------------------------
-- Table structure for match_player
-- ----------------------------
DROP TABLE IF EXISTS "public"."match_player";
CREATE TABLE "public"."match_player" (
  "match_id" int4 REFERENCES "match" ("id"),
  "player_id" int4 REFERENCES "player" ("id"),
  "team_id" int2 NOT NULL REFERENCES "team" ("id"),
  "stats_id" int4 NOT NULL REFERENCES "stats" ("id"),
  PRIMARY KEY ("match_id", "player_id")
);

-- ----------------------------
-- Table structure for match_bot
-- ----------------------------
DROP TABLE IF EXISTS "public"."match_bot";
CREATE TABLE "public"."match_bot" (
  "match_id" int4 REFERENCES "match" ("id"),
  "bot_id" int2 REFERENCES "bot" ("id"),
  "team_id" int2 NOT NULL REFERENCES "team" ("id"),
  "bot_difficulty_id" int2 NOT NULL REFERENCES "bot_difficulty" ("id"),
  "stats_id" int4 NOT NULL REFERENCES "stats" ("id"),
  PRIMARY KEY ("match_id", "bot_id")
);

-- ----------------------------
-- Table structure for match_team
-- ----------------------------
DROP TABLE IF EXISTS "public"."match_team";
CREATE TABLE "public"."match_team" (
  "match_id" int4 REFERENCES "match" ("id"),
  "team_id" int2 REFERENCES "team" ("id"),
  -- "odds_of_winning" real NOT NULL,
  "stats_id" int4 NOT NULL REFERENCES "stats" ("id"),
  PRIMARY KEY ("match_id", "team_id")
);

-- ----------------------------
-- Table structure for stats_medal
-- ----------------------------
DROP TABLE IF EXISTS "public"."stats_medal";
CREATE TABLE "public"."stats_medal" (
  "stats_id" int4 REFERENCES "stats" ("id"),
  "medal_id" int2 REFERENCES "medal" ("id"),
  "count" int2 NOT NULL,
  PRIMARY KEY ("stats_id", "medal_id")
);

-- ----------------------------
-- Table structure for stats_csr
-- ----------------------------
DROP TABLE IF EXISTS "public"."stats_csr";
CREATE TABLE "public"."stats_csr" (
  "stats_id" int4 PRIMARY KEY REFERENCES "match_stats" ("id"),
  "pre_match" int2,
  "post_match" int2
);

-- ----------------------------
-- Table structure for match_player_ctf
-- ----------------------------
-- DROP TABLE IF EXISTS "public"."match_player_ctf";
-- CREATE TABLE "public"."match_player_ctf" (
--   "match_player_id" int4 PRIMARY KEY REFERENCES "match_player" ("id"),
--   "flag_capture_assists" int2 NOT NULL,
--   "flag_captures" int2 NOT NULL,
--   "flag_carriers_killed" int2 NOT NULL,
--   "flag_grabs" int2 NOT NULL,
--   "flag_returners_killed" int2 NOT NULL,
--   "flag_returns" int2 NOT NULL,
--   "flag_secures" int2 NOT NULL,
--   "flag_steals" int2 NOT NULL,
--   "kills_as_flag_carrier" int2 NOT NULL,
--   "kills_as_flag_returner" int2 NOT NULL,
--   "time_as_flag_carrier" int2 NOT NULL --,
--   -- "job_id" int4 REFERENCES "job" ("id")
-- );

-- ----------------------------
-- Table structure for match_player_oddball
-- ----------------------------
-- DROP TABLE IF EXISTS "public"."match_player_oddball";
-- CREATE TABLE "public"."match_player_oddball" (
--   "match_player_id" int4 PRIMARY KEY REFERENCES "match_player" ("id"),
--   "kills_as_skull_carrier" int2 NOT NULL,
--   "longest_time_as_skull_carrier_seconds" int2 NOT NULL,
--   "skull_carriers_killed" int2 NOT NULL,
--   "skull_grabs" int2 NOT NULL,
--   "skull_scoring_ticks" int2 NOT NULL,
--   "time_as_skull_carrier_seconds" int2 NOT NULL --,
--   -- "job_id" int4 REFERENCES "job" ("id")
-- );

-- ----------------------------
-- Table structure for match_player_zones
-- ----------------------------
-- DROP TABLE IF EXISTS "public"."match_player_zones";
-- CREATE TABLE "public"."match_player_zones" (
--   "match_player_id" int4 PRIMARY KEY REFERENCES "match_player" ("id"),
--   "total_zone_occupation_seconds" int2 NOT NULL,
--   "zone_captures" int2 NOT NULL,
--   "zone_defensive_kills" int2 NOT NULL,
--   "zone_offensive_kills" int2 NOT NULL,
--   "zone_scoring_ticks" int2 NOT NULL,
--   "zone_secures" int2 NOT NULL --,
--   -- "job_id" int4 REFERENCES "job" ("id")
-- );

-- ----------------------------
-- Table structure for match_player_elimination
-- ----------------------------
-- DROP TABLE IF EXISTS "public"."match_player_elimination";
-- CREATE TABLE "public"."match_player_elimination" (
--   "match_player_id" int4 PRIMARY KEY REFERENCES "match_player" ("id"),
--   "allies_revived" int2 NOT NULL,
--   "elimination_assists" int2 NOT NULL,
--   "eliminations" int2 NOT NULL,
--   "enemy_revives_denied" int2 NOT NULL,
--   "executions" int2 NOT NULL,
--   "kills_as_last_player_standing" int2 NOT NULL,
--   "last_players_standing_killed" int2 NOT NULL,
--   "rounds_survived" int2 NOT NULL,
--   "times_revived_by_ally" int2 NOT NULL --,
--   -- "job_id" int4 REFERENCES "job" ("id")
-- );

-- ----------------------------
-- Table structure for match_player_stockpile
-- ----------------------------
-- DROP TABLE IF EXISTS "public"."match_player_stockpile";
-- CREATE TABLE "public"."match_player_stockpile" (
--   "match_player_id" int4 PRIMARY KEY REFERENCES "match_player" ("id"),
--   "kills_as_power_seed_carrier" int2 NOT NULL,
--   "power_seed_carriers_killed" int2 NOT NULL,
--   "power_seeds_deposited" int2 NOT NULL,
--   "power_seeds_stolen" int2 NOT NULL,
--   "time_as_power_seed_carrier_seconds" int2 NOT NULL,
--   "time_as_power_seed_driver_seconds" int2 NOT NULL --,
--   -- "job_id" int4 REFERENCES "job" ("id")
-- );

-- ----------------------------
-- Table structure for vehicle
-- ----------------------------
-- DROP TABLE IF EXISTS "public"."vehicle";
-- CREATE TABLE "public"."vehicle" (
--   "id" smallserial PRIMARY KEY,
--   "name" text
-- );
-- INSERT INTO "vehicle" ("name")
-- VALUES ('banshee'), ('wraith'), ('scorpion'), ('ghost'), ('wasp'),
--       ('gungoose'), ('brute_chopper'), ('razorback'), ('warthog'),
--       ('mongoose'), ('rocket_hog');

-- ----------------------------
-- Table structure for match_player_vehicle_destroy
-- ----------------------------
-- DROP TABLE IF EXISTS "public"."match_player_vehicle_destroy";
-- CREATE TABLE "public"."match_player_vehicle_destroy" (
--   "match_player_id" int4 REFERENCES "match_player" ("id"),
--   "vehicle_id" int2 REFERENCES "vehicle" ("id"),
--   "count" int2 NOT NULL CHECK ("count" > 0),
--   -- "job_id" int4 REFERENCES "job" ("id"),
--   PRIMARY KEY ("match_player_id", "vehicle_id")
-- );

-- ----------------------------
-- Table structure for match_player_vehicle_hijack
-- ----------------------------
-- DROP TABLE IF EXISTS "public"."match_player_vehicle_hijack";
-- CREATE TABLE "public"."match_player_vehicle_hijack" (
--   "match_player_id" int4 REFERENCES "match_player" ("id"),
--   "vehicle_id" int2 REFERENCES "vehicle" ("id"),
--   "count" int2 NOT NULL CHECK ("count" > 0),
--   -- "job_id" int4 REFERENCES "job" ("id"),
--   PRIMARY KEY ("match_player_id", "vehicle_id")
-- );