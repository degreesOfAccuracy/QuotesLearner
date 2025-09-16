import sqlite3
from sys import exit
# from pprint import pprint
# print = pprint

def create_db():
    con = sqlite3.connect("quotes.db")
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE quotes (\
        id INTEGER PRIMARY KEY,\
        source TEXT,\
        note TEXT,\
        quote TEXT,\
        correct TEXT,\
        wrong TEXT\
        )"
    )
    con.commit()

def delete_db():
    con = sqlite3.connect("quotes.db")
    cur = con.cursor()
    cur.execute("DROP TABLE quotes")
    con.commit()

def reset_db():
    delete_db()
    create_db()

def update_db():
    with open("quotes.csv") as file:
        lines = file.readlines()
    con = sqlite3.connect("quotes.db")
    cur = con.cursor()
    # parse the file
    current_text = None
    file_quotes = []
    for line in lines:
        if line[0] == "#":
            current_text = line[1:].strip()
        else:
            file_quotes.append([current_text] + [x.strip() for x in line.split("|")])
    print(f"Found {len(file_quotes)} quotes in file")
    # delete quotes from the database that weren't in the file
    cur.execute("SELECT id, source, note, quote FROM quotes")
    db_quotes = cur.fetchall()
    count = 0
    for quote in db_quotes:
        if list(quote)[1:] not in file_quotes:
            count += 1
            cur.execute("DELETE FROM quotes WHERE id = ?", (quote[0],))
    print(f"Removed {count} quotes that were not in the file")
    # now insert quotes from the file that aren't in the database
    count = 0
    for quote in file_quotes:
        cur.execute("SELECT id FROM quotes WHERE source = ? and note = ? and quote = ?", quote)
        if cur.fetchone() == None:
            count += 1
            cur.execute("INSERT INTO quotes (source, note, quote, correct, wrong)\
                        VALUES (?, ?, ?, ?, ?)",\
                        (quote[0], quote[1], quote[2], 0, 0))
    print(f"Inserted {count} new quotes")
    con.commit()

def update_score(id, correct_change, wrong_change):
    con = sqlite3.connect("quotes.db")
    cur = con.cursor()
    cur.execute("UPDATE quotes SET correct = correct + ?, wrong = wrong + ? WHERE id = ?", (correct_change, wrong_change, id))
    con.commit()

def get_sources():
    con = sqlite3.connect("quotes.db")
    cur = con.cursor()
    cur.execute("SELECT DISTINCT source FROM quotes")
    return [x[0] for x in cur.fetchall()]

def get_quotes(source, mode):
    con = sqlite3.connect("quotes.db")
    cur = con.cursor()
    match mode:
        case 1: # random order
            cur.execute("SELECT id, note, quote FROM quotes WHERE source = ? ORDER BY RANDOM()", (source,))
        case 2: # ordered by the note
            cur.execute("SELECT id, note, quote FROM quotes WHERE source = ? ORDER BY note", (source,))
        case 3: # ordered by % correct
            cur.execute("SELECT id, note, quote FROM quotes WHERE source = ?\
                        ORDER BY CAST(correct AS FLOAT) / NULLIF(CAST(correct + wrong AS FLOAT), 0)", (source,))
    return cur.fetchall()

if __name__ == "__main__":
    menu = (
        ("Reset database", reset_db),
        ("Update database from quotes.csv", update_db),
        ("Exit", exit)
    )
    for i, option in enumerate(menu):
        print(f"{i+1}. {option[0]}")
    while True:
        request = int(input(">>> ")) - 1
        if input(f"Are you sure you want to '{menu[request][0]}'? (y/n)\n>>> ") == "y":
            menu[request][1]()
            print("Action completed.")
        else:
            print("Action aborted.")
