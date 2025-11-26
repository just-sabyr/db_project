-- setup.sql
CREATE DATABASE IF NOT EXISTS db_project;
USE db_project;

-- Extra tables
CREATE TABLE IF NOT EXISTS Genres (                                 -- Sabyr
    genre_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    parent_genre VARCHAR(100),
    genre_name VARCHAR(100),
    genre_description VARCHAR(255)
);


-- Main tables
CREATE TABLE IF NOT EXISTS Artists (                                -- Flavio
    artist_id INT UNSIGNED PRIMARY KEY,
    artist_name VARCHAR(255) NOT NULL,
    artist_popularity INTEGER,
    country VARCHAR(100),
    genre_id INT UNSIGNED NULL,

    UNIQUE (artist_name, country),                                  -- prevent duplicate artist names from same country
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

CREATE TABLE IF NOT EXISTS Albums (                                 -- Ildi
    album_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    album_name VARCHAR(255) NOT NULL,
    release_year INT NOT NULL,
    artist_id INT UNSIGNED NOT NULL,
    genre_id INT UNSIGNED NULL,
    cover_url VARCHAR(500),

    PRIMARY KEY (album_id),
    
    UNIQUE (artist_id, album_name, release_year),   
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id),   
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id) 
);


CREATE TABLE IF NOT EXISTS Tracks (                                 -- Sabyr
    track_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    track_name VARCHAR(100) NOT NULL,
    album_id INT UNSIGNED NOT NULL,
    artist_id INT UNSIGNED NULL,
    genre_id INT UNSIGNED NULL,
    duration INT NULL,
    explicit BOOL NULL,
    popularity INT NULL,

    FOREIGN KEY (album_id) REFERENCES Albums(album_id),
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

CREATE TABLE IF NOT EXISTS AudioFeatures (                          -- Frenklin
    feature_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    track_id INT UNSIGNED NOT NULL,
    danceability DECIMAL(3,2),
    energy       DECIMAL(3,2),
    valence      DECIMAL(3,2),
    tempo        DECIMAL(5,2),
    loudness     DECIMAL(4,1),
    acousticness DECIMAL(3,2),
    UNIQUE (track_id),
    FOREIGN KEY (track_id) REFERENCES Tracks(track_id)              -- Added foreign key constraint from tracks
);


CREATE TABLE IF NOT EXISTS Users (                                  -- Sabyr
    user_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100),                                             
    phone_number CHAR(13),                                          -- + and 12 numbers
    dob DATE,
    genre_id INT UNSIGNED NULL,
    artist_id INT UNSIGNED NULL,
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id),             -- Favourite genre
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),          -- Fav artist

    CONSTRAINT chk_users_email CHECK (email IS NULL OR email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
);


