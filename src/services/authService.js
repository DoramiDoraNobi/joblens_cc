const jwt = require('jsonwebtoken');
const { hashPassword, comparePassword } = require('../utils/hash');
const { addUser, getUserByEmail } = require('../models/userModel');

const JWT_SECRET = process.env.JWT_SECRET;

const registerUser = async (email, password, name) => {
  const hashedPassword = await hashPassword(password);
  const user = {
    id: email,  // Menggunakan email sebagai ID unik
    email,
    password: hashedPassword,
    name
  };
  await addUser(user);
  return user;
};

const loginUser = async (email, password) => {
  const user = await getUserByEmail(email);
  if (!user) {
    throw new Error('User not found');
  }
  const isPasswordValid = await comparePassword(password, user.password);
  if (!isPasswordValid) {
    throw new Error('Invalid password');
  }
  const token = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET, { expiresIn: '1h' });
  return { user, token };
};

const validateToken = async (token) => {
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    return decoded;
  } catch (err) {
    throw new Error('Invalid token');
  }
};

module.exports = {
  registerUser,
  loginUser,
  validateToken
};
