from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import os
import sqlite3
import sys
import tarfile as tar

import db_statements


class Artist(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return 'Artist (name=%s, type=%s)' % (self.name, self.type)


class Song(object):
    def __init__(self, name, raga, tala, composer):
        self.name = name
        self.raga = raga
        self.tala = tala
        self.composer = composer

    def __repr__(self):
        attrs = vars(self)
        return 'Song: (%s)' % (', '.join("%s=%s" % item for item in attrs.items()))


class Album(object):
    def __init__(self, name):
        self.name = name
        self.artists = []
        self.songs = collections.OrderedDict()
        self.venue = None
        self.date = None
        self.info = None

    def add_artist(self, artist):
        self.artists.append(artist)

    def set_venue(self, venue):
        self.venue = venue

    def set_date(self, date):
        self.date = date

    def set_info(self, info):
        self.info = info

    def add_song(self, song, index):
        self.songs[index] = song

    def __repr__(self):
        return 'Album: %s (%s)' % (self.name, self.artists[0])


def add_songs(fp, album):
    for line in fp:
        # Remove trailing newline
        if line.isspace() or line.startswith('#'):
            continue
        line = line[:-1]
        #print("Line: ", line)
        splits = line.split(' - ')

        # Remove whitespace from each element
        splits = [x.strip(' ') for x in splits]
        #print("Splitlen: ", len(splits))
        composer = None
        tala = None

        if len(splits) == 2:
            # "0 - ?"
            index, name = splits
            raga = "?"
        elif len(splits) == 3:
            # Mangalam?
            index, name, raga = splits
        elif len(splits) == 4:
            # RTP?
            index, name, raga, tala = splits
        else:
            index, name, raga, tala, composer = splits
        song = Song(name, raga, tala, composer)
        #print("adding: ", repr(song))
        album.add_song(song, index)


def add_artists(fp, album):
    for line in fp:
        if line in ['\n', '\r\n']:
            # No more artists
            break
        # Remove newline
        line = line[:-1]
        artist_name, type = line.split(' - ')
        artist = Artist(artist_name, type)
        #print("adding: ", repr(artist))
        album.add_artist(artist)


def add_venue(line, album):
    _, venue = line.split(' - ')
    venue = venue.strip()
    #print("Setting venue: ", venue)
    album.set_venue(venue)
    return

    # No venue found. Return to saved position.
    fp.seek(save_pos)


def add_date(line, album):
    _, date = line.split(' - ')
    date = date.strip()
    #print("Setting date: ", date)
    album.set_date(date)
    return


def add_info(line, album):
    info = line[len("Info -"):]
    info = info.strip()
    #print("Setting info: ", info)
    album.set_info(info)
    return


def read_index_file(album_name, fp):
    print("Processing: ", album_name)
    album = Album(album_name)
    add_artists(fp, album)

    # Read Date and Misc lines.
    while True:
        save_pos = fp.tell()
        line = fp.readline()
        # If the line starts with a digit the songs section has started.
        if not line or line[0].isdigit():
            # Rewind.
            fp.seek(save_pos)
            break
        if line in ['\n', '\r\n']:
            continue
        if line.startswith("Date"):
            add_date(line, album)
        elif line.startswith("Venue"):
            add_venue(line, album)
        elif line.startswith("Info"):
            add_info(line, album)

    add_songs(fp, album)
    return album


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    c = conn.cursor()
    c.execute(create_table_sql)


def create_tables(conn):
    create_table(conn, db_statements.CREATE_ARTISTS_TABLE)
    create_table(conn, db_statements.CREATE_COMPOSERS_TABLE)
    create_table(conn, db_statements.CREATE_RAGAS_TABLE)
    create_table(conn, db_statements.CREATE_TALAS_TABLE)
    create_table(conn, db_statements.CREATE_SONGS_TABLE)
    create_table(conn, db_statements.CREATE_ALBUMS_TABLE)
    create_table(conn, db_statements.CREATE_TRACKS_TABLE)
    create_table(conn, db_statements.CREATE_ARTIST_ALBUM_TABLE)


def insert_artist(conn, artist):
    c = conn.cursor()
    c.execute("""INSERT OR IGNORE INTO artists VALUES(NULL, ?, ?)""", (artist.name, artist.type))
    c.execute("""SELECT id FROM artists WHERE name = ? AND type = ?""", (artist.name, artist.type))
    rows = c.fetchall()
    assert len(rows), 1
    return rows[0][0]


def insert_composer(conn, composer):
    c = conn.cursor()
    #print("Composer: ", composer)
    c.execute("""INSERT OR IGNORE INTO composers VALUES(NULL, ?)""", (composer,))
    c.execute("""SELECT id FROM composers WHERE composer = ?""", (composer,))
    rows = c.fetchall()
    #print("Composer rows: ", len(rows))
    assert len(rows), 1
    return rows[0][0]


def insert_raga(conn, raga):
    c = conn.cursor()
    c.execute("""INSERT OR IGNORE INTO ragas VALUES(NULL, ?)""", (raga,))
    c.execute("""SELECT id FROM ragas WHERE raga = ?""", (raga,))
    rows = c.fetchall()
    assert len(rows), 1
    return rows[0][0]


def insert_tala(conn, tala):
    c = conn.cursor()
    c.execute("""INSERT OR IGNORE INTO talas VALUES(NULL, ?)""", (tala,))
    c.execute("""SELECT id FROM talas WHERE tala = ?""", (tala,))
    rows = c.fetchall()
    assert len(rows), 1
    return rows[0][0]


def insert_song(conn, song):
    composer_id = insert_composer(conn, song.composer) if song.composer else None
    raga_id = insert_raga(conn, song.raga)
    tala_id = insert_tala(conn, song.tala) if song.tala else None
    #print("Song name: ", song.name)
    #print("Composer_id: {0}, raga_id: {1}, tala_id: {0}".format(composer_id, raga_id, tala_id))
    c = conn.cursor()
    c.execute("""INSERT OR IGNORE INTO songs VALUES(NULL, ?, ?, ?, ?)""",
              (song.name, raga_id, tala_id, composer_id))

    statement = "SELECT id FROM songs WHERE song = ? AND raga_id = ? "
    vars = [song.name, raga_id]
    if song.composer:
        statement = statement + "AND composer_id = ? "
        vars.append(composer_id)
    if song.tala:
        statement = statement + "AND tala_id = ? "
        vars.append(tala_id)
    c.execute(statement, vars)
    rows = c.fetchall()
    #print("Rows: ", len(rows))
    assert len(rows), 1
    return rows[0][0]


def insert_track(conn, album_id, album_index, track_num, song_id):
    c = conn.cursor()
    c.execute("""INSERT OR IGNORE INTO tracks VALUES(NULL, ?, ?, ?, ?)""",
              (album_id, album_index, track_num, song_id))
    c.execute(
        """SELECT id FROM tracks WHERE album_id = ? AND album_index = ? AND track_num = ? AND song_id = ?""",
        (album_id, album_index, track_num, song_id))
    rows = c.fetchall()
    assert len(rows), 1
    return rows[0][0]


def insert_album(conn, album):
    c = conn.cursor()
    c.execute("""INSERT OR IGNORE INTO albums VALUES(NULL, ?, ?, ?, ?)""",
              (album.name, album.venue, album.date, album.info))
    c.execute(
        """SELECT id FROM albums WHERE name = ?""", (album.name,))
    rows = c.fetchall()
    assert len(rows), 1
    album_id = rows[0][0]

    # Insert into artist_album table.
    c = conn.cursor()
    for i, artist in enumerate(album.artists):
        artist_id = insert_artist(conn, artist)
        c.execute("INSERT OR IGNORE INTO artist_album VALUES(?, ?)",
                  (artist_id, album_id))

    for i, (album_index, song) in enumerate(album.songs.iteritems()):
        song_id = insert_song(conn, song)
        insert_track(conn, album_id, album_index, i, song_id)

    return album_id


def add_indexfile_tar(conn, tarfile):
    the_tarfile = tar.open(tarfile)
    album_count = 0
    for member in the_tarfile.getmembers():
        #print("File: ", member.name)
        if os.path.basename(member.name) != 'index.txt':
            print("Skipping: ", member.name)
            continue
        path_to_album = os.path.dirname(member.name)
        #print("Path: ", path_to_album)
        album_name = os.path.basename(path_to_album)
        album_artist = os.path.basename(os.path.dirname(path_to_album))

        album_plus_artist = "%s/%s" % (album_artist, album_name)
        #print("Album: ", album_plus_artist)

        fp = the_tarfile.extractfile(member)
        album = read_index_file(album_plus_artist, fp)
        insert_album(conn, album)
        album_count += 1
    print("Scanned {0} albums".format(album_count))


def main(argv):
    tarfile = argv[0]
    conn = sqlite3.connect("music.db")
    create_tables(conn)
    add_indexfile_tar(conn, tarfile)
    conn.commit()


if __name__ == "__main__":
    main(sys.argv[1:])