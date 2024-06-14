const { registerUser, loginUser, validateToken } = require('../services/authService');

const registerHandler = async (request, h) => {
  const { email, password, name } = request.payload;
  try {
    const user = await registerUser(email, password, name);
    return h.response({ status: 'success', message: 'User registered successfully', data: user }).code(201);
  } catch (error) {
    return h.response({ status: 'error', message: error.message }).code(400);
  }
};

const loginHandler = async (request, h) => {
  const { email, password } = request.payload;
  try {
    const { user, token } = await loginUser(email, password);
    return h.response({ status: 'success', message: 'User logged in successfully', data: { user, token } }).code(200);
  } catch (error) {
    return h.response({ status: 'error', message: error.message }).code(400);
  }
};

const validateTokenHandler = async (request, h) => {
  const token = request.headers.authorization.split(' ')[1];
  try {
    const decoded = await validateToken(token);
    return h.response({ status: 'success', message: 'Token is valid', data: decoded }).code(200);
  } catch (error) {
    return h.response({ status: 'error', message: error.message }).code(401);
  }
};

module.exports = {
  registerHandler,
  loginHandler,
  validateTokenHandler
};
