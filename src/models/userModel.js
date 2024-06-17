const firestore = require('../utils/firestore');

const addUser = async (user) => {
  const userRef = firestore.collection('users').doc(user.id);
  await userRef.set(user);
};

const getUserByEmail = async (email) => {
  try {
    const usersRef = firestore.collection('users');
    const snapshot = await usersRef.where('email', '==', email).get();
    if (snapshot.empty) {
      return null;
    }
    return snapshot.docs[0].data();
  } catch (error) {
    throw new Error('Firestore error: ' + error.message);
  }
};

module.exports = {
  addUser,
  getUserByEmail
};
