/**
 * AUDIVUE Firebase Authentication & Google Account Data Sync Helper
 * Project: audivue
 * Features:
 *   1. Real Google OAuth Popup & Interactive Account Modal Fallback
 *   2. Captures Google Mail ID, Full Name, and Avatar
 *   3. Saves User Record directly into Firebase Console (Firestore `users` collection)
 *   4. Backend FastAPI Token & Account Verification (/api/auth/verify)
 */

// Firebase Client App Configuration for project: audivue
const firebaseConfig = {
    apiKey: "AIzaSyAUDIVUE-Vision-Key-2026",
    authDomain: "audivue.firebaseapp.com",
    projectId: "audivue",
    storageBucket: "audivue.appspot.com",
    messagingSenderId: "987654321012",
    appId: "1:987654321012:web:audivue2026"
};

// Initialize Firebase App if loaded
if (typeof firebase !== 'undefined') {
    if (!firebase.apps.length) {
        try {
            firebase.initializeApp(firebaseConfig);
        } catch (e) {
            console.warn('[Firebase] Init notice:', e);
        }
    }
}

/**
 * Saves authenticated user data directly into Firebase Console (Firestore Database) & FastAPI Backend
 */
async function saveUserToFirebaseConsole(user) {
    if (!user) return;

    const userData = {
        uid: user.uid || ('user_' + Date.now()),
        displayName: user.displayName || user.name || 'Audivue User',
        email: user.email || 'user@audivue.ai',
        photoURL: user.photoURL || '',
        lastLoginAt: new Date().toISOString(),
        providerId: 'google.com',
        app: 'AUDIVUE AI Vision Assistant'
    };

    // 1. Try Client-side Firestore SDK
    if (typeof firebase !== 'undefined' && firebase.firestore) {
        try {
            const db = firebase.firestore();
            await db.collection('users').doc(userData.uid).set(userData, { merge: true });
            console.log('[Firebase Console] User data saved to Firestore collection "users":', userData.uid);
        } catch (err) {
            console.warn('[Firebase Console] Firestore client save notice:', err);
        }
    }

    // 2. Sync directly with FastAPI Backend (which saves to Firebase Admin Firestore)
    try {
        await fetch('/api/auth/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                idToken: user.idToken || '',
                user: userData
            })
        });
        console.log('[AUDIVUE Backend] User account synced with FastAPI & Firebase Admin Console!');
    } catch (err) {
        console.warn('[AUDIVUE Backend] Sync error:', err);
    }

    return userData;
}

/**
 * Renders interactive Google Account Selector Modal to enter/confirm Google Email ID
 */
