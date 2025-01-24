const router = require("express").Router();
const {
  postAuth,
  postLogin,
  sendEmailVerification,
  findPwd,
  resetPwd,
  updateUser,
  deleteUser,
  sendEmail,
} = require("../controllers/authController");

router.post("/register", postAuth);
router.post("/login", postLogin);
router.post("/email-verification", sendEmailVerification);
router.put("/update-user/:id", updateUser);
router.delete("/delete-user/:id", deleteUser);
router.post("/find-pwd", findPwd);
router.post("/reset-pwd", resetPwd);
router.post("/send-email", sendEmail);

module.exports = router;
