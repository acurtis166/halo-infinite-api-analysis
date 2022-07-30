/*
    Insert new matches into the database.
*/

DROP TABLE IF EXISTS tmp;

-- define temp table to match incoming data format
CREATE TEMP TABLE tmp (
    guid text,
    started_at timestamptz(3),
    completed_at timestamptz(3),
    duration real,
    map_asset_id text,
    map_version_id text,
    map_level_id text,
    game_variant_asset_id text,
    game_variant_version_id text,
    game_variant_category int,
    playlist_asset_id text,
    playlist_version_id text,
    lifecycle_mode_id int,
    experience_id int,
    season_id text,
    playable_duration real
);

-- insert the records as-is into the temp table
INSERT INTO tmp
VALUES %s;

INSERT INTO map (asset_id, level_id)
SELECT DISTINCT map_asset_id, map_level_id
FROM tmp
WHERE NOT EXISTS (SELECT 1 FROM map WHERE asset_id = map_asset_id);

INSERT INTO map_version (map_id, version_id)
SELECT DISTINCT m.id, tmp.map_version_id
FROM tmp
JOIN map m ON m.asset_id = tmp.map_asset_id
WHERE NOT EXISTS (SELECT 1 FROM map_version WHERE map_id = m.id AND version_id = tmp.map_version_id);

INSERT INTO mode (asset_id, category_id)
SELECT DISTINCT game_variant_asset_id, game_variant_category
FROM tmp
WHERE NOT EXISTS (SELECT 1 FROM mode WHERE asset_id = game_variant_asset_id);

INSERT INTO mode_version (mode_id, version_id)
SELECT DISTINCT m.id, tmp.game_variant_version_id
FROM tmp
JOIN mode m ON m.asset_id = tmp.game_variant_asset_id
WHERE NOT EXISTS (SELECT 1 FROM mode_version WHERE mode_id = m.id AND version_id = tmp.game_variant_version_id);

INSERT INTO playlist (asset_id)
SELECT DISTINCT playlist_asset_id
FROM tmp
WHERE playlist_asset_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM playlist WHERE asset_id = playlist_asset_id);

INSERT INTO playlist_version (playlist_id, version_id)
SELECT DISTINCT p.id, tmp.playlist_version_id
FROM tmp
JOIN playlist p ON p.asset_id = tmp.playlist_asset_id
WHERE NOT EXISTS (SELECT 1 FROM playlist_version WHERE playlist_id = p.id AND version_id = tmp.playlist_version_id);

INSERT INTO season (name)
SELECT DISTINCT season_id
FROM tmp
WHERE season_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM season WHERE name = season_id);

-- insert matches
INSERT INTO match (
    guid,
    mode_version_id,
    map_version_id,
    playlist_version_id,
    lifecycle_mode_id,
    experience_id,
    season_id,
    started_at,
    completed_at,
    total_duration,
    playable_duration
)
SELECT
    tmp.guid,
    modev.id,
    mv.id,
    pv.id,
    tmp.lifecycle_mode_id,
    tmp.experience_id,
    s.id,
    tmp.started_at,
    tmp.completed_at,
    tmp.duration,
    tmp.playable_duration
FROM tmp
LEFT JOIN mode ON mode.asset_id = tmp.game_variant_asset_id
LEFT JOIN mode_version modev ON modev.mode_id = mode.id AND modev.version_id = tmp.game_variant_version_id
LEFT JOIN map m ON m.asset_id = tmp.map_asset_id
LEFT JOIN map_version mv ON mv.map_id = m.id AND mv.version_id = tmp.map_version_id
LEFT JOIN playlist p ON p.asset_id = tmp.playlist_asset_id
LEFT JOIN playlist_version pv ON pv.playlist_id = p.id AND pv.version_id = tmp.playlist_version_id
LEFT JOIN season s ON s.name = tmp.season_id
WHERE NOT EXISTS (SELECT 1 FROM match WHERE guid = tmp.guid)
RETURNING id;