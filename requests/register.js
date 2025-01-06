const fs = require('fs');
const path = require('path');

// Path to the users database file
const dbPath = path.join(__dirname, 'users.db');

// Function to register a new user
function registerUser(username, password, clearance) {
    const newUser = `${username},${password},${clearance}\n`;

    // Append the new user to the database file
    fs.appendFile(dbPath, newUser, (err) => {
        if (err) {
            console.error('Error registering user:', err);
        } else {
            console.log('User registered successfully.');
        }
    });
}

// Example usage
registerUser('newUser', 'password123', 'Member');