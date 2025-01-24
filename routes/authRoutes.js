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
router.post("/emailVerification", sendEmailVerification);
router.put("/update_user/:id", updateUser);
router.delete("/delete_user/:id", deleteUser);
router.post("/find_pwd", findPwd);
router.post("/reset_pwd", resetPwd);
router.post("/send-email", sendEmail);

module.exports = router;
