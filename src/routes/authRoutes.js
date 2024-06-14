const Hapi = require('@hapi/hapi');
const { registerHandler, loginHandler, validateTokenHandler } = require('../controllers/authController');

const authRoutes = [
  {
    method: 'POST',
    path: '/register',
    handler: registerHandler
  },
  {
    method: 'POST',
    path: '/login',
    handler: loginHandler
  },
  {
    method: 'GET',
    path: '/validate-token',
    handler: validateTokenHandler
  }
];

module.exports = authRoutes;
