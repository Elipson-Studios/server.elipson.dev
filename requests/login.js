const fs = require('fs');
const path = require('path');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

const usersDbPath = path.join(__dirname, '../../.db/users.db');
const secretKeyPath = path.join(__dirname, '../../.db/secret.key');

// Generate a secret key if it doesn't exist
if (!fs.existsSync(secretKeyPath)) {
    const secretKey = crypto.randomBytes(64).toString('hex');
    fs.writeFileSync(secretKeyPath, secretKey);
}

const secretKey = fs.readFileSync(secretKeyPath, 'utf8');

function login(username, password) {
    // Read the users.db file
    const usersDb = JSON.parse(fs.readFileSync(usersDbPath, 'utf8'));

    // Find the user
    const user = usersDb.find(user => user.username === username && user.password === password);

    if (user) {
        // Generate a token valid for 1 hour
        const token = jwt.sign({ username: user.username }, secretKey, { expiresIn: '1h' });
        return { success: true, token: token };
    } else {
        return { success: false, message: 'Invalid username or password' };
    }
}

module.exports = login;