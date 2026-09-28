const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { execFile } = require('child_process');
const { customAlphabet } = require('nanoid');
const db = require('./db');

// All runtime data (database, signed IPAs, certificates) lives in ONE folder that is created
// automatically. On Railway, mount a single Volume at /data and set DATA_DIR=/data.
const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, 'data');
const CERTS_DIR = path.join(DATA_DIR, 'certs'); // never served statically
const IPAS_DIR = path.join(DATA_DIR, 'ipas');
fs.mkdirSync(CERTS_DIR, { recursive: true });
fs.mkdirSync(IPAS_DIR, { recursive: true });

// Signs an unsigned .ipa in place using the stored enterprise certificate + provisioning
// profile via zsign (https://github.com/zhlynn/zsign). zsign must be installed and on PATH —
// see README for build instructions (Apple's own `codesign` is macOS-only, zsign works on Linux).
function signIpa(unsignedPath, outputPath) {
  return new Promise((resolve, reject) => {
    const cert = db.prepare('SELECT * FROM certificate WHERE id = 1').get();
    if (!cert) return reject(new Error('no_certificate_uploaded'));

    const p12Path = path.join(CERTS_DIR, cert.p12_filename);
    const provisionPath = path.join(CERTS_DIR, cert.provision_filename);

    execFile(
      'zsign',
      ['-k', p12Path, '-p', cert.p12_password, '-m', provisionPath, '-o', outputPath, unsignedPath],
      (err, stdout, stderr) => {
        if (err) return reject(new Error(stderr || err.message));
        resolve(outputPath);
      }
    );
  });
}

const app = express();
const PORT = process.env.PORT || 3000;

// Set this to your real public HTTPS domain before deploying.
// itms-services requires a real, publicly reachable HTTPS URL — it will not work on http:// or localhost.
const BASE_URL = process.env.BASE_URL || 'https://YOUR-DOMAIN.example.com';

// Simple admin auth — replace with something stronger before going live.
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || 'change-me';

const genCode = customAlphabet('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', 10); // no ambiguous chars

app.use(express.json());
// Only these two pages are public — everything else in the project folder stays private.
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'download.html')));
app.get('/download.html', (req, res) => res.sendFile(path.join(__dirname, 'download.html')));
app.get('/admin.html', (req, res) => res.sendFile(path.join(__dirname, 'admin.html')));

const upload = multer({ dest: IPAS_DIR });

function requireAdmin(req, res, next) {
  if (req.headers['x-admin-token'] !== ADMIN_TOKEN) {
    return res.status(401).json({ error: 'unauthorized' });
  }
  next();
}

// ---------- ADMIN: upload the enterprise certificate + provisioning profile (once) ----------
const certUpload = multer({ dest: CERTS_DIR });
app.post(
  '/admin/certificate',
  requireAdmin,
  certUpload.fields([{ name: 'p12' }, { name: 'provision' }]),
  (req, res) => {
    const { p12_password } = req.body;
    const p12File = req.files?.p12?.[0];
    const provisionFile = req.files?.provision?.[0];
    if (!p12File || !provisionFile || !p12_password) {
      return res.status(400).json({ error: 'p12, provision file and p12_password are required' });
    }

    const p12Final = `cert-${Date.now()}.p12`;
    const provisionFinal = `profile-${Date.now()}.mobileprovision`;
    fs.renameSync(p12File.path, path.join(CERTS_DIR, p12Final));
    fs.renameSync(provisionFile.path, path.join(CERTS_DIR, provisionFinal));

    // Single-row table: replace whatever was there before.
    db.prepare('DELETE FROM certificate WHERE id = 1').run();
    db.prepare(
      'INSERT INTO certificate (id, p12_filename, p12_password, provision_filename) VALUES (1, ?, ?, ?)'
    ).run(p12Final, p12_password, provisionFinal);

    res.json({ ok: true });
  }
);

app.get('/admin/certificate', requireAdmin, (req, res) => {
  const cert = db.prepare('SELECT uploaded_at FROM certificate WHERE id = 1').get();
  res.json({ uploaded: !!cert, uploaded_at: cert?.uploaded_at || null });
});

// ---------- ADMIN: add an app (uploads an UNSIGNED .ipa; server signs it automatically) ----------
app.post('/admin/apps', requireAdmin, upload.single('ipa'), async (req, res) => {
  const { name, bundle_id, version, icon_url } = req.body;
  if (!name || !bundle_id || !version || !req.file) {
    return res.status(400).json({ error: 'name, bundle_id, version and ipa file are required' });
  }

  const signedName = `${Date.now()}-signed.ipa`;
  const signedPath = path.join(IPAS_DIR, signedName);

  try {
    await signIpa(req.file.path, signedPath);
  } catch (e) {
    fs.unlinkSync(req.file.path);
    const msg = e.message === 'no_certificate_uploaded'
      ? 'no certificate on file — upload one at /admin/certificate first'
      : `signing failed: ${e.message}`;
    return res.status(400).json({ error: msg });
  }
  fs.unlinkSync(req.file.path); // remove the unsigned original

  const stmt = db.prepare(
    'INSERT INTO apps (name, bundle_id, version, ipa_filename, icon_url) VALUES (?, ?, ?, ?, ?)'
  );
  const info = stmt.run(name, bundle_id, version, signedName, icon_url || null);
  res.json({ id: info.lastInsertRowid, name, bundle_id, version, signed: true });
});

