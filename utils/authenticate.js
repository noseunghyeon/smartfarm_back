const jwt = require("jsonwebtoken");
const secretKey = "your_secret_key";

// 사용자 인증 미들웨어
function authenticateToken(req, res, next) {
  const token = req.headers["authorization"];
  if (!token) return res.sendStatus(401);

  jwt.verify(token, secretKey, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
}

// 권한 부여 미들웨어
function authorizeRoles(...roles) {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.sendStatus(403);
    }
    next();
  };
}

module.exports = {
  authenticateToken,
  authorizeRoles,
};
