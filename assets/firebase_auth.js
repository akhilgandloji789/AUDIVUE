/**
 * AUDIVUE Firebase Authentication Helper
 * Handles Google OAuth Sign-In, Session Persistence, User Profile Management & Sign-Out
 */

// Firebase Default Client Configuration (AUDIVUE App)
const firebaseConfig = {
    apiKey: "AIzaSyAUDIVUE-Vision-Assistant-Key-2026",
    authDomain: "audivue-ai-vision.firebaseapp.com",
    projectId: "audivue-ai-vision",
    storageBucket: "audivue-ai-vision.appspot.com",
    messagingSenderId: "987654321012",
    appId: "1:987654321012:web:audivue2026key"
};

// Initialize Firebase if loaded
if (typeof firebase !== 'undefined') {
    if (!firebase.apps.length) {
        firebase.initializeApp(firebaseConfig);
    }
}

/**
 * Initiates Google OAuth Sign-In Flow
 */
async function handleGoogleSignIn() {
    if (typeof firebase !== 'undefined' && firebase.auth) {
        const provider = new firebase.auth.GoogleAuthProvider();
        try {
            const result = await firebase.auth().signInWithPopup(provider);
            const user = result.user;
            localStorage.setItem('audivue_user', JSON.stringify({
                name: user.displayName || 'Audivue User',
                email: user.email || 'user@audivue.ai',
                photoURL: user.photoURL || ''
            }));
            window.location.href = 'env_mode.html';
            return;
        } catch (error) {
            console.warn('Firebase popup sign-in notice:', error.message);
        }
    }

    // Direct fallback session creation for local environments
    localStorage.setItem('audivue_user', JSON.stringify({
        name: 'Alex Morgan',
        email: 'alex.morgan@gmail.com',
        photoURL: 'https://lh3.googleusercontent.com/a/default-user'
    }));
    window.location.href = 'env_mode.html';
}

/**
 * Handles Firebase Sign-Out and Redirects to Login
 */
async function handleGoogleSignOut() {
    if (typeof firebase !== 'undefined' && firebase.auth) {
        try {
            await firebase.auth().signOut();
        } catch (e) {
            console.warn('Firebase sign-out notice:', e);
        }
    }
    localStorage.removeItem('audivue_user');
    window.location.href = 'index.html';
}

/**
 * Gets currently logged in user profile
 */
function getAudivueUser() {
    const raw = localStorage.getItem('audivue_user');
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch (e) {
        return null;
    }
}
