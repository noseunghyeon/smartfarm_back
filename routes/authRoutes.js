const express = require("express");
const router = express.Router();
const {
  postAuth,
  postLogin,
  sendEmailVerification,
  findPwd,
  resetPwd,
  updateUser,
  deleteUser,
  sendEmail,
  getUserInfo,
} = require("../controllers/authController");
const { authenticateToken } = require("../utils/authenticate");

router.post("/register", postAuth);
router.post("/login", postLogin);
router.post("/email-verification", sendEmailVerification);
router.put("/update-user/:id", updateUser);
router.delete("/delete-user/:id", deleteUser);
router.post("/find-pwd", findPwd);
router.post("/reset-pwd", resetPwd);
router.post("/send-email", sendEmail);
router.get("/mypage", authenticateToken, getUserInfo);

module.exports = router;
