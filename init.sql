CREATE TABLE Match (
    MatchId TEXT PRIMARY KEY,
    PlayedAt TEXT,
    Duration INTEGER,
    Playlist TEXT,
    GameType TEXT,
    Map TEXT
);

CREATE TABLE Team (
    MatchId TEXT,
    TeamId INTEGER,
    MMR REAL,
    [Rank] INTEGER,
    Outcome TEXT,
    Score INTEGER,
    Points INTEGER,
    KDA REAL,
    DamageDealt INTEGER,
    DamageTaken INTEGER,
    ShotsFired INTEGER,
    ShotsLanded INTEGER,
    PRIMARY KEY (MatchId, TeamId)
    FOREIGN KEY (MatchId) REFERENCES Match (MatchId)
);

CREATE TABLE Player (
    MatchId TEXT,
    TeamId INTEGER,
    Gamertag TEXT,
    PreMatchCsr INTEGER,
    Score INTEGER,
    Points INTEGER,
    KDA REAL,
    DamageDealt INTEGER,
    DamageTaken INTEGER,
    ShotsFired INTEGER,
    ShotsLanded INTEGER,
    JoinedAt TEXT,
    LeftAt TEXT,
    PRIMARY KEY (MatchId, TeamId, Gamertag),
    FOREIGN KEY (MatchId) REFERENCES Match (MatchId),
    FOREIGN KEY (TeamId) REFERENCES Team (TeamId)
);