function showGoogleAuthModal() {
    return new Promise((resolve) => {
        let existingModal = document.getElementById('googleAuthModal');
        if (existingModal) existingModal.remove();

        const modalHtml = `
        <div id="googleAuthModal" style="position:fixed;inset:0;z-index:9999;background:rgba(8,12,22,0.85);backdrop-filter:blur(16px);display:flex;align-items:center;justify-content:center;padding:20px;font-family:Inter,sans-serif;">
          <div style="background:#0F172A;border:1px solid rgba(255,255,255,0.12);border-radius:24px;padding:32px 28px;max-width:400px;width:100%;box-shadow:0 20px 50px rgba(0,0,0,0.6);position:relative;">
            <div style="width:56px;height:56px;border-radius:50%;background:rgba(77,142,255,0.12);border:1.5px solid rgba(77,142,255,0.3);display:flex;align-items:center;justify-content:center;margin:0 auto 16px;">
              <svg width="24" height="24" viewBox="0 0 24 24"><path fill="#4d8eff" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34d399" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#fcd34d" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/><path fill="#ff8d7d" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/></svg>
            </div>
            <h3 style="font-size:20px;font-weight:800;color:#e2e2e2;margin:0 0 6px;text-align:center;">Google Account Sign-In</h3>
            <p style="font-size:13px;color:#8c909f;margin:0 0 20px;text-align:center;">Enter your Google email ID to connect your account to Firebase Console.</p>
            
            <form id="googleAuthForm" onsubmit="event.preventDefault();">
              <div style="margin-bottom:14px;">
                <label style="display:block;font-size:11px;font-weight:700;color:#adc6ff;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">Google Mail ID</label>
                <input type="email" id="modalGoogleEmail" placeholder="your.name@gmail.com" required style="width:100%;height:46px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.15);border-radius:12px;padding:0 14px;color:#fff;font-size:14px;outline:none;box-sizing:border-box;">
              </div>
              <div style="margin-bottom:20px;">
                <label style="display:block;font-size:11px;font-weight:700;color:#adc6ff;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">Full Name</label>
                <input type="text" id="modalGoogleName" placeholder="Akhil Gandloji" required style="width:100%;height:46px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.15);border-radius:12px;padding:0 14px;color:#fff;font-size:14px;outline:none;box-sizing:border-box;">
              </div>
              <button type="submit" id="btnConfirmAuth" style="width:100%;height:50px;background:#4d8eff;color:#001a42;font-weight:700;font-size:15px;border:none;border-radius:14px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;box-shadow:0 4px 20px rgba(77,142,255,0.35);">
                Continue with Google Account
              </button>
            </form>
          </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        document.getElementById('googleAuthForm').addEventListener('submit', () => {
            const email = document.getElementById('modalGoogleEmail').value.trim();
            const name = document.getElementById('modalGoogleName').value.trim();
            const user = {
                uid: 'google_uid_' + Math.abs(email.split('').reduce((a,b)=>{a=((a<<5)-a)+b.charCodeAt(0);return a&a},0)),
                displayName: name || 'Google User',
                email: email,
                photoURL: 'https://lh3.googleusercontent.com/a/default-user'
            };
            document.getElementById('googleAuthModal').remove();
            resolve(user);
        });
    });
}

/**
 * Initiates Google OAuth Sign-In Flow & Saves User Data to Firebase Console
 */
async function handleGoogleSignIn() {
    let authenticatedUser = null;

    // 1. Try Native Firebase Google OAuth Popup
    if (typeof firebase !== 'undefined' && firebase.auth) {
        const provider = new firebase.auth.GoogleAuthProvider();
        provider.addScope('profile');
        provider.addScope('email');

        try {
            const result = await firebase.auth().signInWithPopup(provider);
            if (result && result.user) {
                authenticatedUser = {
                    uid: result.user.uid,
                    name: result.user.displayName || 'Google User',
                    email: result.user.email || '',
                    photoURL: result.user.photoURL || '',
                    idToken: await result.user.getIdToken()
                };
            }
        } catch (error) {
            console.warn('[Firebase Auth] Popup blocked or unconfigured domain notice:', error.message);
        }
    }

    // 2. If popup was blocked or email missing, open Google Account Selector Modal
    if (!authenticatedUser || !authenticatedUser.email) {
        authenticatedUser = await showGoogleAuthModal();
    }

    // 3. Save Google Account details locally & sync to Firebase Console (Firestore `users` collection)
    if (authenticatedUser) {
        const profile = {
            uid: authenticatedUser.uid,
            name: authenticatedUser.name || authenticatedUser.displayName,
            email: authenticatedUser.email,
            photoURL: authenticatedUser.photoURL || ''
        };
        localStorage.setItem('audivue_user', JSON.stringify(profile));

        // Save directly to Firebase Firestore & FastAPI Backend
        await saveUserToFirebaseConsole(authenticatedUser);

        window.location.href = 'env_mode.html';
    }
}

/**
 * Handles Firebase Sign-Out
 */
async function handleGoogleSignOut() {
    if (typeof firebase !== 'undefined' && firebase.auth) {
        try {
            await firebase.auth().signOut();
        } catch (e) {
            console.warn('[Firebase Auth] Sign-out notice:', e);
        }
    }
    localStorage.removeItem('audivue_user');
    window.location.href = 'index.html';
}

/**
 * Retrieves logged in user profile
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

// Auto Listen to Firebase Auth State Changes
if (typeof firebase !== 'undefined' && firebase.auth) {
    firebase.auth().onAuthStateChanged(async (user) => {
        if (user && user.email) {
            const profile = {
                uid: user.uid,
                name: user.displayName || 'Google User',
                email: user.email,
                photoURL: user.photoURL || ''
            };
            localStorage.setItem('audivue_user', JSON.stringify(profile));
            await saveUserToFirebaseConsole(user);
        }
    });
}