-- Genres data insertion from genres.csv
INSERT INTO Genres (genre_id, parent_genre, genre_name, genre_description) VALUES
    (1, 'Hip-Hop', 'hip-hop', 'Music with stylized rhythmic and rhyming speech (''rapping'') over a beat, originating in the US.'),
    (2, 'Jazz, Blues & Funk', 'blues', 'Genre rooted in African-American music, characterized by a specific chord progression and expressive, often sorrowful, lyrics.'),
    (3, 'Jazz, Blues & Funk', 'funk', 'Rhythmic, danceable music emphasizing bass, drums, and a strong groove, de-emphasizing melody.'),
    (4, 'Jazz, Blues & Funk', 'honky-tonk', 'Subgenre of country music focused on drinking, cheating, and heartbreak; traditionally played in bars.'),
    (5, 'Jazz, Blues & Funk', 'jazz', 'Improvised music with roots in ragtime and blues, known for its complex harmonies and rhythm.'),
    (6, 'Jazz, Blues & Funk', 'r-n-b', 'Rhythm and Blues; a genre blending pop, soul, and hip-hop, often focused on love and relationships.'),
    (7, 'Jazz, Blues & Funk', 'soul', 'Music combining gospel, R&B, and pop, known for emotional, passionate singing.'),
    (8, 'Pop', 'cantopop', 'Popular music sung in Cantonese, primarily from Hong Kong.'),
    (9, 'Pop', 'disney', 'Music from or associated with Disney films and media.'),
    (10, 'Pop', 'happy', 'Upbeat, major-key music intended to evoke positive emotions.'),
    (11, 'Pop', 'indie-pop', 'Pop music produced outside of major labels, often with a focus on melody and less polished sound.'),
    (12, 'Pop', 'j-pop', 'Japanese popular music.'),
    (13, 'Pop', 'k-pop', 'South Korean pop music, known for polished production, dance, and fashion.'),
    (14, 'Pop', 'mandopop', 'Popular music sung in Mandarin, primarily from China, Taiwan, and Singapore.'),
    (15, 'Pop', 'pop', 'The main commercial popular music genre, characterized by catchy melodies and mass appeal.'),
    (16, 'Pop', 'pop-rock', 'A fusion of pop music''s catchy structure and rock music''s instruments/production.'),
    (17, 'Pop', 'vocal', 'Music centered around the human voice, often with minimal instrumental accompaniment.'),
    (18, 'Rock & Metal', 'alternative', 'A broad subgenre of rock that emerged from the independent music underground in the 1980s.'),
    (19, 'Rock & Metal', 'classic-rock', 'A radio format focused on rock music from the late 1960s to the 1980s.'),
    (20, 'Rock & Metal', 'country-rock', 'A blend of country music and rock music, prominent in the late 1960s and 1970s.'),
    (21, 'Rock & Metal', 'emo', 'A subgenre of rock characterized by expressive, often confessional lyrics.'),
    (22, 'Rock & Metal', 'garage-rock', 'Raw and energetic form of rock and roll, prominent in the mid-1960s.'),
    (23, 'Rock & Metal', 'glam-metal', 'Subgenre of heavy metal known for flamboyant fashion and makeup.'),
    (24, 'Rock & Metal', 'goth', 'A style of rock music combining dark, atmospheric sounds with introspective and romantic lyrics.'),
    (25, 'Rock & Metal', 'grunge', 'Subgenre of alternative rock blending elements of punk rock and heavy metal.'),
    (26, 'Rock & Metal', 'hard-rock', 'A loosely defined subgenre of rock music that is more aggressive than traditional rock.'),
    (27, 'Rock & Metal', 'heavy-metal', 'Genre of rock music characterized by loud, distorted guitars, emphasis on rhythm, and powerful vocals.'),
    (28, 'Rock & Metal', 'indie-rock', 'Rock music produced independently of major commercial record labels.'),
    (29, 'Rock & Metal', 'metal', 'A broad term for heavy metal and its many subgenres.'),
    (30, 'Rock & Metal', 'nu-metal', 'A fusion genre that combines elements of heavy metal with other music styles like funk and hip hop.'),
    (31, 'Rock & Metal', 'punk', 'Fast, aggressive, often short-lived rock music with a DIY ethic.'),
    (32, 'Rock & Metal', 'rock', 'A broad genre of popular music originating in the 1950s, defined by a strong backbeat and electric instruments.'),
    (33, 'Rock & Metal', 'rock-n-roll', 'A popular music genre that originated in the United States in the 1950s, combining elements of blues and country.'),
    (34, 'Electronic & Dance', 'ambient', 'Atmospheric, instrumental music designed to induce calm and contemplation.'),
    (35, 'Electronic & Dance', 'dance', 'Music specifically produced for use in a dance club or rave, often electronic.'),
    (36, 'Electronic & Dance', 'deep-house', 'A subgenre of house music known for smooth, soulful, and atmospheric sounds.'),
    (37, 'Electronic & Dance', 'edm', 'Electronic Dance Music; a broad term for music created for club environments.'),
    (38, 'Electronic & Dance', 'electro', 'A genre of electronic music that is heavily influenced by funk and uses a heavy reliance on drum machines.'),
    (39, 'Electronic & Dance', 'electronic', 'A broad genre of music that employs electronic musical instruments and digital technology.'),
    (40, 'Electronic & Dance', 'house', 'A style of electronic dance music originating in Chicago, characterized by repetitive four-on-the-floor beats.'),
    (41, 'Electronic & Dance', 'techno', 'A genre of electronic dance music originating in Detroit, characterized by repetitive, percussive beats.'),
    (42, 'Electronic & Dance', 'trance', 'A genre of electronic music characterized by a tempo of 125 to 150 beats per minute (bpm) and a repetitive melodic phrase.'),
    (43, 'Electronic & Dance', 'trap', 'A subgenre of hip-hop and electronic music characterized by a heavy 808 sub-bass, rattling hi-hats, and synth melodies.'),
    (44, 'Electronic & Dance', 'chill', 'Relaxed, downtempo music, often instrumental, for unwinding.'),
    (45, 'Folk, Country & Indie', 'americana', 'A blend of acoustic-oriented genres like folk, country, R&B, and blues.'),
    (46, 'Folk, Country & Indie', 'bluegrass', 'A form of American roots music, characterized by string instruments and high-speed tempo.'),
    (47, 'Folk, Country & Indie', 'country', 'A genre of American music developed in the Southern United States, blending folk, gospel, and blues.'),
    (48, 'Folk, Country & Indie', 'folk', 'Traditional music of a specific culture, often acoustic and passed down orally.'),
    (49, 'Folk, Country & Indie', 'indie', 'Music produced independently of major commercial record labels, spanning various genres.'),
    (50, 'Folk, Country & Indie', 'new-age', 'Instrumental music intended to inspire creativity and relaxation.'),
    (51, 'Folk, Country & Indie', 'singer-songwriter', 'An artist who writes and performs their own musical material, often acoustic and narrative.'),
    (52, 'Classical & Instrumental', 'classical', 'Music composed in the European tradition, typically from the 18th and 19th centuries.'),
    (53, 'Classical & Instrumental', 'instrumental', 'Music performed solely by musical instruments, with no vocals.'),
    (54, 'Classical & Instrumental', 'opera', 'A form of theatre in which all or most of the characters'' roles are sung.'),
    (55, 'Classical & Instrumental', 'soundtrack', 'Music recorded to accompany and synchronize with a film, television show, or video game.'),
    (56, 'Classical & Instrumental', 'world-classical', 'Classical music traditions from non-Western cultures.'),
    (57, 'Other', 'children', 'Music created and marketed specifically for children.'),
    (58, 'Other', 'comedy', 'Music written for comedic purposes, often satirical or parody.'),
    (59, 'Other', 'holiday', 'Music associated with a holiday season, most commonly Christmas.'),
    (60, 'Other', 'other', 'Miscellaneous or hard-to-classify music genres.'),
    (61, 'Other', 'spoken-word', 'Audio content where the focus is on the human voice and speech, such as poetry or storytelling.'),
    (62, 'Other', 'workout', 'Upbeat music designed to accompany and motivate exercise.'),
    (63, 'Reggae, Caribbean & African', 'afrobeat', 'A music style combining West African musical styles with jazz and funk.'),
    (64, 'Reggae, Caribbean & African', 'dancehall', 'A genre of Jamaican popular music that originated in the late 1970s.'),
    (65, 'Reggae, Caribbean & African', 'reggae', 'A music genre that originated in Jamaica in the late 1960s, characterized by a heavy, offbeat rhythm.'),
    (66, 'Reggae, Caribbean & African', 'soca', 'A genre of Caribbean music that originated in Trinidad and Tobago, blending calypso with soul/funk.'),
    (67, 'Reggae, Caribbean & African', 'world-reggae', 'Reggae music from non-Jamaican artists or with broader international influences.'),
    (68, 'World & Regional', 'anime', 'Music associated with Japanese animation, including openings, closings, and scores.'),
    (69, 'World & Regional', 'c-pop', 'Chinese popular music, a broad term for music from mainland China, Taiwan, and Hong Kong.'),
    (70, 'World & Regional', 'cumbia', 'A folk and social dance style popular throughout Latin America.'),
    (71, 'World & Regional', 'filmi', 'Music from Indian cinema, often incorporating classical and folk styles.'),
    (72, 'World & Regional', 'german', 'Music originating from Germany, including pop, rock, and Schlager.'),
    (73, 'World & Regional', 'greek', 'Music from Greece, encompassing traditional, folk, and modern pop styles.'),
    (74, 'World & Regional', 'j-idol', 'Japanese popular music acts featuring young, charismatic singers/performers.'),
    (75, 'World & Regional', 'j-pop', 'Japanese popular music, a diverse, mainstream genre.'),
    (76, 'World & Regional', 'j-rock', 'Japanese rock music.'),
    (77, 'World & Regional', 'k-pop', 'South Korean pop music, known for polished production, dance, and fashion.'),
    (78, 'World & Regional', 'latin', 'Music originating from Latin America and the Iberian Peninsula.'),
    (79, 'World & Regional', 'latino', 'Broad term for music and musicians from a Latin American cultural background.'),
    (80, 'World & Regional', 'malay', 'Music from Malaysia, often pop or traditional styles.'),
    (81, 'World & Regional', 'mandopop', 'Popular music sung in Mandarin, primarily from China, Taiwan, and Singapore.'),
    (82, 'World & Regional', 'mpb', 'Música Popular Brasileira (Brazilian Popular Music), a post-Bossa Nova genre.'),
    (83, 'World & Regional', 'salsa', 'Cuban and Puerto Rican social dance music, fast and energetic.'),
    (84, 'World & Regional', 'samba', 'Lively Brazilian dance and music, often associated with Carnival.'),
    (85, 'World & Regional', 'sertanejo', 'Popular Brazilian country music, divided into various eras and styles.'),
    (86, 'World & Regional', 'spanish', 'Music from Spain, including flamenco and various regional folk/pop styles.'),
    (87, 'World & Regional', 'swedish', 'Music originating from Sweden, including pop, metal, and dance music.'),
    (88, 'World & Regional', 'tango', 'A dramatic, often melancholy, Argentine and Uruguayan dance music.'),
    (89, 'World & Regional', 'turkish', 'Music from Turkey, blending traditional, folk, pop, and rock elements.'),
    (90, 'World & Regional', 'world-music', 'Catch-all term for traditional or non-Western popular music.');
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    







