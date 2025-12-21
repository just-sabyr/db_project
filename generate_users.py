from werkzeug.security import generate_password_hash

users = [
    ('frenklin23', 'frenklin23@gmail.com', '+90682345678', '2000-05-12', 1, 62),
    ('sabyrPM', 'projectmanager@yahoo.com', '+90694567890', '1999-11-03', 3, 5),
    ('Favi', 'favi@gmail.com', '+90671234567', '2001-07-21', 2, 1),
    ('ildo', 'ildoh@hotmail.com', '+905312345678', '1998-02-18', 4, 7),
    ('amira_sound', 'amira.sound@outlook.com', '+90672220011', '2002-09-30', 6, None),
    ('noah.dev', 'noah.dev@gmail.com', '+491712345678', '1997-03-05', 1, 3),
    ('melisa2000', 'melisa2000@gmail.com', '+35688899900', '2000-12-14', 5, 4),
    ('altin_rh', 'altin.rh@yahoo.com', '+35691234888', '1995-01-09', None, None),
    ('julia_tunes', 'julia.tunes@gmail.com', '+55696666222', '2003-04-27', 2, 9),
    ('genti_official', 'genti.official@gmail.com', '+55682998877', '1996-10-10', 8, 12),
    ('mario_s', 'mario.s@gmail.com', '+393512345678', '1994-06-01', 4, None),
    ('eva_star', 'eva.star@hotmail.com', '+35692340000', '2001-08-23', 7, 13),
    ('lina_k', 'lina.k@yahoo.com', '+35675556677', '2002-03-14', 1, 5),
    ('andrea_vibe', 'andrea.vibe@gmail.com', '+35682112233', '1998-12-31', 9, 6),
    ('kevin_m', 'kevin.m@gmail.com', '+1 2025550199', '1997-04-17', 2, 10),
    ('elira_x', 'elira.x@gmail.com', '+35683330055', '2000-11-20', 3, None),
    ('ronaldo_plays', 'ronaldo.plays@gmail.com', '+35690099887', '1999-01-01', None, 4),
    ('diana_live', 'diana.live@gmail.com', '+35694443210', '2003-09-15', 6, 8),
    ('markosound', 'markosound@outlook.com', '+306944442211', '2002-02-02', 10, None),
    ('sara_b', 'sara.b@gmail.com', '+90688812121', '1998-05-05', 5, 15),
]

password_hash = generate_password_hash("123")

print("INSERT INTO Users (username, password, email, phone_number, dob, genre_id, artist_id) VALUES")
for i, u in enumerate(users):
    genre = 'NULL' if u[4] is None else u[4]
    artist = 'NULL' if u[5] is None else u[5]
    comma = ',' if i < len(users) - 1 else ';'
    print(f"('{u[0]}', '{password_hash}', '{u[1]}', '{u[2]}', '{u[3]}', {genre}, {artist}){comma}")
