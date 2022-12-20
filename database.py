import sqlite3
from helper import serialize as s

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("egg.db")

        # local copy so we don't need to send a query every time we just want to read something
        self.local = self.query_all()

    def set(self, key, value, serialize=True):
        cur = self.conn.cursor()

        if serialize:
            v = s.serialize(value)
        else:
            v = value

        self.local[key] = v
        cur.execute(f"insert into egg (key, value) values ('{key}', '{v}') on conflict(key) do update set value='{v}'",)

        self.conn.commit()

    def get(self, key, deserialize=True):
        if key not in self.local:
            raise KeyError(f"{key} not in database")

        v = self.local[key]
        if deserialize:
            return s.deserialize(v)
        return v

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __delitem__(self, key):
        cur = self.conn.cursor()

        del self.local[key]
        cur.execute(f"delete from egg where key='{key}'")

    def __iter__(self):
        return self.keys()

    def __len__(self):
        return len(self.local)

    def __contains__(self, key):
        return key in self.local

    def prefix(self, pref):
        return sorted([k for k in self.local.keys() if k.startswith(pref)])
    
    def keys(self):
        return self.prefix("")

    def query_all(self):
        cur = self.conn.cursor()
        cur.execute("select * from egg")
        return dict(cur.fetchall())

    def all(self):
        return self.local

db = Database()
