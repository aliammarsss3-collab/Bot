const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, 'data');
fs.mkdirSync(DATA_DIR, { recursive: true });

const db = new Database(path.join(DATA_DIR, 'store.db'));

db.exec(`
CREATE TABLE IF NOT EXISTS apps (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  bundle_id TEXT NOT NULL,
  version TEXT NOT NULL,
  ipa_filename TEXT NOT NULL,
  icon_url TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS certificate (
  id INTEGER PRIMARY KEY CHECK (id = 1), -- single row: the one enterprise cert
  p12_filename TEXT NOT NULL,
  p12_password TEXT NOT NULL,
  provision_filename TEXT NOT NULL,
  uploaded_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS codes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT UNIQUE NOT NULL,
  app_id INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'unused', -- unused | active | revoked
  created_at TEXT DEFAULT (datetime('now')),
  activated_at TEXT,
  expires_at TEXT,
  FOREIGN KEY (app_id) REFERENCES apps(id)
);
`);

module.exports = db;