app.get('/admin/apps', requireAdmin, (req, res) => {
  res.json(db.prepare('SELECT * FROM apps ORDER BY id DESC').all());
});

// ---------- ADMIN: generate a code for an app ----------
app.post('/admin/codes', requireAdmin, (req, res) => {
  const { app_id } = req.body;
  const appRow = db.prepare('SELECT id FROM apps WHERE id = ?').get(app_id);
  if (!appRow) return res.status(404).json({ error: 'app not found' });

  const code = genCode();
  db.prepare('INSERT INTO codes (code, app_id, status) VALUES (?, ?, ?)').run(
    code,
    app_id,
    'unused'
  );
  res.json({ code });
});

app.get('/admin/codes', requireAdmin, (req, res) => {
  res.json(
    db
      .prepare(
        `SELECT codes.*, apps.name as app_name FROM codes
         JOIN apps ON apps.id = codes.app_id
         ORDER BY codes.id DESC`
      )
      .all()
  );
});

// ---------- CUSTOMER: verify a code, activate on first use (1 year from activation) ----------
app.post('/api/verify-code', (req, res) => {
  const { code } = req.body;
  const row = db
    .prepare(
      `SELECT codes.*, apps.name as app_name FROM codes
       JOIN apps ON apps.id = codes.app_id
       WHERE code = ?`
    )
    .get((code || '').trim().toUpperCase());

  if (!row) return res.status(404).json({ error: 'invalid_code' });
  if (row.status === 'revoked') return res.status(403).json({ error: 'revoked' });

  const now = new Date();

  if (row.status === 'unused') {
    const expires = new Date(now.getTime() + 365 * 24 * 60 * 60 * 1000);
    db.prepare(
      "UPDATE codes SET status = 'active', activated_at = ?, expires_at = ? WHERE id = ?"
    ).run(now.toISOString(), expires.toISOString(), row.id);
    row.expires_at = expires.toISOString();
  } else if (row.status === 'active') {
    if (new Date(row.expires_at) < now) {
      return res.status(403).json({ error: 'expired', expired_at: row.expires_at });
    }
  }

  res.json({
    ok: true,
    app_name: row.app_name,
    expires_at: row.expires_at,
    manifest_url: `${BASE_URL}/manifest/${row.code}.plist`,
    install_link: `itms-services://?action=download-manifest&url=${encodeURIComponent(
      `${BASE_URL}/manifest/${row.code}.plist`
    )}`,
  });
});

// ---------- Manifest + IPA serving (re-checks validity every time) ----------
app.get('/manifest/:code.plist', (req, res) => {
  const code = req.params.code.toUpperCase();
  const row = db
    .prepare(
      `SELECT codes.*, apps.* , apps.id as app_id FROM codes
       JOIN apps ON apps.id = codes.app_id
       WHERE code = ?`
    )
    .get(code);

  if (!row || row.status !== 'active') return res.status(403).send('Forbidden');
  if (new Date(row.expires_at) < new Date()) return res.status(403).send('Code expired');

  const ipaUrl = `${BASE_URL}/ipas/${row.code}/${encodeURIComponent(row.ipa_filename)}`;

  const plist = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>items</key>
  <array>
    <dict>
      <key>assets</key>
      <array>
        <dict>
          <key>kind</key>
          <string>software-package</string>
          <key>url</key>
          <string>${ipaUrl}</string>
        </dict>
      </array>
      <key>metadata</key>
      <dict>
        <key>bundle-identifier</key>
        <string>${row.bundle_id}</string>
        <key>bundle-version</key>
        <string>${row.version}</string>
        <key>kind</key>
        <string>software</string>
        <key>title</key>
        <string>${row.name}</string>
      </dict>
    </dict>
  </array>
</dict>
</plist>`;

  res.set('Content-Type', 'text/xml');
  res.send(plist);
});

// Serve the actual IPA only through a code-scoped path (re-validated)
app.get('/ipas/:code/:filename', (req, res) => {
  const code = req.params.code.toUpperCase();
  const row = db.prepare('SELECT * FROM codes WHERE code = ?').get(code);
  if (!row || row.status !== 'active' || new Date(row.expires_at) < new Date()) {
    return res.status(403).send('Forbidden');
  }
  const appRow = db.prepare('SELECT * FROM apps WHERE id = ?').get(row.app_id);
  const filePath = path.join(IPAS_DIR, appRow.ipa_filename);
  if (!fs.existsSync(filePath)) return res.status(404).send('Not found');
  res.download(filePath, appRow.ipa_filename);
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`BASE_URL is set to: ${BASE_URL} (must be a real public HTTPS domain for itms-services to work)`);
});
