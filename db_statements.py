
CREATE_ARTISTS_TABLE = \
"""
CREATE TABLE IF NOT EXISTS artists (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  UNIQUE(name, type)
);
"""

CREATE_ARTIST_ALBUM_TABLE = \
"""
CREATE TABLE IF NOT EXISTS artist_album (
  artist_id INTEGER,
  album_id INTEGER,
  UNIQUE(artist_id, album_id)
);
"""

CREATE_RAGAS_TABLE = \
"""
CREATE TABLE IF NOT EXISTS ragas (
  id INTEGER PRIMARY KEY,
  raga TEXT NOT NULL UNIQUE
);
"""

CREATE_TALAS_TABLE = \
"""
CREATE TABLE IF NOT EXISTS talas (
  id INTEGER PRIMARY KEY,
  tala TEXT NOT NULL UNIQUE
);
"""

CREATE_COMPOSERS_TABLE = \
"""
CREATE TABLE IF NOT EXISTS composers (
  id INTEGER PRIMARY KEY,
  composer TEXT NOT NULL UNIQUE
);
"""

CREATE_SONGS_TABLE = \
"""
CREATE TABLE IF NOT EXISTS songs (
  id INTEGER PRIMARY KEY,
  song TEXT NOT NULL,
  raga_id INTEGER NOT NULL,
  tala_id INTEGER,
  composer_id INTEGER,
  FOREIGN KEY(raga_id) REFERENCES ragas(id),
  FOREIGN KEY(tala_id) REFERENCES talas(id),
  FOREIGN KEY(composer_id) references composers(id),
  UNIQUE(song, raga_id, tala_id, composer_id)
);
"""

CREATE_ALBUMS_TABLE = \
"""
CREATE TABLE IF NOT EXISTS albums (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  venue TEXT,
  date TEXT,
  info TEXT
);
"""

CREATE_TRACKS_TABLE = \
"""
CREATE TABLE IF NOT EXISTS tracks (
  id INTEGER PRIMARY KEY,
  album_id INTEGER,
  album_index TEXT NOT NULL,
  track_num INTEGER NOT NULL,
  song_id INTEGER,
  FOREIGN KEY(album_id) REFERENCES albums(id),
  FOREIGN KEY(song_id) REFERENCES songs(id),
  UNIQUE(album_id, album_index, song_id)
);
"""